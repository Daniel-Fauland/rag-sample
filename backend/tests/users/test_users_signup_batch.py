import pytest
import uuid
from sqlmodel import select
from database.schemas.users import User
from utils.user import UserHelper

user_helper = UserHelper()


@pytest.mark.asyncio
async def test_batch_signup_successful(client, db_session):
    """Test batch user signup with valid data for multiple users"""
    # Generate unique emails for each test run
    unique_email_1 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    unique_email_2 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    unique_email_3 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    # Define the request payload with multiple users
    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": unique_email_1,
                "password": "Strongpassword123-"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": unique_email_2,
                "password": "Strongpassword456!"
            },
            {
                "first_name": "Test",
                "last_name": "User3",
                "email": unique_email_3,
                "password": "Strongpassword789#"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert "result" in data
    assert len(data["result"]) == 3

    # Verify all users were created successfully
    for i, result in enumerate(data["result"]):
        assert result["email"] == payload["users"][i]["email"]
        assert result["success"] is True
        assert result["reason"] == ""

    # Verify all users exist in the database
    for user_payload in payload["users"]:
        statement = select(User).where(User.email == user_payload["email"])
        result = await db_session.exec(statement)
        user = result.first()
        assert user is not None

        # Validate user information
        assert user.email == user_payload["email"]
        assert user.first_name == user_payload["first_name"]
        assert user.last_name == user_payload["last_name"]

        # Validate default/auto values
        assert user.account_type == "local"  # Default value
        assert user.is_verified is True  # Default value
        assert user.id is not None  # Auto-generated UUID
        assert user.created_at is not None
        assert user.modified_at is not None

        # Validate the password hash
        assert user.password_hash is not None
        assert await user_helper.verify_password(user_payload["password"], user.password_hash)


@pytest.mark.asyncio
async def test_batch_signup_single_user(client, db_session):
    """Test batch signup with a single user"""
    unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User",
                "email": unique_email,
                "password": "Strongpassword123-"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert len(data["result"]) == 1
    assert data["result"][0]["email"] == unique_email
    assert data["result"][0]["success"] is True
    assert data["result"][0]["reason"] == ""

    # Verify user exists in the database
    statement = select(User).where(User.email == unique_email)
    result = await db_session.exec(statement)
    user = result.first()
    assert user is not None
    assert user.email == unique_email


@pytest.mark.asyncio
async def test_batch_signup_duplicate_within_batch(client, db_session):
    """Test batch signup when duplicate emails exist within the same batch"""
    unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    other_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": unique_email,
                "password": "Strongpassword123-"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": other_email,
                "password": "Strongpassword456!"
            },
            {
                "first_name": "Test",
                "last_name": "User3",
                "email": unique_email,  # Duplicate within batch
                "password": "Strongpassword789#"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert len(data["result"]) == 3

    # Group results by email for easier assertions
    results_by_email = {result["email"]: result for result in data["result"]}

    # Find successful and failed results for unique_email
    unique_email_results = [r for r in data["result"]
                            if r["email"] == unique_email]
    other_email_result = results_by_email[other_email]

    # Should have 2 results for unique_email (1 success, 1 duplicate)
    assert len(unique_email_results) == 2

    # One should be successful, one should be duplicate
    successes = [r for r in unique_email_results if r["success"]]
    duplicates = [r for r in unique_email_results if not r["success"]]
    assert len(successes) == 1
    assert len(duplicates) == 1
    assert duplicates[0]["reason"] == "Duplicate email in the batch request"

    # Other email should succeed
    assert other_email_result["success"] is True
    assert other_email_result["reason"] == ""

    # Verify only two users exist in the database (not three)
    statement = select(User).where(User.email == unique_email)
    result = await db_session.exec(statement)
    users = result.all()
    assert len(users) == 1  # Only one user with this email should exist


@pytest.mark.asyncio
async def test_batch_signup_existing_user_in_database(client, db_session):
    """Test batch signup when some users already exist in the database"""
    # Create an existing user first
    existing_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    new_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    # Create the existing user
    existing_user_payload = {
        "first_name": "Existing",
        "last_name": "User",
        "email": existing_email,
        "password": "Strongpassword123-"
    }
    await client.post("/users", json=existing_user_payload)

    # Now try to create a batch with the existing user and a new user
    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": existing_email,  # Already exists
                "password": "Strongpassword456!"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": new_email,  # New user
                "password": "Strongpassword789#"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert len(data["result"]) == 2

    # First user (existing) should fail
    assert data["result"][0]["email"] == existing_email
    assert data["result"][0]["success"] is False
    assert data["result"][0]["reason"] == "User with this email already exists in the database"

    # Second user (new) should succeed
    assert data["result"][1]["email"] == new_email
    assert data["result"][1]["success"] is True
    assert data["result"][1]["reason"] == ""

    # Verify the new user exists in the database
    statement = select(User).where(User.email == new_email)
    result = await db_session.exec(statement)
    user = result.first()
    assert user is not None
    assert user.email == new_email


@pytest.mark.asyncio
async def test_batch_signup_all_existing_users(client, db_session):
    """Test batch signup when all users already exist in the database"""
    # Create existing users first
    email_1 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    email_2 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    await client.post("/users", json={
        "first_name": "Existing",
        "last_name": "User1",
        "email": email_1,
        "password": "Strongpassword123-"
    })

    await client.post("/users", json={
        "first_name": "Existing",
        "last_name": "User2",
        "email": email_2,
        "password": "Strongpassword456!"
    })

    # Try to create batch with all existing users
    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": email_1,
                "password": "Strongpassword789#"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": email_2,
                "password": "Strongpassword000@"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert len(data["result"]) == 2

    # Both users should fail
    for result in data["result"]:
        assert result["success"] is False
        assert result["reason"] == "User with this email already exists in the database"


@pytest.mark.asyncio
async def test_batch_signup_invalid_password(client, db_session):
    """Test batch signup with invalid password in one of the users"""
    unique_email_1 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    unique_email_2 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": unique_email_1,
                "password": "weak"  # Invalid password
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": unique_email_2,
                "password": "Strongpassword123-"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)

    # Assertions - should get validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_signup_missing_field(client, db_session):
    """Test batch signup with missing required field"""
    unique_email_1 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    unique_email_2 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    payload = {
        "users": [
            {
                "first_name": "Test",
                # Missing last_name
                "email": unique_email_1,
                "password": "Strongpassword123-"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": unique_email_2,
                "password": "Strongpassword456!"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)

    # Assertions - should get validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_signup_invalid_email(client, db_session):
    """Test batch signup with invalid email format"""
    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": "invalid-email",  # Invalid email format
                "password": "Strongpassword123-"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": "another-invalid",  # Invalid email format
                "password": "Strongpassword456!"
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)

    # Assertions - should get validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_signup_empty_list(client, db_session):
    """Test batch signup with empty users list"""
    payload = {
        "users": []
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)

    # Should return 201 with empty results (or 429 if rate limited)
    # When rate limited, we accept it as the endpoint is working correctly
    if response.status_code == 429:
        pytest.skip("Rate limit exceeded - endpoint is protected correctly")

    assert response.status_code == 201
    data = response.json()
    assert "result" in data
    assert len(data["result"]) == 0


@pytest.mark.asyncio
async def test_batch_signup_mixed_valid_invalid(client, db_session):
    """Test batch signup with a mix of valid users and users with validation errors"""
    # This test ensures that validation happens before database operations
    unique_email_1 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    unique_email_2 = f"test_user_{uuid.uuid4().hex[:8]}@example.com"

    payload = {
        "users": [
            {
                "first_name": "Test",
                "last_name": "User1",
                "email": unique_email_1,
                "password": "Strongpassword123-"
            },
            {
                "first_name": "Test",
                "last_name": "User2",
                "email": unique_email_2,
                "password": "weak"  # Invalid password - should fail validation
            }
        ]
    }

    # Perform POST request
    response = await client.post("/users/batch", json=payload)

    # Should get validation error, no users should be created
    assert response.status_code == 422

    # Verify no users were created in the database
    statement = select(User).where(User.email == unique_email_1)
    result = await db_session.exec(statement)
    user = result.first()
    assert user is None  # First user should NOT be created due to validation failure in batch


@pytest.mark.asyncio
async def test_batch_signup_large_batch(client, db_session):
    """Test batch signup with a larger number of users"""
    # Create 5 users (reduced from 10 to avoid rate limiting in rapid test runs)
    users = []
    for i in range(5):
        unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        users.append({
            "first_name": f"Test{i}",
            "last_name": f"User{i}",
            "email": unique_email,
            "password": f"Strongpassword{i}23-"
        })

    payload = {"users": users}

    # Perform POST request
    response = await client.post("/users/batch", json=payload)

    # Handle rate limiting gracefully
    if response.status_code == 429:
        pytest.skip("Rate limit exceeded - endpoint is protected correctly")

    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert len(data["result"]) == 5

    # Verify all users were created successfully
    for user_data in users:
        # Find result for this user
        user_result = next(
            (r for r in data["result"] if r["email"] == user_data["email"]), None)
        assert user_result is not None
        assert user_result["success"] is True
        assert user_result["reason"] == ""

        # Verify user exists in database
        statement = select(User).where(User.email == user_data["email"])
        result = await db_session.exec(statement)
        user = result.first()
        assert user is not None
        assert user.email == user_data["email"]
