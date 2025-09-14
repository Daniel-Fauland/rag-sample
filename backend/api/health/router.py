from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.health.service import HealthService
from models.health.response import HealthCheckResponse, HealthCheckDBResponse
from errors import HealthCheckError, HealthCheckDBError
from database.session import get_session
from config import config

health_router = APIRouter()
health_service = HealthService()

# Rate limiter for health checks
limiter = Limiter(key_func=get_remote_address)


@health_router.get("", status_code=status.HTTP_200_OK, response_model=HealthCheckResponse)
@limiter.limit(f"{config.rate_limit_unprotected_routes}/minute")
async def get_fastapi_version(request: Request) -> dict:
    """Check the FastAPI version <br />

    Raises: <br />
        HealthCheckError: If the FastAPI CLI version can't be retrieved <br />

    Returns: <br />
        dict: The FastAPI version <br />
    """
    result = await health_service.check_FastAPI_version()
    try:
        response = HealthCheckResponse(**result)
    except Exception:
        raise HealthCheckError()
    return response


@health_router.get("-db", status_code=status.HTTP_200_OK, response_model=HealthCheckDBResponse)
@limiter.limit(f"{config.rate_limit_unprotected_routes}/minute")
async def check_db_status(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    """Check if the DB connection is working <br />

    Raises: <br />
        HealthCheckDBError: If the DB can't be reached <br />

    Returns: <br />
        dict: The DB connection status <br />
    """
    result: dict = await health_service.check_db_health(session)
    if not result:
        raise HealthCheckDBError
    return HealthCheckDBResponse(**result)
