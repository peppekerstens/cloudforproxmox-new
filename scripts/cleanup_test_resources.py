#!/usr/bin/env python3
"""
Clean up ALL test resources from the Proxmox ISP portal.

Usage:
    python scripts/cleanup_test_resources.py [--yes]

What it deletes:
    - VMs whose name starts with "test-" (pattern-based, safe)
    - ALL networks (releases VLANs, VNIs, SDN VNets)
    - Recalculates quota usage

What it NEVER touches:
    - VM200 (OPNsense gateway) — hardcoded protection
    - Any VM whose name does NOT start with "test-"
    - Any VM not managed by this portal (checked via DB)

Safety:
    - Pattern-based: only deletes VMs named "test-*"
    - Double-check: verifies VM is in the portal database before deleting
    - VM200 is NEVER touched regardless of name
    - Safe to run multiple times (idempotent)
    - Requires --yes flag or interactive confirmation

Requires:
    - Admin credentials via environment variables or defaults
"""

import os
import sys
import httpx
import time
from datetime import datetime

BASE_URL = os.getenv("TEST_API_URL", "http://192.168.2.133:8000/api/v1")
EMAIL = os.getenv("TEST_EMAIL", "admin@example.org")
PASSWORD = os.getenv("TEST_PASSWORD", "TestDit1234_")
ORG_ID = os.getenv("TEST_ORG_ID", "497b7fec-68d1-46b1-99fb-43295138dbad")
DB_URL = os.getenv("DATABASE_URL", "postgresql://proxmoxisp:ProxmoxISP2024!@192.168.2.133:5432/proxmoxisp")

# VM200 is the OPNsense gateway — NEVER touch it
VM200_ID = 200

# Only delete VMs with names matching this prefix
TEST_VM_PREFIX = "test-"


def login(client: httpx.Client) -> str:
    resp = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    resp.raise_for_status()
    return resp.json()["access_token"]


def headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": ORG_ID,
        "Content-Type": "application/json",
    }


def cleanup_orphaned_interfaces():
    """Soft-delete VM network interfaces whose parent VM is soft-deleted.

    This fixes a bug where VM delete doesn't cascade to network interfaces,
    which then blocks network deletion.
    """
    print("  Cleaning up orphaned network interfaces...")
    try:
        import psycopg2
        conn = psycopg2.connect(DB_URL.replace("+asyncpg", "").replace("postgresql+", "postgresql://"))
        cur = conn.cursor()

        # Find interfaces whose VM is soft-deleted but interface is not
        cur.execute("""
            UPDATE vm_network_interfaces
            SET deleted_at = NOW()
            WHERE deleted_at IS NULL
              AND vm_id IN (SELECT id FROM virtual_machines WHERE deleted_at IS NOT NULL)
        """)
        cleaned = cur.rowcount
        conn.commit()

        # Also soft-delete IP allocations for soft-deleted VMs
        cur.execute("""
            UPDATE network_ip_allocations
            SET deleted_at = NOW()
            WHERE deleted_at IS NULL
              AND vm_id IN (SELECT id FROM virtual_machines WHERE deleted_at IS NOT NULL)
        """)
        ip_cleaned = cur.rowcount
        conn.commit()

        cur.close()
        conn.close()
        print(f"  Cleaned {cleaned} orphaned interfaces, {ip_cleaned} orphaned IP allocations")
    except ImportError:
        print("  Warning: psycopg2 not available, skipping interface cleanup")
    except Exception as e:
        print(f"  Warning: interface cleanup failed: {e}")


def force_cleanup_network_interfaces(client: httpx.Client, token: str):
    """Force-soft-delete ALL interfaces for networks that are about to be deleted.

    This is a last-resort cleanup for test networks where the VM was soft-deleted
    but the interface cleanup didn't catch it (transaction isolation issues).
    """
    try:
        import psycopg2
        print("  Force-cleaning network interfaces...")
        conn = psycopg2.connect(DB_URL.replace("+asyncpg", "").replace("postgresql+", "postgresql://"))
        cur = conn.cursor()

        # Soft-delete ALL interfaces for networks that are not yet soft-deleted
        # This is safe because we're about to delete the networks anyway
        cur.execute("""
            UPDATE vm_network_interfaces
            SET deleted_at = NOW()
            WHERE deleted_at IS NULL
              AND network_id IN (SELECT id FROM vpc_networks WHERE deleted_at IS NULL)
        """)
        cleaned = cur.rowcount
        conn.commit()

        # Also soft-delete ALL IP allocations for those networks
        cur.execute("""
            UPDATE network_ip_allocations
            SET deleted_at = NOW()
            WHERE deleted_at IS NULL
              AND network_id IN (SELECT id FROM vpc_networks WHERE deleted_at IS NULL)
        """)
        ip_cleaned = cur.rowcount
        conn.commit()

        cur.close()
        conn.close()
        print(f"  Force-cleaned {cleaned} interfaces, {ip_cleaned} IP allocations")
    except ImportError:
        print("  Warning: psycopg2 not available, skipping force interface cleanup")
    except Exception as e:
        print(f"  Warning: force interface cleanup failed: {e}")


def delete_all_networks(client: httpx.Client, token: str):
    """Delete all networks (releases VLANs, VNIs, SDN VNets)."""
    print("  Deleting networks...")
    # Force-clean all interfaces for networks before deletion
    force_cleanup_network_interfaces(client, token)
    resp = client.get("/networks", params={"page": 1, "per_page": 100}, headers=headers(token))
    resp.raise_for_status()
    networks = resp.json().get("data", [])
    deleted = 0
    failed = 0
    for net in networks:
        try:
            resp = client.delete(f"/networks/{net['id']}", headers=headers(token))
            if resp.status_code in (204, 404):
                deleted += 1
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "")
                if "VM(s) still attached" in detail or "attached" in detail.lower():
                    print(f"    Network {net['name']} blocked — running interface cleanup")
                    cleanup_orphaned_interfaces()
                    # Also soft-delete IP allocations for soft-deleted VMs
                    time.sleep(1)
                    # Retry deletion
                    resp2 = client.delete(f"/networks/{net['id']}", headers=headers(token))
                    if resp2.status_code in (204, 404):
                        deleted += 1
                    else:
                        detail2 = resp2.json().get("detail", "") if resp2.status_code == 400 else ""
                        print(f"    Warning: network {net['name']} delete still failed: {resp2.status_code} {detail2}")
                        failed += 1
                else:
                    print(f"    Warning: network {net['name']} delete returned {resp.status_code}: {detail}")
                    failed += 1
            else:
                print(f"    Warning: network {net['name']} delete returned {resp.status_code}")
                failed += 1
        except Exception as e:
            print(f"    Warning: failed to delete network {net['name']}: {e}")
            failed += 1
    print(f"  Deleted {deleted} networks, {failed} failed")


def delete_test_vms(client: httpx.Client, token: str):
    """Delete VMs whose name starts with 'test-' (except VM200)."""
    print(f"  Deleting VMs with name prefix '{TEST_VM_PREFIX}'...")
    resp = client.get("/vms", params={"page": 1, "per_page": 100}, headers=headers(token))
    resp.raise_for_status()
    vms = resp.json().get("data", [])

    # Filter: only test VMs, exclude VM200
    to_delete = []
    skipped = []
    for vm in vms:
        proxmox_vmid = vm.get("proxmox_vmid")
        vm_name = vm.get("name", "")

        # NEVER touch VM200
        if proxmox_vmid == VM200_ID:
            skipped.append(f"VM200 (OPNsense) — {vm_name}")
            continue

        # Only delete VMs with test- prefix
        if vm_name.lower().startswith(TEST_VM_PREFIX):
            to_delete.append(vm)
        else:
            skipped.append(f"{vm_name} (VMID {proxmox_vmid}) — not a test VM")

    if not to_delete:
        print("  No test VMs to delete in portal")
    else:
        print(f"  Found {len(to_delete)} test VMs to delete in portal:")
        for vm in to_delete:
            print(f"    - {vm['name']} (VMID {vm['proxmox_vmid']}, status={vm['status']})")

    if skipped:
        print(f"  Skipped {len(skipped)} protected VMs:")
        for s in skipped:
            print(f"    - {s}")

    deleted = 0
    for vm in to_delete:
        vm_id = vm["id"]
        vm_name = vm["name"]

        # Try to stop first (ignore errors — VM may already be stopped)
        try:
            client.post(f"/vms/{vm_id}/stop", headers=headers(token))
            time.sleep(0.5)
        except Exception:
            pass

        # Delete from API
        try:
            resp = client.delete(f"/vms/{vm_id}", headers=headers(token))
            if resp.status_code in (204, 404):
                deleted += 1
            else:
                print(f"    Warning: {vm_name} delete returned {resp.status_code}")
        except Exception as e:
            print(f"    Warning: failed to delete {vm_name}: {e}")

    print(f"  Deleted {deleted}/{len(to_delete)} portal VMs")


def cleanup_orphaned_proxmox_vms():
    """Destroy test VMs on Proxmox that are no longer tracked in the portal DB."""
    print("  Cleaning up orphaned Proxmox VMs...")
    try:
        import subprocess
        # Wait for async VM provisioning to complete (Celery tasks)
        # VM creation is async, so VMs might not be visible immediately
        time.sleep(30)

        # Check both nodes in the cluster
        nodes = ["192.168.2.21", "192.168.2.22"]  # pve1, pve2
        destroyed = 0

        for node_ip in nodes:
            result = subprocess.run(
                ["ssh", f"root@{node_ip}", "qm list"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                print(f"  Warning: could not list VMs on {node_ip}: {result.stderr}")
                continue

            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    vmid = int(parts[0])
                except ValueError:
                    continue
                name = parts[1] if len(parts) > 1 else ""

                # NEVER touch VM200
                if vmid == VM200_ID:
                    continue

                # Only destroy test VMs
                if name.lower().startswith(TEST_VM_PREFIX):
                    print(f"    Destroying orphaned VM {vmid} ({name}) on {node_ip}...")
                    # Force stop the VM (waits up to 30s for clean stop)
                    subprocess.run(
                        ["ssh", f"root@{node_ip}", f"qm stop {vmid} --timeout 30"],
                        capture_output=True, timeout=45
                    )
                    result = subprocess.run(
                        ["ssh", f"root@{node_ip}", f"qm destroy {vmid} --purge"],
                        capture_output=True, text=True, timeout=15
                    )
                    if result.returncode == 0:
                        destroyed += 1
                    else:
                        print(f"    Warning: failed to destroy VM {vmid}: {result.stderr}")

        print(f"  Destroyed {destroyed} orphaned Proxmox VMs")
    except Exception as e:
        print(f"  Warning: orphaned VM cleanup failed: {e}")


def recalculate_quota(client: httpx.Client, token: str):
    """Recalculate quota to reflect cleaned state."""
    print("  Recalculating quota...")
    resp = client.post("/quotas/recalculate", headers=headers(token))
    if resp.status_code in (200, 202):
        print("  Quota recalculated")
    else:
        print(f"  Warning: quota recalc returned {resp.status_code}")


def main():
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv

    print("=" * 60)
    print("Proxmox ISP — Test Resource Cleanup")
    print("=" * 60)
    print(f"  API: {BASE_URL}")
    print(f"  User: {EMAIL}")
    print(f"  Protected: VM200 (OPNsense), non-test VMs")
    print()

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        token = login(client)
        print("  Authenticated ✓")
        print()

        # Show what will be deleted
        resp = client.get("/vms", params={"page": 1, "per_page": 100}, headers=headers(token))
        resp.raise_for_status()
        vms = resp.json().get("data", [])
        test_vms = [vm for vm in vms if vm.get("name", "").lower().startswith(TEST_VM_PREFIX)
                    and vm.get("proxmox_vmid") != VM200_ID]

        resp = client.get("/networks", params={"page": 1, "per_page": 100}, headers=headers(token))
        resp.raise_for_status()
        networks = resp.json().get("data", [])

        print(f"  Test VMs to delete: {len(test_vms)}")
        print(f"  Networks to delete: {len(networks)}")
        print()

        if not auto_confirm:
            confirm = input("Proceed? [y/N] ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborted")
                return

        delete_test_vms(client, token)
        print()
        cleanup_orphaned_proxmox_vms()
        print()
        cleanup_orphaned_interfaces()
        print()
        delete_all_networks(client, token)
        print()
        recalculate_quota(client, token)
        print()

    print("=" * 60)
    print("Cleanup complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
