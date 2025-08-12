from fastapi import APIRouter
from core.health.service import HealthService
from models.health.response import HealthCheckResponse
from errors import HealthCheckError

health_router = APIRouter()
health_service = HealthService()


@health_router.get("/", response_model=HealthCheckResponse)
async def get_fastapi_version() -> dict:
    """Check the FastAPI version

    Returns:
        dict: The FastAPI version
    """
    result = await health_service.check_FastAPI_version()
    try:
        response = HealthCheckResponse(**result)
    except Exception:
        raise HealthCheckError()
    return response
