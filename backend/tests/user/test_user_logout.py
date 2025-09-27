import pytest
from tests.test_heper import TestHelper
from auth.jwt import JWTHandler
from core.user.service import UserService


test_helper = TestHelper()
jwt_handler = JWTHandler()
user_service = UserService()


@pytest.mark.asyncio
async def test_logout_successful_access_token(client, db_session):
    """Test logout with valid access token"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with Authorization header using the access token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {}
    response = await client.post("/user/logout", headers=headers, json=payload)

    # Assertions
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_successful_access_refresh_token(client, db_session):
    """Test logout with valid access & refresh token"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with Authorization header using the access token & payload including the refresh token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "refresh_token": data['refresh_token']
    }
    response = await client.post("/user/logout", headers=headers, json=payload)

    # Assertions
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_expired_token(client, db_session):
    """Test refresh with an expired token"""
    # Perform POST request with Authorization header using an expired access token
    # fmt: off
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiMDE5OThiYTUtNjUwMS03ZmEyLWE1N2MtNTc0NWJjNWE1NmI5Iiwicm9sZXMiOlt7ImlkIjoyLCJuYW1lIjoidXNlciIsImlzX2FjdGl2ZSI6dHJ1ZX1dfSwiZXhwIjoxNzU4OTg2NDMwLCJqdGkiOiIwMTk5OGJiNS0yZDY1LTczMDEtODdlMS00NzllZjU5ZjQyMDIiLCJyZWZyZXNoIjpmYWxzZX0.WqPAo4VStS2KCTkfXcuRs1ELsujlzHZFCZAz954LTGQ"  # noqa
    }
    # fmt: on
    payload = {}
    response = await client.post("/user/logout", headers=headers, json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "103_invalid_access_token"
