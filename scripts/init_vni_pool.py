#!/usr/bin/env python3
"""
Initialize VXLAN VNI pool with VNIs 100000-16777215.

Run once after the first deployment to populate the pool.
Safe to run multiple times — skips existing VNIs.

Usage:
    python scripts/init_vni_pool.py

Requires DATABASE_URL environment variable or .env file in project root.
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.vni_service import VNIService


async def main():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://proxmoxisp:ProxmoxISP2024!@localhost:5432/proxmoxisp",
    )

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        service = VNIService(session)
        count = await service.initialize_vni_pool()
        print(f"Created {count} VNI entries in pool")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
