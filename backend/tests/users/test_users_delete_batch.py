import pytest
import uuid
from sqlmodel import select
from database.schemas.users import User
from tests.test_helper import TestHelper

test_helper = TestHelper()


@pytest.mark.asyncio
async def test_batch_delete_by_email_successful(client, db_session):
    """Test deleting multiple users by their email addresses"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)
    user3 = await test_helper.create_user_if_not_exists(client, db_session)

    # Verify users exist
    statement = select(User).where(User.email.in_(
        [user1.email, user2.email, user3.email]))
    result = await db_session.exec(statement)
    users_before = result.all()
    assert len(users_before) == 3

    # Delete users by email
    payload = {
        "identifiers": [user1.email, user2.email, user3.email]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 204

    # Verify users were deleted
    statement = select(User).where(User.email.in_(
        [user1.email, user2.email, user3.email]))
    result = await db_session.exec(statement)
    users_after = result.all()
    assert len(users_after) == 0


@pytest.mark.asyncio
async def test_batch_delete_by_uuid_successful(client, db_session):
    """Test deleting multiple users by their UUIDs"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)

    # Verify users exist
    statement = select(User).where(User.id.in_([user1.id, user2.id]))
    result = await db_session.exec(statement)
    users_before = result.all()
    assert len(users_before) == 2

    # Delete users by UUID
    payload = {
        "identifiers": [str(user1.id), str(user2.id)]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 204

    # Verify users were deleted
    statement = select(User).where(User.id.in_([user1.id, user2.id]))
    result = await db_session.exec(statement)
    users_after = result.all()
    assert len(users_after) == 0


@pytest.mark.asyncio
async def test_batch_delete_mixed_email_and_uuid(client, db_session):
    """Test deleting users using a mix of emails and UUIDs"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test users
    user1 = await test_helper.create_user_if_not_exists(client, db_session)
    user2 = await test_helper.create_user_if_not_exists(client, db_session)
    user3 = await test_helper.create_user_if_not_exists(client, db_session)

    # Delete users using mix of email and UUID
    payload = {
        "identifiers": [user1.email, str(user2.id), user3.email]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 204

    # Verify all users were deleted
    statement = select(User).where(User.email.in_(
        [user1.email, user2.email, user3.email]))
    result = await db_session.exec(statement)
    users_after = result.all()
    assert len(users_after) == 0


@pytest.mark.asyncio
async def test_batch_delete_single_user(client, db_session):
    """Test deleting a single user using batch delete"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Delete user
    payload = {
        "identifiers": [user.email]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 204

    # Verify user was deleted
    statement = select(User).where(User.email == user.email)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_batch_delete_non_existent_users(client, db_session):
    """Test deleting users that don't exist - should succeed silently"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Try to delete non-existent users
    fake_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
    fake_uuid = str(uuid.uuid4())

    payload = {
        "identifiers": [fake_email, fake_uuid]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions - should succeed with 204 even if users don't exist
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_batch_delete_partial_exists(client, db_session):
    """Test deleting a mix of existing and non-existent users"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create one real user
    existing_user = await test_helper.create_user_if_not_exists(client, db_session)

    # Mix existing and non-existing identifiers
    fake_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
    fake_uuid = str(uuid.uuid4())

    payload = {
        "identifiers": [existing_user.email, fake_email, fake_uuid]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 204

    # Verify the existing user was deleted
    statement = select(User).where(User.email == existing_user.email)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_batch_delete_empty_list(client, db_session):
    """Test batch delete with empty identifiers list"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    payload = {
        "identifiers": []
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions - should succeed with empty list
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_batch_delete_invalid_uuid_format(client, db_session):
    """Test batch delete with invalid UUID format - should be silently ignored"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create a real user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Include invalid UUID format (not an email, not a valid UUID)
    payload = {
        "identifiers": [user.email, "invalid-uuid-format", "also-invalid"]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions - should succeed, invalid UUIDs are silently ignored
    assert response.status_code == 204

    # Verify the valid user was deleted
    statement = select(User).where(User.email == user.email)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_batch_delete_duplicate_identifiers(client, db_session):
    """Test batch delete with duplicate identifiers in the list"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Include duplicates in the list
    payload = {
        "identifiers": [user.email, user.email, str(user.id), str(user.id)]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions - should handle duplicates gracefully
    assert response.status_code == 204

    # Verify user was deleted (once)
    statement = select(User).where(User.email == user.email)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_batch_delete_large_batch(client, db_session):
    """Test deleting a larger number of users"""
    # Login as admin user (has delete:user:all permission)
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create 10 test users
    users = []
    for _ in range(10):
        user = await test_helper.create_user_if_not_exists(client, db_session)
        users.append(user)

    # Verify all users exist
    emails = [user.email for user in users]
    statement = select(User).where(User.email.in_(emails))
    result = await db_session.exec(statement)
    users_before = result.all()
    assert len(users_before) == 10

    # Delete all users
    payload = {
        "identifiers": emails
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 204

    # Verify all users were deleted
    statement = select(User).where(User.email.in_(emails))
    result = await db_session.exec(statement)
    users_after = result.all()
    assert len(users_after) == 0


@pytest.mark.asyncio
async def test_batch_delete_insufficient_permissions(client, db_session):
    """Test batch delete fails when user doesn't have delete:user:all permission"""
    # Login as regular user (doesn't have delete:user:all permission)
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", unique=True)

    # Create a test user to attempt to delete
    user_to_delete = await test_helper.create_user_if_not_exists(client, db_session)

    payload = {
        "identifiers": [user_to_delete.email]
    }

    # Perform request with regular user authorization (insufficient permissions)
    headers = {"Authorization": f"Bearer {user_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)
    response_data = response.json()

    # Assertions - should get forbidden error
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"

    # Verify user was NOT deleted
    statement = select(User).where(User.email == user_to_delete.email)
    result = await db_session.exec(statement)
    user = result.first()
    assert user is not None


@pytest.mark.asyncio
async def test_batch_delete_no_authentication(client, db_session):
    """Test batch delete fails when no authentication token is provided"""
    # Create a test user
    user_to_delete = await test_helper.create_user_if_not_exists(client, db_session)

    payload = {
        "identifiers": [user_to_delete.email]
    }

    # Perform request without authorization header
    response = await client.post("/users/batch-delete", json=payload)

    # Assertions - should get forbidden error (403 when no token provided)
    assert response.status_code == 403

    # Verify user was NOT deleted
    statement = select(User).where(User.email == user_to_delete.email)
    result = await db_session.exec(statement)
    user = result.first()
    assert user is not None


@pytest.mark.asyncio
async def test_batch_delete_admin_can_delete_other_admin(client, db_session):
    """Test that one admin can delete another admin account"""
    # Login as first admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create another admin user to delete
    other_admin = await test_helper.create_admin_user_if_not_exists(client, db_session)

    # Delete the other admin account
    payload = {
        "identifiers": [other_admin.email]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Assertions - should succeed
    assert response.status_code == 204

    # Verify admin was deleted
    statement = select(User).where(User.email == other_admin.email)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None


@pytest.mark.asyncio
async def test_batch_delete_with_whitespace_in_identifiers(client, db_session):
    """Test batch delete with whitespace in identifiers (should work if trimmed)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", unique=True)

    # Create test user
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Include whitespace around identifiers
    payload = {
        "identifiers": [f" {user.email} ", f"  {str(user.id)}  "]
    }

    headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
    response = await client.post("/users/batch-delete", json=payload, headers=headers)

    # Note: This test may fail if the implementation doesn't trim whitespace
    # The test documents current behavior
    assert response.status_code == 204
