from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from core.health.service import HealthService
from models.health.response import HealthCheckResponse
from errors import HealthCheckError, HealthCheckDBError
from database.session import get_session

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


@health_router.get("/db/", status_code=200)
async def check_db_status(session: AsyncSession = Depends(get_session)) -> dict:
    result: dict = await health_service.check_db_health(session)
    if not result:
        raise HealthCheckDBError
    return JSONResponse(status_code=200, content=result)
