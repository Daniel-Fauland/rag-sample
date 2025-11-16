import pytest
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_all_users_successful_as_regular_user(client, db_session):
    """Test GET /users with regular user (has read:user:all permission by default)"""
    # Login as regular user - they have read:user:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create additional users to ensure there's data to return
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "test_user2@example.com"})
    await test_helper.create_admin_user_if_not_exists(client, db_session, payload={"email": "admin1@example.com"})

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert "limit" in response_data
    assert "offset" in response_data
    assert "total_users" in response_data
    assert "current_users" in response_data

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) >= 2  # At least the users we created

    # Check structure of returned users (UserModelBase - no roles)
    for user in users_data:
        assert "id" in user
        assert "email" in user
        assert "first_name" in user
        assert "last_name" in user
        assert "is_verified" in user
        assert "account_type" in user
        assert "created_at" in user
        assert "modified_at" in user
        # Should NOT include roles (UserModelBase vs UserModel)
        assert "roles" not in user


@pytest.mark.asyncio
async def test_get_all_users_with_permissions_successful_as_regular_user(client, db_session):
    """Test GET /users-with-permissions with regular user (has read:user:all permission)"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create additional users to ensure there's data to return
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "test_user2@example.com"})
    await test_helper.create_admin_user_if_not_exists(client, db_session, payload={"email": "admin1@example.com"})

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert "limit" in response_data
    assert "offset" in response_data
    assert "total_users" in response_data
    assert "current_users" in response_data

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) >= 2  # At least the users we created

    # Check structure of returned users (UserModel with roles)
    for user in users_data:
        assert "id" in user
        assert "email" in user
        assert "first_name" in user
        assert "last_name" in user
        assert "is_verified" in user
        assert "account_type" in user
        assert "created_at" in user
        assert "modified_at" in user
        # Should include roles (UserModel)
        assert "roles" in user
        assert isinstance(user["roles"], list)

        # Check role structure if roles exist
        if user["roles"]:
            for role in user["roles"]:
                assert "id" in role
                assert "name" in role
                assert "is_active" in role
                # Should include permissions in roles
                assert "permissions" in role
                assert isinstance(role["permissions"], list)


@pytest.mark.asyncio
async def test_get_all_users_insufficient_permissions_as_user_without_permissions(client, db_session):
    """Test GET /users fails with user that has no permissions"""
    # Create and login user with no permissions
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Perform GET request with user that has no permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"


@pytest.mark.asyncio
async def test_get_all_users_with_permissions_insufficient_permissions_as_user_without_permissions(client, db_session):
    """Test GET /users-with-permissions fails with user that has no permissions"""
    # Create and login user with no permissions
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "no_permissions", "user1")

    # Perform GET request with user that has no permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "105_insufficient_permissions"


@pytest.mark.asyncio
async def test_get_all_users_successful_as_admin_user(client, db_session):
    """Test GET /users with admin user (has all permissions)"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin_1")

    # Create regular users to ensure there's data to return
    await test_helper.create_user_if_not_exists(client, db_session)

    # Perform GET request with admin access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    response = await client.get("/users", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert "limit" in response_data
    assert "offset" in response_data
    assert "total_users" in response_data
    assert "current_users" in response_data

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) >= 2  # At least admin and regular user

    # Check structure
    for user in users_data:
        assert "id" in user
        assert "email" in user
        assert "first_name" in user
        assert "last_name" in user
        assert "is_verified" in user
        assert "account_type" in user
        # Should NOT include roles (UserModelBase)
        assert "roles" not in user


@pytest.mark.asyncio
async def test_get_all_users_with_ordering_parameters(client, db_session):
    """Test GET /users with query parameters for ordering"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create multiple users to test ordering
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "a_user@example.com"})
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "z_user@example.com"})

    # Test with order_by_field and order_by_direction
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    params = {
        "order_by_field": "id",
        "order_by_direction": "asc"
    }
    response = await client.get("/users", headers=headers, params=params)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) >= 3

    # Verify ordering (ids should be in ascending order)
    ids = [user["id"] for user in users_data]
    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_get_all_users_with_limit_parameter(client, db_session):
    """Test GET /users with limit parameter"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create multiple users to test limit
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser2@example.com"})
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser3@example.com"})
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser4@example.com"})

    # Test with limit parameter
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    params = {
        "limit": 2
    }
    response = await client.get("/users", headers=headers, params=params)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert response_data["limit"] == 2

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) == 2  # Should be limited to 2 users
    assert response_data["current_users"] == 2


@pytest.mark.asyncio
async def test_get_all_users_with_offset_parameter(client, db_session):
    """Test GET /users with offset parameter for pagination"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create multiple users to test pagination
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser2@example.com"})
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser3@example.com"})
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser4@example.com"})

    # Test with offset parameter
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    params = {
        "limit": 2,
        "offset": 1
    }
    response = await client.get("/users", headers=headers, params=params)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert response_data["limit"] == 2
    assert response_data["offset"] == 1

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) == 2  # Should be limited to 2 users
    assert response_data["current_users"] == 2
    # total_users should be >= current_users + offset
    assert response_data["total_users"] >= response_data["current_users"] + \
        response_data["offset"]


@pytest.mark.asyncio
async def test_get_all_users_with_permissions_with_ordering_parameters(client, db_session):
    """Test GET /users-with-permissions with query parameters"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Create additional users
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "testuser2@example.com"})
    await test_helper.create_admin_user_if_not_exists(client, db_session, payload={"email": "admin2@example.com"})

    # Test with query parameters
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    params = {
        "order_by_field": "first_name",
        "order_by_direction": "desc",
        "limit": 10
    }
    response = await client.get("/users-with-permissions", headers=headers, params=params)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert response_data["limit"] == 10

    users_data = response_data["users"]
    assert isinstance(users_data, list)
    assert len(users_data) >= 2

    # All users should have roles included
    for user in users_data:
        assert "roles" in user
        assert isinstance(user["roles"], list)


@pytest.mark.asyncio
async def test_get_all_users_empty_query_parameters(client, db_session):
    """Test GET /users with empty/None query parameters"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    # Test with empty parameters
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    params = {
        "order_by_field": "",
        "order_by_direction": ""
    }
    response = await client.get("/users", headers=headers, params=params)
    response_data = response.json()

    # Assertions - should still work with empty parameters
    assert response.status_code == 200
    assert isinstance(response_data, dict)
    assert "users" in response_data
    assert "limit" in response_data
    assert "offset" in response_data
    assert "total_users" in response_data
    assert "current_users" in response_data


@pytest.mark.asyncio
async def test_get_all_users_with_permissions_admin_user_role_structure(client, db_session):
    """Test that admin user has proper role and permission structure"""
    # Login as admin user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    await test_helper.create_admin_user_if_not_exists(client, db_session, payload={"email": "admin2@example.com"})

    # Get users with permissions
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    response = await client.get("/users-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert isinstance(response_data, dict)
    assert "users" in response_data

    users_data = response_data["users"]
    # Find the admin user we created
    admin_user = None
    for user in users_data:
        if user["email"] == "admin2@example.com":
            admin_user = user
            break

    assert admin_user is not None
    assert "roles" in admin_user
    assert len(admin_user["roles"]) >= 1

    # Check that admin user has admin role
    admin_role = None
    for role in admin_user["roles"]:
        if role["name"] == "admin":
            admin_role = role
            break

    assert admin_role is not None
    assert admin_role["is_active"] is True
    assert "permissions" in admin_role
    assert isinstance(admin_role["permissions"], list)


@pytest.mark.asyncio
async def test_get_all_users_regular_user_role_structure(client, db_session):
    """Test that regular user has proper role structure with read:user:all permission"""
    # Login as regular user
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal", "user1")

    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "test_user2@example.com"})

    # Get users with permissions to see role structure
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert isinstance(response_data, dict)
    assert "users" in response_data

    users_data = response_data["users"]
    # Find the regular user we created
    regular_user = None
    for user in users_data:
        if user["email"] == "test_user2@example.com":
            regular_user = user
            break

    assert regular_user is not None
    assert "roles" in regular_user
    assert len(regular_user["roles"]) >= 1

    # Check that regular user has user role
    user_role = None
    for role in regular_user["roles"]:
        if role["name"] == "user":
            user_role = role
            break

    assert user_role is not None
    assert user_role["is_active"] is True
    assert "permissions" in user_role
    assert isinstance(user_role["permissions"], list)

    # Verify that user role has read:user:all permission
    has_read_user_all = False
    for permission in user_role["permissions"]:
        if (permission["type"] == "read" and
                permission["resource"] == "user" and
                permission["context"] == "all"):
            has_read_user_all = True
            break

    assert has_read_user_all


@pytest.mark.asyncio
async def test_get_all_users_no_permissions_user_structure(client, db_session):
    """Test that user with no permissions has no roles"""
    # First create admin user to be able to see the no-permissions user
    admin_data, _ = await test_helper.login_user_with_type(client, db_session, "admin", "admin1")

    # Create user with no permissions
    await test_helper.create_user_no_permissions(client, db_session, payload={"email": "test_user1_no_permisssions@example.com"})

    # Get users with permissions using admin account
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_data['access_token']}"
    }
    response = await client.get("/users-with-permissions", headers=headers)
    response_data = response.json()

    # Assertions
    assert isinstance(response_data, dict)
    assert "users" in response_data

    users_data = response_data["users"]
    # Find the no-permissions user
    no_perms_user = None
    for user in users_data:
        if user["email"] == "test_user1_no_permisssions@example.com":
            no_perms_user = user
            break

    assert no_perms_user is not None
    assert "roles" in no_perms_user
    # User with no permissions should have empty roles list
    assert len(no_perms_user["roles"]) == 0
