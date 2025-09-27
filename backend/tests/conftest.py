import pytest
import pytest_asyncio
import httpx
from httpx._transports.asgi import ASGITransport
from main import app
from database.session import get_session, get_test_session
from database.redis import redis_manager


@pytest.fixture(scope="session", autouse=True)
def override_get_session():
    """Override the get_session dependency for all tests."""
    # Set the override before any tests run
    app.dependency_overrides[get_session] = get_test_session
    yield
    # Clean up after all tests
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    """HTTP client fixture that uses test-specific database session."""
    await redis_manager.connect()  # Init Redis connection
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    await redis_manager.disconnect()  # Clos Redis connection


@pytest_asyncio.fixture
async def db_session():
    """Direct database session fixture for tests that need direct DB access."""
    async for session in get_test_session():
        yield session
