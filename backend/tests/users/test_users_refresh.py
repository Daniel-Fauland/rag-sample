import pytest
from tests.test_helper import TestHelper
from auth.jwt import JWTHandler
from core.user.service import UserService


test_helper = TestHelper()
jwt_handler = JWTHandler()
user_service = UserService()


@pytest.mark.asyncio
async def test_refresh_successful(client, db_session):
    """Test refresh with valid refresh token"""
    data = await test_helper.login_user(client, db_session)

    # Perform GET request with Authorization header using the refresh token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['refresh_token']}"
    }
    response = await client.get("/users/refresh", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"].startswith("ey")
    assert data["refresh_token"].startswith("ey")

    # Validate that old refresh token is invalid after calling refresh route
    response = await client.get("/users/refresh", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "104_invalid_refresh_token"


@pytest.mark.asyncio
async def test_refresh_invalid_refresh_token(client, db_session):
    """Test refresh with invalid refresh token"""
    # Perform GET request with Authorization header using the refresh token
    # fmt: off
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiMDE5OThiYTUtNjUwMS03ZmEyLWE1N2MtNTc0NWJjNWE1NmI5Iiwicm9sZXMiOlt7ImlkIjoyLCJuYW1lIjoidXNlciIsImlzX2FjdGl2ZSI6dHJ1ZX1dfSwiZXhwIjoxNzU4OTg2NDMwLCJqdGkiOiIwMTk5OGJiNS0yZDY1LTczMDEtODdlMS00NzllZjU5ZjQyMDIiLCJyZWZyZXNoIjpmYWxzZX0.WqPAo4VStS2KCTkfXcuRs1ELsujlzHZFCZAz954LTGQ"  # noqa
    }
    # fmt: on
    response = await client.get("/users/refresh", headers=headers)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "104_invalid_refresh_token"
