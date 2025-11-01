import pytest
from tests.test_helper import TestHelper


test_helper = TestHelper()


# Helper function to create a test role for permission assignment tests
async def create_test_role(client, headers, role_name="test_permission_assignment_role"):
    """Create a dedicated test role for permission assignment tests to ensure test isolation"""
    payload = {
        "name": role_name,
        "description": "Test role for permission assignment tests"
    }
    response = await client.post("/roles", headers=headers, json=payload)
    if response.status_code == 201:
        return response.json()
    # If role already exists (409), get it
    elif response.status_code == 409:
        roles_response = await client.get("/roles", headers=headers)
        roles = roles_response.json()
        for role in roles:
            if role["name"] == role_name:
                return role
    return None


@pytest.mark.asyncio
async def test_get_all_permission_assignments_as_admin(client, db_session):
    """Test GET /permission-assignments as admin (has all permissions)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "user1")

    # Perform GET request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/permission-assignments", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, list)
    # At least some default permission assignments
    assert len(response_data) >= 2
    for assignment in response_data:
        assert "role_id" in assignment
        assert "permission_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["permission_id"], int)
        assert isinstance(assignment["assigned_at"], str)


@pytest.mark.asyncio
async def test_get_all_permission_assignments_as_admin_with_query_parameter(client, db_session):
    """Test GET /permission-assignments as admin with query parameters (has all permissions)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "user1")

    # Perform GET request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # - Test sorting -
    role_id = None
    permission_id = None
    order_by_field = "permission_id"
    order_by_direction = "asc"
    limit = 999
    response = await client.get(f"/permission-assignments?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data) >= 2
    for assignment in response_data:
        assert "role_id" in assignment
        assert "permission_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["permission_id"], int)
        assert isinstance(assignment["assigned_at"], str)
    permission_ids = [assignment["permission_id"]
                      for assignment in response_data]
    assert permission_ids == sorted(
        permission_ids), "permission_id values should be sorted in ascending order"

    # - Test filtering by role_id -
    role_id = 1  # admin role
    permission_id = None
    order_by_field = "permission_id"
    order_by_direction = "asc"
    limit = 999
    response = await client.get(f"/permission-assignments?role_id={role_id}&order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, list)
    # Admin role might have 0 or more permissions depending on migrations
    assert len(response_data) >= 0
    for assignment in response_data:
        assert "role_id" in assignment
        assert "permission_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["permission_id"], int)
        assert isinstance(assignment["assigned_at"], str)
        assert assignment["role_id"] == role_id

    # - Test filtering by both role_id and permission_id -
    role_id = 1  # admin role
    permission_id = 1  # first permission
    order_by_field = "permission_id"
    order_by_direction = "asc"
    limit = 999
    response = await client.get(f"/permission-assignments?role_id={role_id}&permission_id={permission_id}&order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, list)
    # Should have 0 or 1 results
    for assignment in response_data:
        assert assignment["role_id"] == role_id
        assert assignment["permission_id"] == permission_id

    # - Test filtering with nonexistent combination -
    role_id = 1
    permission_id = 99999  # nonexistent permission
    order_by_field = "permission_id"
    order_by_direction = "asc"
    limit = 999
    response = await client.get(f"/permission-assignments?role_id={role_id}&permission_id={permission_id}&order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data) == 0

    # - Test limits -
    role_id = None
    permission_id = None
    order_by_field = "permission_id"
    order_by_direction = "asc"
    limit = 1
    response = await client.get(f"/permission-assignments?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    for assignment in response_data:
        assert "role_id" in assignment
        assert "permission_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["permission_id"], int)
        assert isinstance(assignment["assigned_at"], str)


@pytest.mark.asyncio
async def test_get_all_permission_assignments_as_normal_user(client, db_session):
    """Test GET /permission-assignments as normal user (requires read:permission_assignment:all)"""
    # Login as normal user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with normal user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # - Try to get all permission assignments -> This should fail due to insufficient permissions -
    response = await client.get("/permission-assignments", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:permission_assignment:all" in response_data["message"]


@pytest.mark.asyncio
async def test_get_all_permission_assignments_unauthenticated(client, db_session):
    """Test GET /permission-assignments without authentication"""
    # Try to get permission assignments without authentication
    headers = {
        "accept": "application/json"
    }
    response = await client.get("/permission-assignments", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_permission_assignment_as_admin(client, db_session):
    """Test POST /permission-assignments as admin (has create:permission_assignment:all permission)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }

    # Create a dedicated test role for this test
    test_role = await create_test_role(client, headers, "test_role_create_perm_1")
    assert test_role is not None, "Failed to create test role"

    # Get all permissions to find one we can use
    perms_response = await client.get("/permissions", headers=headers)
    all_permissions = perms_response.json()
    assert len(all_permissions) > 0, "Need at least one permission in the database"

    # Get existing assignments for the test role to find a permission not yet assigned
    existing_response = await client.get(f"/permission-assignments?role_id={test_role['id']}", headers=headers)
    existing_assignments = existing_response.json()
    assigned_permission_ids = {a["permission_id"]
                               for a in existing_assignments}

    # Find a permission that's not yet assigned to the test role
    available_permission = None
    for perm in all_permissions:
        if perm["id"] not in assigned_permission_ids:
            available_permission = perm
            break

    assert available_permission is not None, "Need at least one unassigned permission for this test"

    # Perform POST request to assign the permission to the test role
    payload = {
        "role_id": test_role["id"],
        "permission_id": available_permission["id"]
    }
    response = await client.post("/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 201
    assert "role_id" in response_data
    assert "permission_id" in response_data
    assert "success" in response_data
    assert "message" in response_data
    assert response_data["role_id"] == test_role["id"]
    assert response_data["permission_id"] == available_permission["id"]
    assert response_data["success"] is True
    assert "successfully" in response_data["message"].lower()


@pytest.mark.asyncio
async def test_create_permission_assignment_as_normal_user(client, db_session):
    """Test POST /permission-assignments as normal user (requires create:permission_assignment:all)"""
    # Login as normal user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to assign a permission - should fail due to insufficient permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    payload = {
        "role_id": 2,
        "permission_id": 1
    }
    response = await client.post("/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "create:permission_assignment:all" in response_data["message"]


@pytest.mark.asyncio
async def test_create_permission_assignment_duplicate(client, db_session):
    """Test POST /permission-assignments with duplicate assignment (role already has the permission)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin2")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }

    # Create a dedicated test role for this test
    test_role = await create_test_role(client, headers, "test_role_duplicate_perm")
    assert test_role is not None, "Failed to create test role"

    # Get an available permission
    perms_response = await client.get("/permissions", headers=headers)
    all_permissions = perms_response.json()
    existing_response = await client.get(f"/permission-assignments?role_id={test_role['id']}", headers=headers)
    existing_assignments = existing_response.json()
    assigned_permission_ids = {a["permission_id"]
                               for a in existing_assignments}

    available_permission = None
    for perm in all_permissions:
        if perm["id"] not in assigned_permission_ids:
            available_permission = perm
            break

    assert available_permission is not None, "Need at least one unassigned permission for this test"

    # First, create a permission assignment
    payload = {
        "role_id": test_role["id"],
        "permission_id": available_permission["id"]
    }
    first_response = await client.post("/permission-assignments", headers=headers, json=payload)
    assert first_response.status_code == 201

    # Try to create the same assignment again
    response = await client.post("/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 409
    assert "error_code" in response_data
    assert response_data["error_code"] == "123_permission_assignment_already_exists"


@pytest.mark.asyncio
async def test_create_permission_assignment_nonexistent_role(client, db_session):
    """Test POST /permission-assignments with nonexistent role ID"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to assign permission to nonexistent role
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    payload = {
        "role_id": 99999,  # nonexistent role
        "permission_id": 1
    }
    response = await client.post("/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert "error_code" in response_data
    assert response_data["error_code"] == "114_role_not_found"


@pytest.mark.asyncio
async def test_create_permission_assignment_nonexistent_permission(client, db_session):
    """Test POST /permission-assignments with nonexistent permission ID"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to assign nonexistent permission
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    payload = {
        "role_id": 2,
        "permission_id": 99999  # nonexistent permission
    }
    response = await client.post("/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert "error_code" in response_data
    assert response_data["error_code"] == "116_permission_not_found"


@pytest.mark.asyncio
async def test_create_permission_assignment_unauthenticated(client, db_session):
    """Test POST /permission-assignments without authentication"""
    # Try to assign permission without authentication
    headers = {
        "accept": "application/json"
    }
    payload = {
        "role_id": 2,
        "permission_id": 1
    }
    response = await client.post("/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_permission_assignment_as_admin(client, db_session):
    """Test DELETE /permission-assignments as admin (has delete:permission_assignment:all permission)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }

    # Create a dedicated test role for this test
    test_role = await create_test_role(client, create_headers, "test_role_delete_perm")
    assert test_role is not None, "Failed to create test role"

    # Get an available permission
    perms_response = await client.get("/permissions", headers=create_headers)
    all_permissions = perms_response.json()
    existing_response = await client.get(f"/permission-assignments?role_id={test_role['id']}", headers=create_headers)
    existing_assignments = existing_response.json()
    assigned_permission_ids = {a["permission_id"]
                               for a in existing_assignments}

    available_permission = None
    for perm in all_permissions:
        if perm["id"] not in assigned_permission_ids:
            available_permission = perm
            break

    assert available_permission is not None, "Need at least one unassigned permission for this test"

    # Create a permission assignment first
    create_payload = {
        "role_id": test_role["id"],
        "permission_id": available_permission["id"]
    }
    create_response = await client.post("/permission-assignments", headers=create_headers, json=create_payload)
    assert create_response.status_code == 201

    # Now delete the permission assignment
    delete_payload = {
        "role_id": test_role["id"],
        "permission_id": available_permission["id"]
    }
    create_headers["Content-Type"] = "application/json"
    response = await client.request("DELETE", "/permission-assignments", headers=create_headers, json=delete_payload)

    # Assertions
    assert response.status_code == 204

    # Verify the assignment was deleted by trying to get it
    get_response = await client.get(f"/permission-assignments?role_id={test_role['id']}&permission_id={available_permission['id']}", headers=create_headers)
    get_data = get_response.json()
    assert len(get_data) == 0  # Should be empty now


@pytest.mark.asyncio
async def test_delete_permission_assignment_as_normal_user(client, db_session):
    """Test DELETE /permission-assignments as normal user (requires delete:permission_assignment:all)"""
    # Login as normal user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to delete a permission assignment - should fail due to insufficient permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "role_id": 2,
        "permission_id": 1
    }
    response = await client.request("DELETE", "/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "delete:permission_assignment:all" in response_data["message"]


@pytest.mark.asyncio
async def test_delete_permission_assignment_nonexistent(client, db_session):
    """Test DELETE /permission-assignments with nonexistent assignment"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to delete a permission assignment that doesn't exist
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "role_id": 2,
        "permission_id": 99999  # nonexistent permission
    }
    response = await client.request("DELETE", "/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert "error_code" in response_data
    assert response_data["error_code"] == "122_permission_assignment_not_found"


@pytest.mark.asyncio
async def test_delete_permission_assignment_unauthenticated(client, db_session):
    """Test DELETE /permission-assignments without authentication"""
    # Try to delete permission assignment without authentication
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "role_id": 2,
        "permission_id": 1
    }
    response = await client.request("DELETE", "/permission-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_permission_assignment_crud_lifecycle(client, db_session):
    """Test complete CRUD lifecycle for permission assignments"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin3")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }

    # Create a dedicated test role for this test
    test_role = await create_test_role(client, headers, "test_role_crud_lifecycle")
    assert test_role is not None, "Failed to create test role"

    # Get an available permission
    perms_response = await client.get("/permissions", headers=headers)
    all_permissions = perms_response.json()
    existing_response = await client.get(f"/permission-assignments?role_id={test_role['id']}", headers=headers)
    existing_assignments = existing_response.json()
    assigned_permission_ids = {a["permission_id"]
                               for a in existing_assignments}

    available_permission = None
    for perm in all_permissions:
        if perm["id"] not in assigned_permission_ids:
            available_permission = perm
            break

    assert available_permission is not None, "Need at least one unassigned permission for this test"

    # 1. CREATE - Assign permission to role
    create_payload = {
        "role_id": test_role["id"],
        "permission_id": available_permission["id"]
    }
    create_response = await client.post("/permission-assignments", headers=headers, json=create_payload)
    assert create_response.status_code == 201
    create_data = create_response.json()
    assert create_data["role_id"] == test_role["id"]
    assert create_data["permission_id"] == available_permission["id"]
    assert create_data["success"] is True

    # 2. READ - Verify the assignment exists
    get_response = await client.get(f"/permission-assignments?role_id={test_role['id']}&permission_id={available_permission['id']}", headers=headers)
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data) == 1
    assert get_data[0]["role_id"] == test_role["id"]
    assert get_data[0]["permission_id"] == available_permission["id"]

    # 3. DELETE - Remove the assignment
    delete_payload = {
        "role_id": test_role["id"],
        "permission_id": available_permission["id"]
    }
    headers["Content-Type"] = "application/json"
    delete_response = await client.request("DELETE", "/permission-assignments", headers=headers, json=delete_payload)
    assert delete_response.status_code == 204

    # 4. VERIFY - Confirm the assignment is gone
    verify_response = await client.get(f"/permission-assignments?role_id={test_role['id']}&permission_id={available_permission['id']}", headers=headers)
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert len(verify_data) == 0  # Should be empty now
