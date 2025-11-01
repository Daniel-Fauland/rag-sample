import pytest
from tests.test_helper import TestHelper


test_helper = TestHelper()


@pytest.mark.asyncio
async def test_get_all_users_successful_as_regular_user(client, db_session):
    """Test GET /user with regular user (has read:user:all permission by default)"""
    # Login as regular user - they have read:user:all permission by default
    user_data, _ = await test_helper.login_user_with_type(client, db_session, "normal")

    # Create additional users to ensure there's data to return
    await test_helper.create_user_if_not_exists(client, db_session, payload={"email": "test_user2@example.com"})
    await test_helper.create_admin_user_if_not_exists(client, db_session, payload={"email": "admin1@example.com"})

    # Perform GET request with regular user access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}"
    }
    response = await client.get("/users", headers=headers)
    users_data = response.json()

    # Assertions
    assert response.status_code == 200
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
