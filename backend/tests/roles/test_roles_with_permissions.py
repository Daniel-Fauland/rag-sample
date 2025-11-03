import pytest
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_all_roles_successful_as_regular_user(client, db_session):
    """Test GET /roles with regular user (has read:role:all permission by default)"""
    # Login as regular user - they have read:role:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/roles-with-permissions", headers=headers)
    roles_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(roles_data, list)
    # There should exist at least 2 roles: [admin, user]
    assert len(roles_data) >= 2

    # Check structure of returned users (UserModelBase - no roles)
    for role in roles_data:
        assert "id" in role
        assert "name" in role
        assert "description" in role
        assert "is_active" in role
        assert "created_at" in role
        assert "permissions" in role
        assert isinstance(role["id"], int)
        assert isinstance(role["name"], str)
        assert isinstance(role["description"], str)
        assert isinstance(role["is_active"], bool)
        assert isinstance(role["created_at"], str)
        assert isinstance(role["permissions"], list)
        for permission in role["permissions"]:
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
            assert isinstance(permission["description"], str)
            assert isinstance(permission["is_active"], bool)
            assert isinstance(permission["created_at"], str)


@pytest.mark.asyncio
async def test_get_all_roles_successful_with_query_parameter(client, db_session):
    """Test GET /roles with query parameters (order_by_field, order_by_direction, limit)"""
    # Login as regular user - they have read:role:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    order_by_field = "id"
    order_by_direction = "desc"
    limit = 999
    response = await client.get(f"/roles-with-permissions?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    roles_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(roles_data, list)
    # There should exist at least 2 roles: [admin, user]
    assert len(roles_data) >= 2
    # Should not exceed the limit
    assert len(roles_data) <= limit

    # Check whether the records are sorted correctly by id in descending order
    role_ids = [role["id"] for role in roles_data]
    assert role_ids == sorted(
        role_ids, reverse=True), "Roles should be sorted by id in descending order"

    # Verify structure of returned roles
    for role in roles_data:
        assert "id" in role
        assert "name" in role
        assert "description" in role
        assert "is_active" in role
        assert "created_at" in role
        assert "permissions" in role
        assert isinstance(role["id"], int)
        assert isinstance(role["name"], str)
        assert isinstance(role["description"], str)
        assert isinstance(role["is_active"], bool)
        assert isinstance(role["created_at"], str)
        assert isinstance(role["permissions"], list)
        for permission in role["permissions"]:
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
            assert isinstance(permission["description"], str)
            assert isinstance(permission["is_active"], bool)
            assert isinstance(permission["created_at"], str)

    # --- Test ordering by name ---
    order_by_field = "name"
    order_by_direction = "asc"
    limit = 999
    response = await client.get(f"/roles?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    roles_data = response.json()

    # Verify if roles are sorted alphabetically by name in ascending order
    assert response.status_code == 200
    assert isinstance(roles_data, list)
    assert len(roles_data) >= 2

    # Verify ordering is consistent (PostgreSQL ORDER BY may differ from Python sorted())
    # Check that consecutive pairs are in correct order
    role_names = [role["name"] for role in roles_data]
    for i in range(len(role_names) - 1):
        # In ascending order, each name should be <= the next
        # Note: We can't use Python's sorted() as PostgreSQL collation may differ
        assert role_names[i].lower() <= role_names[i + 1].lower(), \
            f"Roles should be sorted by name in ascending order, but '{role_names[i]}' comes after '{role_names[i + 1]}'"

    # Verify 'admin' comes before 'user' alphabetically
    admin_index = next((i for i, role in enumerate(
        roles_data) if role["name"] == "admin"), None)
    user_index = next((i for i, role in enumerate(
        roles_data) if role["name"] == "user"), None)
    if admin_index is not None and user_index is not None:
        assert admin_index < user_index, "'admin' role should come before 'user' role when sorted by name ascending"

    # --- Test limit ---
    order_by_field = "id"
    order_by_direction = "asc"
    limit = 1
    response = await client.get(f"/roles?order_by_field={order_by_field}&order_by_direction={order_by_direction}&limit={limit}", headers=headers)
    roles_data = response.json()

    # Verify there is only 1 result with the id of '1' (lowest id)
    assert response.status_code == 200
    assert isinstance(roles_data, list)
    assert len(roles_data) == 1, "Should return exactly 1 role when limit=1"
    assert roles_data[0]["id"] == 1, "Should return the role with id=1 when ordering by id asc with limit=1"


@pytest.mark.asyncio
async def test_get_all_roles_unsuccessful_with_no_permissions(client, db_session):
    """Test GET /roles with user that has no permissions (this route requires permission: read:role:all)"""
    # Login as regular user - they have read:role:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Perform GET request with user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/roles-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"
    assert "read:role:all" in response_data["message"]


@pytest.mark.asyncio
async def test_get_all_roles_unauthenticated(client):
    """Test GET /roles with unauthenticated user"""

    # Perform GET request without user access token
    headers = {
        "accept": "application/json"
    }
    response = await client.get("/roles-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in response_data
    assert response_data["detail"] == "Not authenticated"
