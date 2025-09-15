import pytest
import pytest_asyncio
from httpx import AsyncClient, get
from httpx._transports.asgi import ASGITransport
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
from main import app
from database.session import get_session


@pytest_asyncio.fixture
async def session():
    """Fixture for creating a new test session."""
    session: AsyncSession = await get_session().__anext__()  # Get the session
    try:
        yield session
    finally:
        await session.close()  # Ensure the session is properly closed


@pytest.mark.asyncio
async def test_signup_successful(session):
    """Test user signup with valid data"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload = {
            "first_name": "Test",
            "last_name": "User",
            "email": "integration_testuser@example.com",
            "password": "Strongpassword123-"
        }
        # Perform POST request
        response = await client.post("/user/signup", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "uuid" in data
    assert data["role"] == "user"

    # Verify the user exists in the database
    statement = text(
        f"SELECT email FROM users WHERE email = '{payload['email']}'")
    result = await session.exec(statement)
    user = result.scalar()
    assert user is not None
    await session.close()
