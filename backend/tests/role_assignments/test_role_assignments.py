import pytest
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_all_role_assignments_as_admin(client, db_session):
    """Test GET /role-assignments as admin (has all permissions)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "user1")

    # Perform GET request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/role-assignments", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "assignments" in response_data
    assert "limit" in response_data
    assert "offset" in response_data
    assert "total_assignments" in response_data
    assert "current_assignments" in response_data

    assignments = response_data["assignments"]
    assert len(assignments) >= 2
    for assignment in assignments:
        assert "user_id" in assignment
        assert "role_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["user_id"], str)
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["assigned_at"], str)


@pytest.mark.asyncio
async def test_get_all_role_assignments_as_admin_with_query_parameter(client, db_session):
    """Test GET /role-assignments as admin with query parameters(has all permissions)"""
    # Login as admin user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "admin", "user1")

    # Perform GET request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    # - Test sorting -
    user_id = None
    role_id = None
    order_by_field = "role_id"
    order_by_direction = "asc"
    limit = 500
    response = await client.get(f"/role-assignments?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "assignments" in response_data

    assignments = response_data["assignments"]
    assert len(assignments) >= 2
    for assignment in assignments:
        assert "user_id" in assignment
        assert "role_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["user_id"], str)
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["assigned_at"], str)
    role_ids = [assignment["role_id"] for assignment in assignments]
    assert role_ids == sorted(
        role_ids), "role_id values should be sorted in ascending order"

    # - Test filtering -
    user_id = str(user.id)
    role_id = 1
    order_by_field = "role_id"
    order_by_direction = "asc"
    limit = 500
    response = await client.get(f"/role-assignments?user_id={user_id}&role_id={role_id}&order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "assignments" in response_data

    assignments = response_data["assignments"]
    assert len(assignments) == 1
    for assignment in assignments:
        assert "user_id" in assignment
        assert "role_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["user_id"], str)
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["assigned_at"], str)

    # - Test filtering -
    user_id = str(user.id)
    role_id = 12345
    order_by_field = "role_id"
    order_by_direction = "asc"
    limit = 500
    response = await client.get(f"/role-assignments?user_id={user_id}&role_id={role_id}&order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "assignments" in response_data

    assignments = response_data["assignments"]
    assert len(assignments) == 0

    # - Test limits -
    user_id = None
    role_id = None
    order_by_field = "role_id"
    order_by_direction = "asc"
    limit = 1
    response = await client.get(f"/role-assignments?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "assignments" in response_data

    assignments = response_data["assignments"]
    assert len(assignments) == 1
    assert response_data["limit"] == limit
    assert response_data["current_assignments"] == 1
    for assignment in assignments:
        assert "user_id" in assignment
        assert "role_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["user_id"], str)
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["assigned_at"], str)


@pytest.mark.asyncio
async def test_get_all_role_assignments_as_normal_user(client, db_session):
    """Test GET /role-assignments as normal user (requires read:role_assignment:all)"""
    # Login as admin user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with normal user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # - Try to get all role assignments -> This should fail due to insufficient permissions -
    response = await client.get("/role-assignments", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:role_assignment:all" in response_data["message"]


@pytest.mark.asyncio
async def test_get_specific_role_assignments_as_normal_user(client, db_session):
    """Test GET /role-assignments for specific user as normal user (requires read:role_assignment:all or read:role_assignment:me)"""
    # Login as admin user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")
    user_data2, user2 = await test_helper.login_user_with_type(client, db_session, "normal", "user2")

    # Perform GET request with normal user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }

    # - Try to get role assignments for different user -> This should fail due to insufficient permissions -
    user_id = str(user2.id)
    response = await client.get(f"/role-assignments?user_id={user_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:role_assignment:all" in response_data["message"]

    # - Try to get role assignments for own user -> This should work as the normal user has read:role_assignment:me permission -
    user_id = str(user.id)
    response = await client.get(f"/role-assignments?user_id={user_id}", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "assignments" in response_data

    assignments = response_data["assignments"]
    assert len(assignments) == 1
    for assignment in assignments:
        assert "user_id" in assignment
        assert "role_id" in assignment
        assert "assigned_at" in assignment
        assert isinstance(assignment["user_id"], str)
        assert isinstance(assignment["role_id"], int)
        assert isinstance(assignment["assigned_at"], str)


@pytest.mark.asyncio
async def test_create_role_assignment_as_admin(client, db_session):
    """Test POST /role-assignment as admin (has create:role_assignment:all permission)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a regular user to assign a role to
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", unique=True)

    # Perform POST request to assign admin role (role_id=1) to the user
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    payload = {
        "user_id": str(user.id),
        "role_id": 1  # admin role
    }
    response = await client.post("/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 201
    assert "user_id" in response_data
    assert "role_id" in response_data
    assert "success" in response_data
    assert "message" in response_data
    assert response_data["user_id"] == str(user.id)
    assert response_data["role_id"] == 1
    assert response_data["success"] is True
    assert "successfully" in response_data["message"].lower()


@pytest.mark.asyncio
async def test_create_role_assignment_as_normal_user(client, db_session):
    """Test POST /role-assignment as normal user (requires create:role_assignment:all)"""
    # Login as normal user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create another user to try to assign a role to
    user_data2, user2 = await test_helper.login_user_with_type(client, db_session, "normal", "user4")

    # Try to assign a role - should fail due to insufficient permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    payload = {
        "user_id": str(user2.id),
        "role_id": 1
    }
    response = await client.post("/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "create:role_assignment:all" in response_data["message"]


@pytest.mark.asyncio
async def test_create_role_assignment_duplicate(client, db_session):
    """Test POST /role-assignment with duplicate assignment (user already has the role)"""
    # Login as admin user
    admin_data, admin_user = await test_helper.login_user_with_type(client, db_session, "admin", "admin2")

    # Admin already has admin role (role_id=1), try to assign it again
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    payload = {
        "user_id": str(admin_user.id),
        "role_id": 1  # admin role - already assigned
    }
    response = await client.post("/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 409
    assert "error_code" in response_data
    assert response_data["error_code"] == "119_role_assignment_already_exists"


@pytest.mark.asyncio
async def test_create_role_assignment_nonexistent_user(client, db_session):
    """Test POST /role-assignment with nonexistent user ID"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Try to assign role to nonexistent user
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    payload = {
        "user_id": "01234567-89ab-cdef-0123-456789abcdef",  # nonexistent UUID
        "role_id": 2
    }
    response = await client.post("/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert "error_code" in response_data
    assert response_data["error_code"] == "108_user_not_found"


@pytest.mark.asyncio
async def test_create_role_assignment_nonexistent_role(client, db_session):
    """Test POST /role-assignment with nonexistent role ID"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a user to assign role to
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user5")

    # Try to assign nonexistent role
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    payload = {
        "user_id": str(user.id),
        "role_id": 99999  # nonexistent role
    }
    response = await client.post("/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert "error_code" in response_data
    assert response_data["error_code"] == "114_role_not_found"


@pytest.mark.asyncio
async def test_create_role_assignment_unauthenticated(client, db_session):
    """Test POST /role-assignment without authentication"""
    # Create a user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user6")

    # Try to assign role without authentication
    headers = {
        "accept": "application/json"
    }
    payload = {
        "user_id": str(user.id),
        "role_id": 1
    }
    response = await client.post("/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_role_assignment_as_admin(client, db_session):
    """Test DELETE /role-assignment as admin (has delete:role_assignment:all permission)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a user and assign them a role first
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user7")

    # Assign admin role to the user
    create_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    create_payload = {
        "user_id": str(user.id),
        "role_id": 1  # admin role
    }
    create_response = await client.post("/role-assignments", headers=create_headers, json=create_payload)
    assert create_response.status_code == 201

    # Now delete the role assignment
    delete_payload = {
        "user_id": str(user.id),
        "role_id": 1
    }
    create_headers["Content-Type"] = "application/json"
    response = await client.request("DELETE", "/role-assignments", headers=create_headers, json=delete_payload)

    # Assertions
    assert response.status_code == 204

    # Verify the assignment was deleted by trying to get it
    get_response = await client.get(f"/role-assignments?user_id={user.id}&role_id=1", headers=create_headers)
    get_response_data = get_response.json()
    get_data = get_response_data["assignments"]
    assert len(get_data) == 0  # Should be empty now


@pytest.mark.asyncio
async def test_delete_role_assignment_as_normal_user(client, db_session):
    """Test DELETE /role-assignment as normal user (requires delete:role_assignment:all)"""
    # Login as normal user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Try to delete a role assignment - should fail due to insufficient permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": str(user.id),
        "role_id": 2  # user role
    }
    response = await client.request("DELETE", "/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "delete:role_assignment:all" in response_data["message"]


@pytest.mark.asyncio
async def test_delete_role_assignment_nonexistent(client, db_session):
    """Test DELETE /role-assignment with nonexistent assignment"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create a user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user8")

    # Try to delete a role assignment that doesn't exist
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": str(user.id),
        "role_id": 1  # admin role - user doesn't have this
    }
    response = await client.request("DELETE", "/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 404
    assert "error_code" in response_data
    assert response_data["error_code"] == "118_role_assignment_not_found"


@pytest.mark.asyncio
async def test_delete_role_assignment_unauthenticated(client, db_session):
    """Test DELETE /role-assignment without authentication"""
    # Create a user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user9")

    # Try to delete role assignment without authentication
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": str(user.id),
        "role_id": 2
    }
    response = await client.request("DELETE", "/role-assignments", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_role_assignment_crud_lifecycle(client, db_session):
    """Test complete CRUD lifecycle for role assignments"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin3")

    # Create a test user
    user_data, user = await test_helper.login_user_with_type(client, db_session, "normal", "user10")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }

    # 1. CREATE - Assign admin role to user
    create_payload = {
        "user_id": str(user.id),
        "role_id": 1  # admin role
    }
    create_response = await client.post("/role-assignments", headers=headers, json=create_payload)
    assert create_response.status_code == 201
    create_data = create_response.json()
    assert create_data["user_id"] == str(user.id)
    assert create_data["role_id"] == 1
    assert create_data["success"] is True

    # 2. READ - Verify the assignment exists
    get_response = await client.get(f"/role-assignments?user_id={user.id}&role_id=1", headers=headers)
    assert get_response.status_code == 200
    get_response_data = get_response.json()
    assert isinstance(get_response_data, dict)
    assert "assignments" in get_response_data
    get_data = get_response_data["assignments"]
    assert len(get_data) == 1
    assert get_data[0]["user_id"] == str(user.id)
    assert get_data[0]["role_id"] == 1

    # 3. DELETE - Remove the assignment
    delete_payload = {
        "user_id": str(user.id),
        "role_id": 1
    }
    headers["Content-Type"] = "application/json"
    delete_response = await client.request("DELETE", "/role-assignments", headers=headers, json=delete_payload)
    assert delete_response.status_code == 204

    # 4. VERIFY - Confirm the assignment is gone
    verify_response = await client.get(f"/role-assignments?user_id={user.id}&role_id=1", headers=headers)
    assert verify_response.status_code == 200
    verify_response_data = verify_response.json()
    assert isinstance(verify_response_data, dict)
    assert "assignments" in verify_response_data
    verify_data = verify_response_data["assignments"]
    assert len(verify_data) == 0  # Should be empty now
