import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from core.test.service import TestService

service = TestService()


@pytest.mark.asyncio
async def test_check_string_conversion_invalid_input():
    """Test string conversion with invalid input"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "xyz"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_check_string_conversion_empty_string():
    """Test string conversion with an empty string"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = ""
        payload_conversion_type = "kebab-case"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == ""


@pytest.mark.asyncio
async def test_check_string_conversion_lower_successful():
    """Test string conversion lower successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "lower"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == await service.convert_string(message=payload_msg, conversion_type=payload_conversion_type)


@pytest.mark.asyncio
async def test_check_string_conversion_upper_successful():
    """Test string conversion upper successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "upper"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == await service.convert_string(message=payload_msg, conversion_type=payload_conversion_type)


@pytest.mark.asyncio
async def test_check_string_conversion_camelcase_successful():
    """Test string conversion camelCase successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "camelCase"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == await service.convert_string(message=payload_msg, conversion_type=payload_conversion_type)


@pytest.mark.asyncio
async def test_check_string_conversion_pascalcase_successful():
    """Test string conversion PascalCase successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "PascalCase"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == await service.convert_string(message=payload_msg, conversion_type=payload_conversion_type)


@pytest.mark.asyncio
async def test_check_string_conversion_snakecase_successful():
    """Test string conversion snake_case successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "snake_case"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == await service.convert_string(message=payload_msg, conversion_type=payload_conversion_type)


@pytest.mark.asyncio
async def test_check_string_conversion_kebabcase_successful():
    """Test string conversion kebab-case successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Define the request payload
        payload_msg = "This is an example for testing purposes."
        payload_conversion_type = "kebab-case"
        payload = {
            "message": payload_msg,
            "conversion_type": payload_conversion_type,
        }
        # Perform POST request
        response = await client.post("/test", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "conversion_type" in data
    assert data["conversion_type"].lower() == payload_conversion_type.lower()
    assert data["message"] == await service.convert_string(message=payload_msg, conversion_type=payload_conversion_type)
