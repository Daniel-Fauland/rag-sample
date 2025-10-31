import pytest
import uuid
from sqlmodel import select
from database.schemas.users import User
from utils.user import UserHelper

user_helper = UserHelper()


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
    response = await client.post("/users", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert data["email"] == payload["email"]
    assert data["success"]

    # Verify the user exists in the database using ORM
    statement = select(User).where(User.email == payload["email"])
    result = await db_session.exec(statement)
    user = result.first()
    assert user is not None

    # Validate user information
    assert user.email == payload["email"]
    assert user.first_name == payload["first_name"]
    assert user.last_name == payload["last_name"]

    # Validate default/auto values
    assert user.account_type == "local"  # Default value
    assert user.is_verified is True  # Default value
    assert user.id is not None  # Auto-generated UUID
    assert user.created_at is not None
    assert user.modified_at is not None

    # Validate the password hash
    assert user.password_hash is not None
    assert await user_helper.verify_password(payload["password"], user.password_hash)


@pytest.mark.asyncio
async def test_signup_user_exists(client, db_session):
    """Test user signup with existing user"""
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
    response = await client.post("/users", json=payload)

    # Assertions
    assert response.status_code == 201

    # Perform POST request
    response = await client.post("/users", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert data["message"]
    assert data["error_code"]
    assert data["solution"]
    assert data["error_code"] == "107_user_email_exists"


@pytest.mark.asyncio
async def test_signup_invalid_request(client, db_session):
    """Test user signup with existing user"""
    # Generate unique email for each test run
    unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    # Define the request payload
    # -> Invalid password
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": unique_email,
        "password": "invalidpassword"
    }

    # Define the request payload
    # -> Missing field
    payload2 = {
        "first_name": "Test",
        "email": unique_email,
        "password": "Strongpassword123-"
    }

    # Perform POST request
    response = await client.post("/users", json=payload)

    # Assertions
    assert response.status_code == 422

    # Perform POST request
    response = await client.post("/users", json=payload2)

    # Assertions
    assert response.status_code == 422
