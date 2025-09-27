import pytest
from tests.test_heper import TestHelper
from auth.jwt import JWTHandler
from core.user.service import UserService


test_helper = TestHelper()
jwt_handler = JWTHandler()
user_service = UserService()


@pytest.mark.asyncio
async def test_update_password_successful(client, db_session):
    """Test successful password update and verify it works correctly"""
    # Create user and login
    data = await test_helper.login_user(client, db_session)

    # Get user info for later verification
    token_data = await jwt_handler.decode_token(data['access_token'])
    user_data = token_data.get('user', {})
    user = await user_service.get_user_by_id(id=user_data['id'], session=db_session)
    assert user is not None

    # Update password
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "old_password": "Strongpassword123-",
        "new_password": "NewStrongPassword456!"
    }
    response = await client.post("/user/update-password", headers=headers, json=payload)
    response_data = response.json()

    # Verify password update was successful
    assert response.status_code == 201
    assert "message" in response_data
    assert response_data["message"] == "Password changed successfully"

    # Verify new password works for login
    login_payload = {
        "email": user.email,
        "password": "NewStrongPassword456!"
    }
    login_response = await client.post("/user/login", json=login_payload)
    login_data = login_response.json()

    assert login_response.status_code == 201
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["message"] == "Login successful"

    # Verify old password no longer works
    old_login_payload = {
        "email": user.email,
        "password": "Strongpassword123-"  # Old password
    }
    old_login_response = await client.post("/user/login", json=old_login_payload)
    old_login_data = old_login_response.json()

    assert old_login_response.status_code == 403
    assert "message" in old_login_data
    assert "error_code" in old_login_data
    assert old_login_data["error_code"] == "109_user_invalid_credentials"


@pytest.mark.asyncio
async def test_update_password_incorrect_old_password(client, db_session):
    """Test password update with incorrect old password"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with incorrect old password
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "old_password": "WrongOldPassword123!",
        "new_password": "NewStrongPassword456!"
    }
    response = await client.post("/user/update-password", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 403
    assert "message" in response_data
    assert "error_code" in response_data
    assert "solution" in response_data
    assert response_data["error_code"] == "112_invalid_password"


@pytest.mark.asyncio
async def test_update_password_with_weak_new_password(client, db_session):
    """Test password update with weak new password (validation should fail)"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with weak new password
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "old_password": "Strongpassword123-",
        "new_password": "weak"  # Too short, no uppercase, no numbers
    }
    response = await client.post("/user/update-password", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 422  # Validation error
    assert "detail" in response_data
    # The validation error should mention password requirements


@pytest.mark.asyncio
async def test_update_password_with_empty_old_password(client, db_session):
    """Test password update with empty old password"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with empty old password
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "old_password": "",
        "new_password": "NewStrongPassword456!"
    }
    response = await client.post("/user/update-password", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 422  # Validation error
    assert "detail" in response_data


@pytest.mark.asyncio
async def test_update_password_with_empty_new_password(client, db_session):
    """Test password update with empty new password"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with empty new password
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "old_password": "Strongpassword123-",
        "new_password": ""
    }
    response = await client.post("/user/update-password", headers=headers, json=payload)
    response_data = response.json()

    # Assertions
    assert response.status_code == 422  # Validation error
    assert "detail" in response_data


@pytest.mark.asyncio
async def test_update_password_with_missing_request_body(client, db_session):
    """Test password update with missing request body"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request without request body
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    response = await client.post("/user/update-password", headers=headers)
    response_data = response.json()

    # Assertions
    assert response.status_code == 422  # Validation error
    assert "detail" in response_data


@pytest.mark.asyncio
async def test_update_password_with_same_old_and_new_password(client, db_session):
    """Test password update where new password is same as old password"""
    data = await test_helper.login_user(client, db_session)

    # Perform POST request with same old and new password
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {data['access_token']}"
    }
    payload = {
        "old_password": "Strongpassword123-",
        "new_password": "Strongpassword123-"  # Same as old password
    }
    response = await client.post("/user/update-password", headers=headers, json=payload)
    response_data = response.json()

    # Assertions - This should succeed as there's no business rule preventing same password
    assert response.status_code == 201
    assert "message" in response_data
    assert response_data["message"] == "Password changed successfully"
