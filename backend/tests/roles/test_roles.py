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
    response = await client.get("/roles", headers=headers)
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
        assert isinstance(role["id"], int)
        assert isinstance(role["name"], str)
        assert isinstance(role["description"], str)
        assert isinstance(role["is_active"], bool)
        assert isinstance(role["created_at"], str)
