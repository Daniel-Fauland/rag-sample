import pytest
from tests.test_helper import TestHelper
from auth.jwt import JWTHandler
from core.user.service import UserService


test_helper = TestHelper()
jwt_handler = JWTHandler()
user_service = UserService()


@pytest.mark.asyncio
async def test_me_successful_with_valid_access_token(client, db_session):
    """Test /user/me with valid access token"""
    data, _ = await test_helper.login_user_with_type(client, db_session, user_type="normal", unique=True)

    # Perform GET request with Authorization header using the access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    response = await client.get("/users/me", headers=headers)
    user_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "id" in user_data
    assert "email" in user_data
    assert "first_name" in user_data
    assert "last_name" in user_data
    assert "is_verified" in user_data
    assert "account_type" in user_data
    assert "roles" in user_data
    assert user_data["email"].endswith("@example.com")
    assert user_data["first_name"] == "Test"
    assert user_data["last_name"] == "User"
    assert user_data["is_verified"] is True
    assert isinstance(user_data["roles"], list)


@pytest.mark.asyncio
async def test_me_with_invalid_access_token(client, db_session):
    """Test /user/me with invalid access token"""
    # Perform GET request with Authorization header using an invalid access token
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer invalid_token_here"
    }
    response = await client.get("/users/me", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "103_invalid_access_token"


@pytest.mark.asyncio
async def test_me_with_expired_access_token(client, db_session):
    """Test /user/me with expired access token"""
    # Perform GET request with Authorization header using an expired access token
    # fmt: off
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiMDE5OThiYTUtNjUwMS03ZmEyLWE1N2MtNTc0NWJjNWE1NmI5Iiwicm9sZXMiOlt7ImlkIjoyLCJuYW1lIjoidXNlciIsImlzX2FjdGl2ZSI6dHJ1ZX1dfSwiZXhwIjoxNzU4OTg2NDMwLCJqdGkiOiIwMTk5OGJiNS0yZDY1LTczMDEtODdlMS00NzllZjU5ZjQyMDIiLCJyZWZyZXNoIjpmYWxzZX0.WqPAo4VStS2KCTkfXcuRs1ELsujlzHZFCZAz954LTGQ"  # noqa
    }
    # fmt: on
    response = await client.get("/users/me", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "103_invalid_access_token"


@pytest.mark.asyncio
async def test_me_with_refresh_token_instead_of_access_token(client, db_session):
    """Test /user/me with refresh token instead of access token"""
    data, _ = await test_helper.login_user_with_type(client, db_session, user_type="normal", unique=True)

    # Perform GET request with Authorization header using the refresh token (should fail)
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['refresh_token']}"
    }
    response = await client.get("/users/me", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "103_invalid_access_token"


@pytest.mark.asyncio
async def test_me_without_authorization_header(client, db_session):
    """Test /user/me without Authorization header"""
    # Perform GET request without Authorization header
    headers = {
        "accept": "application/json"
    }
    response = await client.get("/users/me", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in data
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_me_with_malformed_authorization_header(client, db_session):
    """Test /user/me with malformed Authorization header"""
    data, _ = await test_helper.login_user_with_type(client, db_session, user_type="normal", unique=True)

    # Test with malformed Authorization header (missing "Bearer" prefix)
    headers = {
        "accept": "application/json",
        "Authorization": data['access_token']  # Missing "Bearer" prefix
    }
    response = await client.get("/users/me", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "detail" in data
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_me_user_roles_structure(client, db_session):
    """Test that /user/me returns proper role structure"""
    data, _ = await test_helper.login_user_with_type(client, db_session, user_type="normal", unique=True)

    # Perform GET request with Authorization header using the access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    response = await client.get("/users/me", headers=headers)
    user_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "roles" in user_data
    assert isinstance(user_data["roles"], list)

    # Check that roles have the expected structure if any exist
    if user_data["roles"]:
        for role in user_data["roles"]:
            assert "id" in role
            assert "name" in role
            assert "is_active" in role
            assert isinstance(role["id"], int)
            assert isinstance(role["name"], str)
            assert isinstance(role["is_active"], bool)
