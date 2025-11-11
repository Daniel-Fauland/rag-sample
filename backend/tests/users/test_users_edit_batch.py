import pytest
import uuid
from sqlmodel import select
from database.schemas.users import User
from tests.test_helper import TestHelper

test_helper = TestHelper()


@pytest.mark.asyncio
async def test_batch_edit_successful_by_email(client, db_session):
    """Test batch edit updating multiple users by their email addresses"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)
    user3 = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload
    payload = {
        "users": [
            {
                "identifier": user1.email,
                "updates": {
                    "first_name": "UpdatedFirstName1",
                    "last_name": "UpdatedLastName1"
                }
            },
            {
                "identifier": user2.email,
                "updates": {
                    "first_name": "UpdatedFirstName2"
                }
            },
            {
                "identifier": user3.email,
                "updates": {
                    "last_name": "UpdatedLastName3"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "result" in data
    assert len(data["result"]) == 3

    # Verify all updates were successful
    for result in data["result"]:
        assert result["success"] is True
        assert result["reason"] == ""

    # Verify changes in database - refresh session to see changes
    await db_session.commit()
    original_user2_last = user2.last_name
    original_user3_first = user3.first_name
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    await db_session.refresh(user3)

    assert user1.first_name == "UpdatedFirstName1"
    assert user1.last_name == "UpdatedLastName1"
    assert user2.first_name == "UpdatedFirstName2"
    assert user2.last_name == original_user2_last  # Unchanged
    assert user3.first_name == original_user3_first  # Unchanged
    assert user3.last_name == "UpdatedLastName3"


@pytest.mark.asyncio
async def test_batch_edit_successful_by_uuid(client, db_session):
    """Test batch edit updating multiple users by their UUIDs"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload using UUIDs
    payload = {
        "users": [
            {
                "identifier": str(user1.id),
                "updates": {
                    "first_name": "UUIDUpdated1"
                }
            },
            {
                "identifier": str(user2.id),
                "updates": {
                    "last_name": "UUIDUpdated2"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 2

    # Verify all updates were successful
    for result in data["result"]:
        assert result["success"] is True

    # Verify changes in database - refresh session to see changes
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    assert user1.first_name == "UUIDUpdated1"
    assert user2.last_name == "UUIDUpdated2"


@pytest.mark.asyncio
async def test_batch_edit_mixed_email_and_uuid(client, db_session):
    """Test batch edit with a mix of email and UUID identifiers"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload with mixed identifiers
    payload = {
        "users": [
            {
                "identifier": user1.email,  # Email
                "updates": {
                    "first_name": "MixedEmail"
                }
            },
            {
                "identifier": str(user2.id),  # UUID
                "updates": {
                    "last_name": "MixedUUID"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 2

    # Verify all updates were successful
    for result in data["result"]:
        assert result["success"] is True

    # Verify changes in database - refresh session to see changes
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    assert user1.first_name == "MixedEmail"
    assert user2.last_name == "MixedUUID"


@pytest.mark.asyncio
async def test_batch_edit_single_user(client, db_session):
    """Test batch edit with a single user"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload with one user
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {
                    "first_name": "SingleUpdate",
                    "last_name": "BatchEdit"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 1
    assert data["result"][0]["success"] is True
    assert data["result"][0]["identifier"] == user.email

    # Verify changes in database - refresh session to see changes
    await db_session.commit()
    await db_session.refresh(user)
    assert user.first_name == "SingleUpdate"
    assert user.last_name == "BatchEdit"


@pytest.mark.asyncio
async def test_batch_edit_user_not_found(client, db_session):
    """Test batch edit with non-existent user"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Use non-existent email and UUID
    fake_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
    fake_uuid = str(uuid.uuid4())

    # Define the batch update payload
    payload = {
        "users": [
            {
                "identifier": fake_email,
                "updates": {
                    "first_name": "ShouldFail"
                }
            },
            {
                "identifier": fake_uuid,
                "updates": {
                    "last_name": "ShouldFail"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 2

    # Verify both updates failed with "User not found"
    for result in data["result"]:
        assert result["success"] is False
        assert result["reason"] == "User not found"


@pytest.mark.asyncio
async def test_batch_edit_mixed_existing_and_non_existing(client, db_session):
    """Test batch edit with a mix of existing and non-existent users"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create one real user
    existing_user = await test_helper.create_user_if_not_exists(client, db_session)
    fake_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"

    # Define the batch update payload
    payload = {
        "users": [
            {
                "identifier": existing_user.email,
                "updates": {
                    "first_name": "RealUpdate"
                }
            },
            {
                "identifier": fake_email,
                "updates": {
                    "first_name": "FakeUpdate"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 2

    # Find results by identifier
    existing_result = next(
        r for r in data["result"] if r["identifier"] == existing_user.email)
    fake_result = next(
        r for r in data["result"] if r["identifier"] == fake_email)

    # Verify existing user was updated successfully
    assert existing_result["success"] is True
    assert existing_result["reason"] == ""

    # Verify non-existent user update failed
    assert fake_result["success"] is False
    assert fake_result["reason"] == "User not found"

    # Verify changes in database for existing user - refresh session to see changes
    await db_session.commit()
    await db_session.refresh(existing_user)
    assert existing_user.first_name == "RealUpdate"


@pytest.mark.asyncio
async def test_batch_edit_no_fields_provided(client, db_session):
    """Test batch edit when no update fields are provided"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload with empty updates
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {}
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 1
    assert data["result"][0]["success"] is False
    assert data["result"][0]["reason"] == "No fields provided for update"


@pytest.mark.asyncio
async def test_batch_edit_invalid_uuid_format(client, db_session):
    """Test batch edit with invalid UUID format"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Define the batch update payload with invalid UUID
    payload = {
        "users": [
            {
                "identifier": "invalid-uuid-format",
                "updates": {
                    "first_name": "ShouldFail"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 1
    assert data["result"][0]["success"] is False
    assert data["result"][0]["reason"] == "Invalid UUID format"


@pytest.mark.asyncio
async def test_batch_edit_empty_list(client, db_session):
    """Test batch edit with empty users list"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Define the batch update payload with empty list
    payload = {
        "users": []
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions - should return 200 with empty results
    assert response.status_code == 200
    assert "result" in data
    assert len(data["result"]) == 0


@pytest.mark.asyncio
async def test_batch_edit_update_email(client, db_session):
    """Test batch edit updating user email addresses"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)
    new_email = f"updated_{uuid.uuid4().hex[:8]}@example.com"

    # Define the batch update payload
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {
                    "email": new_email
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 1
    assert data["result"][0]["success"] is True

    # Verify email was updated in database
    statement = select(User).where(User.email == new_email)
    result = await db_session.exec(statement)
    updated_user = result.first()
    assert updated_user is not None
    assert updated_user.id == user.id


@pytest.mark.asyncio
async def test_batch_edit_large_batch(client, db_session):
    """Test batch edit with multiple users"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create 5 test users
    users = []
    for i in range(5):
        user = await test_helper.create_user_if_not_exists(client, db_session)
        users.append(user)

    # Define the batch update payload
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {
                    "first_name": f"BatchUpdated{i}"
                }
            }
            for i, user in enumerate(users)
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 5

    # Verify all updates were successful
    for result in data["result"]:
        assert result["success"] is True

    # Verify changes in database - refresh session to see changes
    await db_session.commit()
    for i, user in enumerate(users):
        await db_session.refresh(user)
        assert user.first_name == f"BatchUpdated{i}"


@pytest.mark.asyncio
async def test_batch_edit_invalid_email_format(client, db_session):
    """Test batch edit with invalid email format in updates"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload with invalid email
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {
                    "email": "invalid-email-format"  # No @ or .
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)

    # Assertions - should get validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_edit_empty_name_fields(client, db_session):
    """Test batch edit with empty name fields"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the batch update payload with empty first_name
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {
                    "first_name": "   "  # Empty string (whitespace)
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)

    # Assertions - should get validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_edit_insufficient_permissions(client, db_session):
    """Test batch edit fails when user doesn't have update:user:all permission"""
    # Login as regular user (doesn't have update:user:all permission)
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", unique=True)

    # Create a test user to attempt to update
    user_to_update = await test_helper.create_user_if_not_exists(client, db_session)

    payload = {
        "users": [
            {
                "identifier": user_to_update.email,
                "updates": {
                    "first_name": "ShouldFail"
                }
            }
        ]
    }

    # Perform request with regular user authorization (insufficient permissions)
    headers = {"Authorization": f"Bearer {user_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    response_data = response.json()

    # Assertions - should get forbidden error
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"

    # Verify user was NOT updated in the database
    statement = select(User).where(User.email == user_to_update.email)
    result = await db_session.exec(statement)
    user = result.first()
    assert user.first_name == user_to_update.first_name  # Unchanged


@pytest.mark.asyncio
async def test_batch_edit_no_authentication(client, db_session):
    """Test batch edit fails when no authentication token is provided"""
    # Create a test user
    user_to_update = await test_helper.create_user_if_not_exists(client, db_session)

    payload = {
        "users": [
            {
                "identifier": user_to_update.email,
                "updates": {
                    "first_name": "ShouldFail"
                }
            }
        ]
    }

    # Perform request without authorization header
    response = await client.post("/users/batch-edit", json=payload)

    # Assertions - should get forbidden error (403 when no token provided)
    assert response.status_code == 403

    # Verify user was NOT updated in the database
    statement = select(User).where(User.email == user_to_update.email)
    result = await db_session.exec(statement)
    user = result.first()
    assert user.first_name == user_to_update.first_name  # Unchanged


@pytest.mark.asyncio
async def test_batch_edit_partial_updates_different_fields(client, db_session):
    """Test batch edit where each user has different fields updated"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)
    user3 = await test_helper.create_user_if_not_exists(client, db_session)

    # Store original values
    original_user1_last = user1.last_name
    original_user2_first = user2.first_name
    original_user3_email = user3.email

    # Define the batch update payload with different fields for each user
    payload = {
        "users": [
            {
                "identifier": user1.email,
                "updates": {
                    "first_name": "OnlyFirstName"
                    # last_name not updated
                }
            },
            {
                "identifier": user2.email,
                "updates": {
                    "last_name": "OnlyLastName"
                    # first_name not updated
                }
            },
            {
                "identifier": user3.email,
                "updates": {
                    "first_name": "BothFields",
                    "last_name": "Updated"
                    # email not updated
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert len(data["result"]) == 3

    # Verify all updates were successful
    for result in data["result"]:
        assert result["success"] is True

    # Verify partial updates in database - refresh session to see changes
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    await db_session.refresh(user3)
    assert user1.first_name == "OnlyFirstName"
    assert user1.last_name == original_user1_last  # Unchanged
    assert user2.first_name == original_user2_first  # Unchanged
    assert user2.last_name == "OnlyLastName"
    assert user3.first_name == "BothFields"
    assert user3.last_name == "Updated"
    assert user3.email == original_user3_email  # Unchanged


@pytest.mark.asyncio
async def test_batch_edit_modified_at_timestamp_updated(client, db_session):
    """Test that batch edit updates the modified_at timestamp"""
    # Login as admin user (has update:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)
    original_modified_at = user.modified_at

    # Define the batch update payload
    payload = {
        "users": [
            {
                "identifier": user.email,
                "updates": {
                    "first_name": "TimestampTest"
                }
            }
        ]
    }

    # Perform POST request with admin authorization
    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-edit", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 200

    # Verify modified_at was updated - refresh session to see changes
    await db_session.commit()
    await db_session.refresh(user)
    assert user.modified_at > original_modified_at
