import pytest
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_all_permissions_successful_as_regular_user(client, db_session):
    """Test GET /permissions with regular user (has read:permission:all permission by default)"""
    # Login as regular user - they have read:permission:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/permissions", headers=headers)
    permissions_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(permissions_data, list)
    # There should exist multiple permissions
    assert len(permissions_data) >= 2

    # Check structure of returned permissions (PermissionModelBase - no roles)
    for permission in permissions_data:
        assert "id" in permission
        assert "type" in permission
        assert "resource" in permission
        assert "context" in permission
        assert "description" in permission
        assert "is_active" in permission
        assert "created_at" in permission
        assert isinstance(permission["id"], int)
        assert isinstance(permission["type"], str)
        assert isinstance(permission["resource"], str)
        assert isinstance(permission["context"], str)
        assert isinstance(permission["is_active"], bool)
        assert isinstance(permission["created_at"], str)


@pytest.mark.asyncio
async def test_get_all_permissions_successful_with_query_parameter(client, db_session):
    """Test GET /permissions with query parameters (order_by_field, order_by_direction, limit)"""
    # Login as regular user - they have read:permission:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    order_by_field = "id"
    order_by_direction = "desc"
    limit = 999
    response = await client.get(f"/permissions?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    permissions_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(permissions_data, list)
    # There should exist multiple permissions
    assert len(permissions_data) >= 2
    # Should not exceed the limit
    assert len(permissions_data) <= limit

    # Check whether the records are sorted correctly by id in descending order
    permission_ids = [permission["id"] for permission in permissions_data]
    assert permission_ids == sorted(
        permission_ids, reverse=True), "Permissions should be sorted by id in descending order"

    # Verify structure of returned permissions
    for permission in permissions_data:
        assert "id" in permission
        assert "type" in permission
        assert "resource" in permission
        assert "context" in permission
        assert "description" in permission
        assert "is_active" in permission
        assert "created_at" in permission
        assert isinstance(permission["id"], int)
        assert isinstance(permission["type"], str)
        assert isinstance(permission["resource"], str)
        assert isinstance(permission["context"], str)
        assert isinstance(permission["is_active"], bool)
        assert isinstance(permission["created_at"], str)

    # --- Test ordering by resource ---
    order_by_field = "resource"
    order_by_direction = "asc"
    limit = 999
    response = await client.get(f"/permissions?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    permissions_data = response.json()

    # Verify if permissions are sorted alphabetically by resource in ascending order
    assert response.status_code == 200
    assert isinstance(permissions_data, list)
    assert len(permissions_data) >= 2

    permission_resources = [permission["resource"]
                            for permission in permissions_data]
    assert permission_resources == sorted(
        permission_resources), "Permissions should be sorted by resource in ascending order"

    # --- Test limit ---
    order_by_field = "id"
    order_by_direction = "asc"
    limit = 1
    response = await client.get(f"/permissions?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    permissions_data = response.json()

    # Verify there is only 1 result with the id of '1' (lowest id)
    assert response.status_code == 200
    assert isinstance(permissions_data, list)
    assert len(
        permissions_data) == 1, "Should return exactly 1 permission when limit=1"
    assert permissions_data[0]["id"] == 1, "Should return the permission with id=1 when ordering by id asc with limit=1"


@pytest.mark.asyncio
async def test_get_all_permissions_unsuccessful_with_no_permissions(client, db_session):
    """Test GET /permissions with user that has no permissions (this route requires permission: read:permission:all)"""
    # Login as user without permissions
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Perform GET request with user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:permission:all" in response_data["message"]


@pytest.mark.asyncio
async def test_get_all_permissions_unauthenticated(client):
    """Test GET /permissions with unauthenticated user"""

    # Perform GET request without user access token
    headers = {
        "accept": "application/json"
    }
    response = await client.get("/permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_permission_successful_as_admin(client, db_session):
    """Test POST /permissions with admin user (has all permissions)"""
    # Login as admin user - they have all permissions by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "user1")

    # Perform POST request with admin user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    payload = {
        "type": "read",
        "resource": "test_resource",
        "context": "all",
        "description": "A test permission"
    }
    response = await client.post("/permissions", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 201
    assert "id" in response_data
    assert "type" in response_data
    assert "resource" in response_data
    assert "context" in response_data
    assert "success" in response_data
    assert isinstance(response_data["id"], int)
    assert response_data["type"] == payload["type"]
    assert response_data["resource"] == payload["resource"]
    assert response_data["context"] == payload["context"]
    assert isinstance(response_data["success"], bool)


@pytest.mark.asyncio
async def test_create_permission_insufficient_permissions(client, db_session):
    """Test POST /permissions with normal user (needs permission: create:permission:all)"""
    # Login as regular user - they do not have create:permission:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform POST request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    payload = {
        "type": "read",
        "resource": "test_resource_2",
        "context": "all",
        "description": "A test permission"
    }
    response = await client.post("/permissions", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "create:permission:all" in response_data["message"]


@pytest.mark.asyncio
async def test_create_permission_unauthenticated(client):
    """Test POST /permissions with unauthenticated user"""

    # Perform POST request without user access token
    headers = {
        "accept": "application/json"
    }
    payload = {
        "type": "read",
        "resource": "test_resource_3",
        "context": "all",
        "description": "A test permission"
    }
    response = await client.post("/permissions", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"
