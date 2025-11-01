import uuid
import pytest
from sqlmodel import select
from database.schemas.roles import Role
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_role_by_id_successful_as_regular_user(client, db_session):
    """Test GET /roles/{id} with regular user (has read:role:all permission by default)"""
    # Login as regular user - they have read:role:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Get the 'user' role (id=2)
    role_id = 2

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/roles/{role_id}", headers=headers)
    role_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "id" in role_data
    assert "name" in role_data
    assert "description" in role_data
    assert "is_active" in role_data
    assert "created_at" in role_data
    assert "permissions" in role_data
    assert role_data["id"] == role_id
    assert role_data["name"] == "user"
    assert isinstance(role_data["permissions"], list)


@pytest.mark.asyncio
async def test_get_role_by_id_successful_as_admin(client, db_session):
    """Test GET /roles/{id} with admin user (has all permissions)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Get the 'admin' role (id=1)
    role_id = 1

    # Perform GET request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/roles/{role_id}", headers=headers)
    role_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert role_data["id"] == role_id
    assert role_data["name"] == "admin"


@pytest.mark.asyncio
async def test_get_role_by_id_insufficient_permissions(client, db_session):
    """Test GET /roles/{id} fails with user that has no permissions"""
    # Login as user without permissions
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Try to get a role
    role_id = 1

    # Perform GET request with user that has no permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/roles/{role_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:role:all" in response_data["message"]


@pytest.mark.asyncio
async def test_get_role_by_nonexistent_id(client, db_session):
    """Test GET /roles/{id} with nonexistent role ID"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to get a nonexistent role
    nonexistent_id = 99999

    # Perform GET request
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get(f"/roles/{nonexistent_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "114_role_not_found"


@pytest.mark.asyncio
async def test_get_role_by_id_unauthenticated(client):
    """Test GET /roles/{id} with unauthenticated user"""
    # Try to get a role without authentication
    role_id = 1

    # Perform GET request without access token
    headers = {
        "accept": "application/json"
    }
    response = await client.get(f"/roles/{role_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_put_role_update_successful_as_admin(client, db_session):
    """Test PUT /roles/{id} with admin user (has update:role:all permission)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a test role first
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    create_payload = {
        "name": f"test-role-{uuid.uuid4().hex[:8]}",
        "description": "Original description"
    }
    create_response = await client.post("/roles", headers=create_headers, json=create_payload)
    created_role = create_response.json()
    role_id = created_role["id"]

    # Update the role
    update_payload = {
        "description": "Updated description",
        "is_active": False
    }
    response = await client.put(f"/roles/{role_id}", headers=create_headers, json=update_payload)
    updated_role_data = response.json()

    # Assertions for API response
    assert response.status_code == 200
    assert updated_role_data["description"] == update_payload["description"]
    assert updated_role_data["is_active"] == update_payload["is_active"]
    # Name should remain unchanged
    assert updated_role_data["name"] == create_payload["name"]

    # Verify in database
    await db_session.commit()
    statement = select(Role).where(Role.id == role_id)
    result = await db_session.exec(statement)
    db_role = result.first()
    assert db_role.description == update_payload["description"]
    assert db_role.is_active == update_payload["is_active"]


@pytest.mark.asyncio
async def test_put_role_update_insufficient_permissions(client, db_session):
    """Test PUT /roles/{id} fails with regular user (lacks update:role:all permission)"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to update a role
    role_id = 2
    update_payload = {
        "description": "Should not work"
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.put(f"/roles/{role_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "update:role:all" in response_data["message"]


@pytest.mark.asyncio
async def test_put_role_update_with_empty_payload(client, db_session):
    """Test PUT /roles/{id} with empty update payload"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to update with empty payload
    role_id = 2
    update_payload = {}

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.put(f"/roles/{role_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 400
    assert response_data["error_code"] == "102_value_error"


@pytest.mark.asyncio
async def test_put_role_update_nonexistent_role(client, db_session):
    """Test PUT /roles/{id} with nonexistent role ID"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to update nonexistent role
    nonexistent_id = 99999
    update_payload = {
        "description": "Should not work"
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.put(f"/roles/{nonexistent_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "114_role_not_found"


@pytest.mark.asyncio
async def test_put_role_update_unauthenticated(client):
    """Test PUT /roles/{id} with unauthenticated user"""
    # Try to update without authentication
    role_id = 2
    update_payload = {
        "description": "Should not work"
    }

    headers = {
        "accept": "application/json"
    }
    response = await client.put(f"/roles/{role_id}", headers=headers, json=update_payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_role_successful_as_admin(client, db_session):
    """Test DELETE /roles/{id} with admin user (has delete:role:all permission)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a test role first
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    create_payload = {
        "name": f"test-role-delete-{uuid.uuid4().hex[:8]}",
        "description": "Role to be deleted"
    }
    create_response = await client.post("/roles", headers=create_headers, json=create_payload)
    created_role = create_response.json()
    role_id = created_role["id"]

    # Delete the role
    response = await client.delete(f"/roles/{role_id}", headers=create_headers)

    # Assertions for API response
    assert response.status_code == 204

    # Verify role was deleted from database
    await db_session.commit()
    statement = select(Role).where(Role.id == role_id)
    result = await db_session.exec(statement)
    deleted_role = result.first()
    assert deleted_role is None


@pytest.mark.asyncio
async def test_delete_role_insufficient_permissions(client, db_session):
    """Test DELETE /roles/{id} fails with regular user (lacks delete:role:all permission)"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to delete a role
    role_id = 2

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.delete(f"/roles/{role_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "delete:role:all" in response_data["message"]


@pytest.mark.asyncio
async def test_delete_role_nonexistent_role(client, db_session):
    """Test DELETE /roles/{id} with nonexistent role ID"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to delete nonexistent role
    nonexistent_id = 99999

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.delete(f"/roles/{nonexistent_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert response_data["error_code"] == "114_role_not_found"


@pytest.mark.asyncio
async def test_delete_role_unauthenticated(client):
    """Test DELETE /roles/{id} with unauthenticated user"""
    # Try to delete without authentication
    role_id = 2

    headers = {
        "accept": "application/json"
    }
    response = await client.delete(f"/roles/{role_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_permission_matrix_comprehensive(client, db_session):
    """Test complete permission matrix for all user types and role operations"""
    # Create different types of users
    regular_user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")
    admin_user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")
    no_perms_user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user2")

    # Create a test role for testing
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_user_data['access_token']}"
    }
    create_payload = {
        "name": f"test-role-matrix-{uuid.uuid4().hex[:8]}",
        "description": "Role for permission matrix testing"
    }
    create_response = await client.post("/roles", headers=create_headers, json=create_payload)
    test_role = create_response.json()
    role_id = test_role["id"]

    # Test GET permissions
    # Regular user: should succeed (has read:role:all)
    response = await client.get(f"/roles/{role_id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"})
    assert response.status_code == 200

    # Admin user: should succeed (has all permissions)
    response = await client.get(f"/roles/{role_id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"})
    assert response.status_code == 200

    # No permissions user: should fail
    response = await client.get(f"/roles/{role_id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"})
    assert response.status_code == 403

    # Test PUT permissions
    update_payload = {"description": "Updated by permission test"}

    # Regular user: should fail (lacks update:role:all)
    response = await client.put(f"/roles/{role_id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 403

    # Admin user: should succeed (has all permissions)
    response = await client.put(f"/roles/{role_id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 200

    # Verify the PUT operation actually updated the database
    await db_session.commit()
    statement = select(Role).where(Role.id == role_id)
    result = await db_session.exec(statement)
    updated_role = result.first()
    assert updated_role.description == update_payload["description"]

    # No permissions user: should fail
    response = await client.put(f"/roles/{role_id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"}, json=update_payload)
    assert response.status_code == 403

    # Test DELETE permissions
    # Regular user: should fail (lacks delete:role:all)
    response = await client.delete(f"/roles/{role_id}", headers={"Authorization": f"Bearer {regular_user_data['access_token']}"})
    assert response.status_code == 403

    # No permissions user: should fail
    response = await client.delete(f"/roles/{role_id}", headers={"Authorization": f"Bearer {no_perms_user_data['access_token']}"})
    assert response.status_code == 403

    # Admin user: should succeed (has all permissions) - test this last since it deletes
    response = await client.delete(f"/roles/{role_id}", headers={"Authorization": f"Bearer {admin_user_data['access_token']}"})
    assert response.status_code == 204

    # Verify the DELETE operation actually removed the role from the database
    await db_session.commit()
    statement = select(Role).where(Role.id == role_id)
    result = await db_session.exec(statement)
    deleted_role = result.first()
    assert deleted_role is None


@pytest.mark.asyncio
async def test_role_crud_lifecycle(client, db_session):
    """Test complete CRUD lifecycle for a role"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # 1. CREATE a new role
    create_payload = {
        "name": f"lifecycle-role-{uuid.uuid4().hex[:8]}",
        "description": "Testing full lifecycle"
    }
    create_response = await client.post("/roles", headers=headers, json=create_payload)
    assert create_response.status_code == 201
    created_role = create_response.json()
    role_id = created_role["id"]
    assert created_role["name"] == create_payload["name"]

    # 2. READ the created role
    get_response = await client.get(f"/roles/{role_id}", headers=headers)
    assert get_response.status_code == 200
    fetched_role = get_response.json()
    assert fetched_role["id"] == role_id
    assert fetched_role["name"] == create_payload["name"]
    assert fetched_role["description"] == create_payload["description"]

    # 3. UPDATE the role
    update_payload = {
        "description": "Updated lifecycle description",
        "is_active": False
    }
    update_response = await client.put(f"/roles/{role_id}", headers=headers, json=update_payload)
    assert update_response.status_code == 200
    updated_role = update_response.json()
    assert updated_role["description"] == update_payload["description"]
    assert updated_role["is_active"] == update_payload["is_active"]

    # Verify update in database
    await db_session.commit()
    statement = select(Role).where(Role.id == role_id)
    result = await db_session.exec(statement)
    db_role = result.first()
    assert db_role.description == update_payload["description"]
    assert db_role.is_active == update_payload["is_active"]

    # 4. DELETE the role
    delete_response = await client.delete(f"/roles/{role_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify deletion in database
    await db_session.commit()
    statement = select(Role).where(Role.id == role_id)
    result = await db_session.exec(statement)
    deleted_role = result.first()
    assert deleted_role is None

    # 5. Verify role no longer exists
    get_deleted_response = await client.get(f"/roles/{role_id}", headers=headers)
    assert get_deleted_response.status_code == 404


@pytest.mark.asyncio
async def test_role_update_partial_fields(client, db_session):
    """Test that role updates support partial field updates (PATCH-like behavior)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # Create a test role
    create_payload = {
        "name": f"partial-update-{uuid.uuid4().hex[:8]}",
        "description": "Original description"
    }
    create_response = await client.post("/roles", headers=headers, json=create_payload)
    created_role = create_response.json()
    role_id = created_role["id"]

    # Update only description (name should remain unchanged)
    update_payload = {
        "description": "Only description updated"
    }
    update_response = await client.put(f"/roles/{role_id}", headers=headers, json=update_payload)
    assert update_response.status_code == 200
    updated_role = update_response.json()
    assert updated_role["description"] == update_payload["description"]
    assert updated_role["name"] == create_payload["name"]  # Name unchanged

    # Update only is_active (other fields should remain unchanged)
    update_payload_2 = {
        "is_active": False
    }
    update_response_2 = await client.put(f"/roles/{role_id}", headers=headers, json=update_payload_2)
    assert update_response_2.status_code == 200
    updated_role_2 = update_response_2.json()
    assert not updated_role_2["is_active"]
    # Previous update preserved
    assert updated_role_2["description"] == "Only description updated"
    assert updated_role_2["name"] == create_payload["name"]  # Still unchanged
