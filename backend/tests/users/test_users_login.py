import pytest
from tests.test_helper import TestHelper
from auth.jwt import JWTHandler
from core.user.service import UserService


test_helper = TestHelper()
jwt_handler = JWTHandler()
user_service = UserService()


@pytest.mark.asyncio
async def test_login_successful(client, db_session):
    """Test user login with valid credentials"""
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the request payload
    payload = {
        "email": user.email,
        "password": "Strongpassword123-"
    }

    # Perform POST request
    response = await client.post("/users/login", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 201
    assert "message" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"].startswith("ey")
    assert data["refresh_token"].startswith("ey")

    # Validate if the access token is valid
    token_data = await jwt_handler.decode_token(data["access_token"])
    assert "user" in token_data
    assert "exp" in token_data
    assert "jti" in token_data
    assert "refresh" in token_data
    assert "roles" in token_data["user"]
    assert len(token_data["user"]["roles"]) == 1
    assert "id" in token_data["user"]["roles"][0]
    assert "name" in token_data["user"]["roles"][0]
    assert token_data["user"]["roles"][0]["is_active"]
    assert token_data["user"]["id"] == str(user.id)
    assert not token_data["refresh"]

    # Validate if the refresh token is valid
    token_data = await jwt_handler.decode_token(data["refresh_token"])
    assert "user" in token_data
    assert "exp" in token_data
    assert "jti" in token_data
    assert "refresh" in token_data
    assert "roles" not in token_data["user"]
    assert token_data["user"]["id"] == str(user.id)
    assert token_data["refresh"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, db_session):
    """Test user login with invalid credentials"""
    # Define the request payload
    payload = {
        "email": "DoesNotExist@example.com",
        "password": "Strongpassword123-"
    }

    # Perform POST request
    response = await client.post("/users/login", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "109_user_invalid_credentials"


@pytest.mark.asyncio
async def test_login_user_unverified(client, db_session):
    """Test user login with unverified user"""
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Update the user to is_verified: False
    update_data = {
        "is_verified": False
    }
    user = await user_service.update_user_by_email(email=user.email, update_data=update_data, session=db_session)

    # Define the request payload
    payload = {
        "email": user.email,
        "password": "Strongpassword123-"
    }

    # Perform POST request
    response = await client.post("/users/login", json=payload)
    data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in data
    assert "error_code" in data
    assert "solution" in data
    assert data["error_code"] == "110_user_unverified"


@pytest.mark.asyncio
async def test_login_invalid_request(client, db_session):
    """Test user login with invalid request data"""
    user = await test_helper.create_user_if_not_exists(client, db_session)

    # Define the request payload
    payload = {
        "email": "InvalidEmailFormat",
        "password": "Strongpassword123-"
    }

    payload2 = {
        "email": user.email,
        "passw": "Strongpassword123-"
    }

    # Perform POST request
    response = await client.post("/users/login", json=payload)

    # Assertions
    assert response.status_code == 422

    # Perform POST request
    response = await client.post("/users/login", json=payload2)

    # Assertions
    assert response.status_code == 422
