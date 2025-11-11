import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check_successful():
    """Test health check successful"""
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "fastapi_version" in data
    assert isinstance(data["fastapi_version"], str)
    assert len(data["fastapi_version"]) > 1


# @pytest.mark.asyncio
# async def test_another_route():
#     """Test another route"""
