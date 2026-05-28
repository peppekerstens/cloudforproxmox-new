"""Shared test fixtures for unit and integration tests."""
import os
import pytest
import pytest_asyncio

# Set required env vars BEFORE importing app modules (Settings loads on import)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars!"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models directly — do NOT import app.db.session or app.main
# Those trigger engine creation and Settings validation on import.
from app.models.base import Base
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.resource_quota import ResourceQuota
from app.models.vlan_pool import VLANPool
from app.models.vxlan_vni_pool import VXLANVNIPool

# --------------------------------------------------------------------------- #
#  Unit test fixtures (in-memory SQLite)
# --------------------------------------------------------------------------- #

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """Create an isolated in-memory database session for unit tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user in the in-memory database."""
    user = User(
        email="test@example.org",
        username="testuser",
        first_name="Test",
        last_name="User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_organization(db_session):
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        slug="test-org",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest_asyncio.fixture
async def test_org_member(db_session, test_user, test_organization):
    """Create an organization membership linking user to org."""
    member = OrganizationMember(
        organization_id=test_organization.id,
        user_id=test_user.id,
        role="owner",
    )
    db_session.add(member)
    await db_session.flush()
    return member


# --------------------------------------------------------------------------- #
#  Integration test fixtures (real LXC deployment)
# --------------------------------------------------------------------------- #

INTEGRATION_BASE_URL = os.getenv(
    "TEST_API_URL", "http://192.168.2.133:8000/api/v1"
)
INTEGRATION_EMAIL = os.getenv("TEST_EMAIL", "admin@example.org")
INTEGRATION_PASSWORD = os.getenv("TEST_PASSWORD", "TestDit1234_")


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests against real deployment",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(
            reason="need --integration option to run"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


@pytest.fixture
def integration_client():
    """Return a synchronous httpx client configured for integration tests."""
    import httpx
    return httpx.Client(
        base_url=INTEGRATION_BASE_URL,
        timeout=30.0,
    )


@pytest.fixture(autouse=True, scope="session")
def integration_cleanup():
    """Run cleanup before AND after integration test session."""
    import subprocess
    script_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "scripts", "cleanup_test_resources.py"
    )

    def _run_cleanup():
        if os.path.exists(script_path):
            print(f"[CLEANUP] Running script: {script_path}")
            # Override DATABASE_URL to use real PostgreSQL, not the in-memory SQLite
            # that unit tests use
            env = os.environ.copy()
            env["DATABASE_URL"] = "postgresql://proxmoxisp:ProxmoxISP2024!@192.168.2.133:5432/proxmoxisp"
            try:
                result = subprocess.run(
                    ["python3", script_path, "--yes"],
                    capture_output=True, text=True, timeout=180,
                    env=env
                )
                print(f"[CLEANUP] returncode={result.returncode}")
                if result.stdout:
                    for line in result.stdout.strip().split("\n"):
                        if any(kw in line for kw in ["Deleting", "Deleted", "Destroyed", "Cleaned", "Quota", "complete", "Warning", "Force"]):
                            print(f"[CLEANUP] {line.strip()}")
                if result.stderr:
                    print(f"[CLEANUP] stderr: {result.stderr[:500]}")
            except subprocess.TimeoutExpired:
                print("[CLEANUP] ERROR: cleanup timed out after 180s")
            except Exception as e:
                print(f"[CLEANUP] ERROR: {e}")
        else:
            print(f"[CLEANUP] Script not found: {script_path}")

    print("\n[CLEANUP] Pre-test cleanup...")
    _run_cleanup()
    yield
    print("\n[CLEANUP] Post-test cleanup...")
    _run_cleanup()


@pytest.fixture
def integration_token(integration_client):
    """Authenticate and return a bearer token for integration tests."""
    resp = integration_client.post(
        "/auth/login",
        json={"email": INTEGRATION_EMAIL, "password": INTEGRATION_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def integration_org_id(integration_client, integration_token):
    """Get the default organization ID from the database."""
    return "497b7fec-68d1-46b1-99fb-43295138dbad"


@pytest.fixture
def auth_headers(integration_token, integration_org_id):
    """Return headers with auth token and org ID."""
    return {
        "Authorization": f"Bearer {integration_token}",
        "X-Organization-ID": integration_org_id,
        "Content-Type": "application/json",
    }
