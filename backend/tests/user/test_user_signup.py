import pytest
import uuid
from sqlalchemy.sql import text


@pytest.mark.asyncio
async def test_signup_successful(client, db_session):
    """Test user signup with valid data"""
    # Generate unique email for each test run
    unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    # Define the request payload
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": unique_email,
        "password": "Strongpassword123-"
    }

    # Perform POST request
    response = await client.post("/user/signup", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["success"]

    # Verify the user exists in the database
    statement = text(
        f"SELECT email FROM users WHERE email = '{payload['email']}'")
    result = await db_session.exec(statement)
    user = result.scalar()
    assert user is not None
