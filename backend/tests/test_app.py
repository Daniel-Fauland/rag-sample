import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from main import app
from config import config


@pytest.mark.asyncio
async def test_root_route():
    # Use ASGITransport explicitly
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Perform GET request
        response = await client.get("/")
        data = response.json()
        assert response.status_code == 200
        assert "Message" in data
        assert data["Message"] == config.fastapi_welcome_msg
