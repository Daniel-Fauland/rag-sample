from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.health.service import HealthService
from models.health.response import HealthCheckResponse
from errors import HealthCheckError, HealthCheckDBError
from database.session import get_session

health_router = APIRouter()
health_service = HealthService()

# Rate limiter for health checks
limiter = Limiter(key_func=get_remote_address)


@health_router.get("", response_model=HealthCheckResponse)
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def get_fastapi_version(request: Request) -> dict:
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


@health_router.get("/db", status_code=200)
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def check_db_status(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    result: dict = await health_service.check_db_health(session)
    if not result:
        raise HealthCheckDBError
    return JSONResponse(status_code=200, content=result)
