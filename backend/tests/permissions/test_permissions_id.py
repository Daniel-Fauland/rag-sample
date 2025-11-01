import pytest
from sqlmodel import select
from database.schemas.permissions import Permission
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_permission_by_id_successful_as_regular_user(client, db_session):
    """Test GET /permissions/{id} with regular user (has read:permission:all permission by default)"""
    # Login as regular user - they have read:permission:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Get a specific permission (id=1)
    permission_id = 1

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/permissions/{permission_id}", headers=headers)
    permission_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "id" in permission_data
    assert "type" in permission_data
    assert "resource" in permission_data
    assert "context" in permission_data
    assert "description" in permission_data
    assert "is_active" in permission_data
    assert "created_at" in permission_data
    assert "roles" in permission_data
    assert permission_data["id"] == permission_id
    assert isinstance(permission_data["roles"], list)


@pytest.mark.asyncio
async def test_get_permission_by_id_successful_as_admin(client, db_session):
    """Test GET /permissions/{id} with admin user (has all permissions)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Get a specific permission
    permission_id = 2

    # Perform GET request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/permissions/{permission_id}", headers=headers)
    permission_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert permission_data["id"] == permission_id


@pytest.mark.asyncio
async def test_get_permission_by_id_insufficient_permissions(client, db_session):
    """Test GET /permissions/{id} fails with user that has no permissions"""
    # Login as user without permissions
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Try to get a permission
    permission_id = 1

    # Perform GET request with user that has no permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/permissions/{permission_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:permission:all" in response_data["message"]


@pytest.mark.asyncio
async def test_get_permission_by_nonexistent_id(client, db_session):
    """Test GET /permissions/{id} with nonexistent permission ID"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to get a nonexistent permission
    nonexistent_id = 99999

    # Perform GET request
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/permissions/{nonexistent_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "116_permission_not_found"


@pytest.mark.asyncio
async def test_get_permission_by_id_unauthenticated(client):
    """Test GET /permissions/{id} with unauthenticated user"""
    # Try to get a permission without authentication
    permission_id = 1

    # Perform GET request without access token
    headers = {
        "accept": "application/json"
    }
    response = await client.get(f"/permissions/{permission_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_put_permission_update_successful_as_admin(client, db_session):
    """Test PUT /permissions/{id} with admin user (has update:permission:all permission)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a test permission first
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    create_payload = {
        "type": "read",
        "resource": "test_update_resource",
        "context": "all",
        "description": "Original description"
    }
    create_response = await client.post("/permissions", headers=create_headers, json=create_payload)
    created_permission = create_response.json()
    permission_id = created_permission["id"]

    # Update the permission
    update_payload = {
        "description": "Updated description",
        "is_active": False
    }
    response = await client.put(f"/permissions/{permission_id}", headers=create_headers, json=update_payload)
    updated_permission_data = response.json()

    # Assertions for API response
    assert response.status_code == 200
    assert updated_permission_data["description"] == update_payload["description"]
    assert updated_permission_data["is_active"] == update_payload["is_active"]
    # Type, resource, context should remain unchanged
    assert updated_permission_data["type"] == create_payload["type"]
    assert updated_permission_data["resource"] == create_payload["resource"]
    assert updated_permission_data["context"] == create_payload["context"]

    # Verify in database
    await db_session.commit()
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db_session.exec(statement)
    db_permission = result.first()
    assert db_permission.description == update_payload["description"]
    assert db_permission.is_active == update_payload["is_active"]


@pytest.mark.asyncio
async def test_put_permission_update_insufficient_permissions(client, db_session):
    """Test PUT /permissions/{id} fails with regular user (lacks update:permission:all permission)"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to update a permission
    permission_id = 1
    update_payload = {
        "description": "Should not work"
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.put(f"/permissions/{permission_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "update:permission:all" in response_data["message"]


@pytest.mark.asyncio
async def test_put_permission_update_with_empty_payload(client, db_session):
    """Test PUT /permissions/{id} with empty update payload"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to update with empty payload
    permission_id = 1
    update_payload = {}

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.put(f"/permissions/{permission_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 400
    assert response_data["error_code"] == "102_value_error"


@pytest.mark.asyncio
async def test_put_permission_update_nonexistent_permission(client, db_session):
    """Test PUT /permissions/{id} with nonexistent permission ID"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to update nonexistent permission
    nonexistent_id = 99999
    update_payload = {
        "description": "Should not work"
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.put(f"/permissions/{nonexistent_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "116_permission_not_found"


@pytest.mark.asyncio
async def test_put_permission_update_unauthenticated(client):
    """Test PUT /permissions/{id} with unauthenticated user"""
    # Try to update without authentication
    permission_id = 1
    update_payload = {
        "description": "Should not work"
    }

    headers = {
        "accept": "application/json"
    }
    response = await client.put(f"/permissions/{permission_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_permission_successful_as_admin(client, db_session):
    """Test DELETE /permissions/{id} with admin user (has delete:permission:all permission)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a test permission first
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    create_payload = {
        "type": "read",
        "resource": "test_delete_resource",
        "context": "all",
        "description": "Permission to be deleted"
    }
    create_response = await client.post("/permissions", headers=create_headers, json=create_payload)
    created_permission = create_response.json()
    permission_id = created_permission["id"]

    # Delete the permission
    response = await client.delete(f"/permissions/{permission_id}", headers=create_headers)

    # Assertions for API response
    assert response.status_code == 204

    # Verify permission was deleted from database
    await db_session.commit()
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db_session.exec(statement)
    deleted_permission = result.first()
    assert deleted_permission is None


@pytest.mark.asyncio
async def test_delete_permission_insufficient_permissions(client, db_session):
    """Test DELETE /permissions/{id} fails with regular user (lacks delete:permission:all permission)"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to delete a permission
    permission_id = 1

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.delete(f"/permissions/{permission_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "delete:permission:all" in response_data["message"]


@pytest.mark.asyncio
async def test_delete_permission_nonexistent_permission(client, db_session):
    """Test DELETE /permissions/{id} with nonexistent permission ID"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to delete nonexistent permission
    nonexistent_id = 99999

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.delete(f"/permissions/{nonexistent_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "116_permission_not_found"


@pytest.mark.asyncio
async def test_delete_permission_unauthenticated(client):
    """Test DELETE /permissions/{id} with unauthenticated user"""
    # Try to delete without authentication
    permission_id = 1

    headers = {
        "accept": "application/json"
    }
    response = await client.delete(f"/permissions/{permission_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_permission_matrix_comprehensive(client, db_session):
    """Test complete permission matrix for all user types and permission operations"""
    # Create different types of users
    regular_user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")
    admin_user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")
    no_perms_user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user2")

    # Create a test permission for testing
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_user_data['access_token']}"
    }
    create_payload = {
        "type": "read",
        "resource": "test_matrix_resource",
        "context": "all",
        "description": "Permission for matrix testing"
    }
    create_response = await client.post("/permissions", headers=create_headers, json=create_payload)
    test_permission = create_response.json()
    permission_id = test_permission["id"]

    # Test GET permissions
    # Regular user: should succeed (has read:permission:all)
    response = await client.get(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"})
    assert response.status_code == 200

    # Admin user: should succeed (has all permissions)
    response = await client.get(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"})
    assert response.status_code == 200

    # No permissions user: should fail
    response = await client.get(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"})
    assert response.status_code == 403

    # Test PUT permissions
    update_payload = {"description": "Updated by permission test"}

    # Regular user: should fail (lacks update:permission:all)
    response = await client.put(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 403

    # Admin user: should succeed (has all permissions)
    response = await client.put(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 200

    # Verify the PUT operation actually updated the database
    await db_session.commit()
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db_session.exec(statement)
    updated_permission = result.first()
    assert updated_permission.description == update_payload["description"]

    # No permissions user: should fail
    response = await client.put(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 403

    # Test DELETE permissions
    # Regular user: should fail (lacks delete:permission:all)
    response = await client.delete(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"})
    assert response.status_code == 403

    # No permissions user: should fail
    response = await client.delete(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"})
    assert response.status_code == 403

    # Admin user: should succeed (has all permissions) - test this last since it deletes
    response = await client.delete(f"/permissions/{permission_id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"})
    assert response.status_code == 204

    # Verify the DELETE operation actually removed the permission from the database
    await db_session.commit()
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db_session.exec(statement)
    deleted_permission = result.first()
    assert deleted_permission is None


@pytest.mark.asyncio
async def test_permission_crud_lifecycle(client, db_session):
    """Test complete CRUD lifecycle for a permission"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # 1. CREATE a new permission
    create_payload = {
        "type": "update",
        "resource": "lifecycle_resource",
        "context": "me",
        "description": "Testing full lifecycle"
    }
    create_response = await client.post("/permissions", headers=headers, json=create_payload)
    assert create_response.status_code == 201
    created_permission = create_response.json()
    permission_id = created_permission["id"]
    assert created_permission["type"] == create_payload["type"]
    assert created_permission["resource"] == create_payload["resource"]
    assert created_permission["context"] == create_payload["context"]

    # 2. READ the created permission
    get_response = await client.get(f"/permissions/{permission_id}", headers=headers)
    assert get_response.status_code == 200
    fetched_permission = get_response.json()
    assert fetched_permission["id"] == permission_id
    assert fetched_permission["type"] == create_payload["type"]
    assert fetched_permission["resource"] == create_payload["resource"]
    assert fetched_permission["context"] == create_payload["context"]
    assert fetched_permission["description"] == create_payload["description"]

    # 3. UPDATE the permission
    update_payload = {
        "description": "Updated lifecycle description",
        "is_active": False
    }
    update_response = await client.put(f"/permissions/{permission_id}", headers=headers, json=update_payload)
    assert update_response.status_code == 200
    updated_permission = update_response.json()
    assert updated_permission["description"] == update_payload["description"]
    assert updated_permission["is_active"] == update_payload["is_active"]

    # Verify update in database
    await db_session.commit()
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db_session.exec(statement)
    db_permission = result.first()
    assert db_permission.description == update_payload["description"]
    assert db_permission.is_active == update_payload["is_active"]

    # 4. DELETE the permission
    delete_response = await client.delete(f"/permissions/{permission_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify deletion in database
    await db_session.commit()
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db_session.exec(statement)
    deleted_permission = result.first()
    assert deleted_permission is None

    # 5. Verify permission no longer exists
    get_deleted_response = await client.get(f"/permissions/{permission_id}", headers=headers)
    assert get_deleted_response.status_code == 404


@pytest.mark.asyncio
async def test_permission_update_partial_fields(client, db_session):
    """Test that permission updates support partial field updates (PATCH-like behavior)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # Create a test permission
    create_payload = {
        "type": "delete",
        "resource": "partial_update_resource",
        "context": "all",
        "description": "Original description"
    }
    create_response = await client.post("/permissions", headers=headers, json=create_payload)
    created_permission = create_response.json()
    permission_id = created_permission["id"]

    # Update only description (type, resource, context should remain unchanged)
    update_payload = {
        "description": "Only description updated"
    }
    update_response = await client.put(f"/permissions/{permission_id}", headers=headers, json=update_payload)
    assert update_response.status_code == 200
    updated_permission = update_response.json()
    assert updated_permission["description"] == update_payload["description"]
    assert updated_permission["type"] == create_payload["type"]
    assert updated_permission["resource"] == create_payload["resource"]
    assert updated_permission["context"] == create_payload["context"]

    # Update only is_active (other fields should remain unchanged)
    update_payload_2 = {
        "is_active": False
    }
    update_response_2 = await client.put(f"/permissions/{permission_id}", headers=headers, json=update_payload_2)
    assert update_response_2.status_code == 200
    updated_permission_2 = update_response_2.json()
    assert not updated_permission_2["is_active"]
    # Previous update preserved
    assert updated_permission_2["description"] == "Only description updated"
    assert updated_permission_2["type"] == create_payload["type"]
    assert updated_permission_2["resource"] == create_payload["resource"]
    assert updated_permission_2["context"] == create_payload["context"]
