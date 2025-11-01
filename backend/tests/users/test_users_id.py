import pytest
from sqlmodel import select
from database.schemas.users import User
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_user_by_id_own_data_as_regular_user(client, db_session):
    """Test GET /user/{id} accessing own data with regular user (has read:user:me permission)"""
    # Login as regular user (automatically creates user)
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request accessing own user data by UUID
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/users/{user.id}", headers=headers)
    user_response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "id" in user_response_data
    assert "email" in user_response_data
    assert "roles" in user_response_data
    assert user_response_data["email"] == "test_normal_user1@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email_own_data_as_regular_user(client, db_session):
    """Test GET /user/{id} accessing own data by email with regular user"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user2")

    # Perform GET request accessing own user data by email
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/users/{user.email}", headers=headers)
    user_response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert user_response_data["email"] == user.email


@pytest.mark.asyncio
async def test_get_user_by_id_other_data_as_regular_user(client, db_session):
    """Test GET /user/{id} accessing other's data with regular user (has read:user:all permission)"""
    # Login as regular user
    user1_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create another user to access
    user2 = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "target_user@example.com"})

    # User1 tries to access user2's data by UUID
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user1_data['access_token']}"
    }
    response = await client.get(f"/users/{user2.id}", headers=headers)
    user_response_data = response.json()

    # Assertions - should succeed as regular users have read:user:all permission
    assert response.status_code == 200
    assert user_response_data["email"] == "target_user@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id_insufficient_permissions_as_user_without_permissions(client, db_session):
    """Test GET /user/{id} fails with user that has no permissions"""
    # Create user without permissions
    user_with_no_perms_data, user = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Create target user to try to access
    target_user = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "target_user2@example.com"})

    # Perform GET request with user that has no permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_with_no_perms_data['access_token']}"
    }
    response = await client.get(f"/users/{target_user.id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"


@pytest.mark.asyncio
async def test_get_user_by_invalid_uuid(client, db_session):
    """Test GET /user/{id} with invalid UUID format"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with invalid UUID
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users/invalid-uuid-format", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 400
    assert response_data["error_code"] == "111_invalid_uuid"


@pytest.mark.asyncio
async def test_get_user_by_nonexistent_id(client, db_session):
    """Test GET /user/{id} with nonexistent user ID"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with nonexistent UUID
    nonexistent_uuid = "01234567-89ab-cdef-0123-456789abcdef"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/users/{nonexistent_uuid}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "108_user_not_found"


@pytest.mark.asyncio
async def test_put_user_update_own_data_as_regular_user(client, db_session):
    """Test PUT /user/{id} updating own data with regular user (has update:user:me permission)"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Store original values for comparison
    original_email = user.email
    original_user_id = user.id

    # Perform PUT request to update own data
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    update_payload = {
        "first_name": "UpdatedFirst",
        "last_name": "UpdatedLast"
    }
    response = await client.put(f"/users/{original_user_id}", headers=headers, json=update_payload)
    updated_user_data = response.json()

    # Assertions for API response
    assert response.status_code == 200
    assert updated_user_data["first_name"] == update_payload["first_name"]
    assert updated_user_data["last_name"] == update_payload["last_name"]
    # Email unchanged
    assert updated_user_data["email"] == original_email

    # Refresh the database session to see committed changes
    await db_session.commit()
    await db_session.refresh(user)

    # Check if the data got changed successfully in the database
    assert user.first_name == update_payload["first_name"]
    assert user.last_name == update_payload["last_name"]
    assert user.email == original_email  # Email should remain unchanged


@pytest.mark.asyncio
async def test_put_user_update_other_data_insufficient_permissions_as_regular_user(client, db_session):
    """Test PUT /user/{id} updating other's data fails with regular user (lacks update:user:all)"""
    # Login as regular user
    user1_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create another user to try to update
    user2 = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "target_update@example.com"})

    # User1 tries to update user2's data
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user1_data['access_token']}"
    }
    update_payload = {
        "first_name": "ShouldNotWork"
    }
    response = await client.put(f"/users/{user2.id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions - should fail as regular users don't have update:user:all permission
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"


@pytest.mark.asyncio
async def test_put_user_update_other_data_as_admin_user(client, db_session):
    """Test PUT /user/{id} updating other's data with admin user (has all permissions)"""
    # Login as admin user
    admin_data, user = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create target user to update
    target_user = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "target_update_by_admin@example.com"})
    original_target_email = target_user.email

    # Admin updates target user's data
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    update_payload = {
        "first_name": "AdminUpdated",
        "last_name": "ByAdmin"
    }
    response = await client.put(f"/users/{target_user.id}", headers=headers, json=update_payload)
    updated_user_data = response.json()

    # Assertions for API response
    assert response.status_code == 200
    assert updated_user_data["first_name"] == update_payload["first_name"]
    assert updated_user_data["last_name"] == update_payload["last_name"]

    # Refresh the database session to see committed changes
    await db_session.commit()
    await db_session.refresh(target_user)

    # Check if the data got changed successfully in the database
    assert target_user.first_name == update_payload["first_name"]
    assert target_user.last_name == update_payload["last_name"]
    assert target_user.email == original_target_email  # Email should remain unchanged


@pytest.mark.asyncio
async def test_put_user_update_with_empty_payload(client, db_session):
    """Test PUT /user/{id} with empty update payload"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform PUT request with empty payload
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    update_payload = {}
    response = await client.put(f"/users/{user.id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 400
    assert response_data["error_code"] == "102_value_error"


@pytest.mark.asyncio
async def test_put_user_update_with_invalid_email(client, db_session):
    """Test PUT /user/{id} with invalid email format"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform PUT request with invalid email
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    update_payload = {
        "email": "invalid-email-format"
    }
    response = await client.put(f"/users/{user.id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 422  # Validation error
    assert "detail" in response_data


@pytest.mark.asyncio
async def test_delete_user_own_data_as_regular_user(client, db_session):
    """Test DELETE /user/{id} deleting own data with regular user (has delete:user:me permission)"""
    # Login as regular user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")
    original_user_id = user.id

    # Perform DELETE request to delete own data
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.delete(f"/users/{user.id}", headers=headers)

    # Assertions for API response
    assert response.status_code == 204

    # Refresh the database session to see committed changes
    await db_session.commit()

    # Check if the user was actually deleted from the database
    statement = select(User).where(User.id == original_user_id)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None  # User should be deleted


@pytest.mark.asyncio
async def test_delete_user_other_data_insufficient_permissions_as_regular_user(client, db_session):
    """Test DELETE /user/{id} deleting other's data fails with regular user (lacks delete:user:all)"""
    # Login as regular user
    user1_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create another user to try to delete
    user2 = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "target_delete@example.com"})

    # User1 tries to delete user2
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user1_data['access_token']}"
    }
    response = await client.delete(f"/users/{user2.id}", headers=headers)
    response_data = response.json()

    # Assertions - should fail as regular users don't have delete:user:all permission
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"


@pytest.mark.asyncio
async def test_delete_user_other_data_as_admin_user(client, db_session):
    """Test DELETE /user/{id} deleting other's data with admin user (has all permissions)"""
    # Login as admin user
    admin_data, user = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create target user to delete
    target_user = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "target_delete_by_admin@example.com"})
    original_target_id = target_user.id

    # Admin deletes target user
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    response = await client.delete(f"/users/{target_user.id}", headers=headers)

    # Assertions for API response
    assert response.status_code == 204

    # Refresh the database session to see committed changes
    await db_session.commit()

    # Check if the target user was actually deleted from the database
    statement = select(User).where(User.id == original_target_id)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None  # Target user should be deleted


@pytest.mark.asyncio
async def test_delete_user_nonexistent_user(client, db_session):
    """Test DELETE /user/{id} with nonexistent user"""
    # Login as admin user (to have delete permissions)
    user_data, user = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to delete nonexistent user
    nonexistent_uuid = "01234567-89ab-cdef-0123-456789abcdef"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.delete(f"/users/{nonexistent_uuid}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "108_user_not_found"


@pytest.mark.asyncio
async def test_permission_matrix_comprehensive(client, db_session):
    """Test complete permission matrix for all user types and operations"""
    # Create different types of users
    regular_user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")
    admin_user_data, user = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")
    no_perms_user_data, user = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user2")

    # Create target user for testing
    target_user = await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "permission_test_target@example.com"})
    original_target_id = target_user.id

    # Test GET permissions
    # Regular user: should succeed (has read:user:all)
    response = await client.get(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"})
    assert response.status_code == 200

    # Admin user: should succeed (has all permissions)
    response = await client.get(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"})
    assert response.status_code == 200

    # No permissions user: should fail
    response = await client.get(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"})
    assert response.status_code == 403

    # Test PUT permissions
    update_payload = {"first_name": "TestUpdate"}

    # Regular user: should fail (lacks update:user:all)
    response = await client.put(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 403

    # Admin user: should succeed (has all permissions)
    response = await client.put(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 200

    # Verify the PUT operation actually updated the database
    await db_session.commit()
    await db_session.refresh(target_user)
    assert target_user.first_name == update_payload["first_name"]

    # No permissions user: should fail
    response = await client.put(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 403

    # Test DELETE permissions
    # Regular user: should fail (lacks delete:user:all)
    response = await client.delete(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"})
    assert response.status_code == 403

    # No permissions user: should fail
    response = await client.delete(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"})
    assert response.status_code == 403

    # Admin user: should succeed (has all permissions) - we'll test this last since it actually deletes
    response = await client.delete(f"/users/{target_user.id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"})
    assert response.status_code == 204

    # Verify the DELETE operation actually removed the user from the database
    await db_session.commit()
    statement = select(User).where(User.id == original_target_id)
    result = await db_session.exec(statement)
    deleted_user = result.first()
    assert deleted_user is None  # User should be deleted


@pytest.mark.asyncio
async def test_user_access_own_vs_other_data(client, db_session):
    """Test that users can access/modify their own data but not others' (except admins)"""
    # Create two regular users
    user1_data, user1 = await test_helper.login_user_with_type(client, db_session, "normal", "user1")
    user2_data, user2 = await test_helper.login_user_with_type(client, db_session, "normal", "user2")

    # Store original IDs for database validation
    original_user1_id = user1.id

    # User1 can read their own data
    response = await client.get(f"/users/{user1.id}", headers={"Authorization": f"Bearer {user1_data['access_token']}"})
    assert response.status_code == 200

    # User1 can read user2's data (has read:user:all)
    response = await client.get(f"/users/{user2.id}", headers={"Authorization": f"Bearer {user1_data['access_token']}"})
    assert response.status_code == 200

    # User1 can update their own data
    update_payload = {"first_name": "Updated"}
    response = await client.put(f"/users/{user1.id}", headers={"Authorization": f"Bearer {user1_data['access_token']}"}, json=update_payload)
    assert response.status_code == 200

    # Verify the update actually changed the database
    await db_session.commit()
    await db_session.refresh(user1)
    assert user1.first_name == update_payload["first_name"]

    # User1 cannot update user2's data (lacks update:user:all)
    response = await client.put(f"/users/{user2.id}", headers={"Authorization": f"Bearer {user1_data['access_token']}"}, json={"first_name": "ShouldNotWork"})
    assert response.status_code == 403

    # Verify user2's data wasn't changed in the database
    await db_session.refresh(user2)
    assert user2.first_name != "ShouldNotWork"  # Should still have original value

    # User1 can delete their own data
    response = await client.delete(f"/users/{user1.id}", headers={"Authorization": f"Bearer {user1_data['access_token']}"})
    assert response.status_code == 204

    # Verify user1 was actually deleted from the database
    await db_session.commit()
    statement = select(User).where(User.id == original_user1_id)
    result = await db_session.exec(statement)
    deleted_user1 = result.first()
    assert deleted_user1 is None  # User1 should be deleted

    # User2 cannot delete user1's data (even though user1 is already deleted)
    response = await client.delete(f"/users/{user1.id}", headers={"Authorization": f"Bearer {user2_data['access_token']}"})
    # Permission check happens before existence check
    assert response.status_code == 403
