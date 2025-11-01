import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from middleware import register_middleware
from errors import register_errors
from config import config, Settings
from utils.logging import logger
from utils.life_span import LifeSpanService
from api.test.router import test_router
from api.user.router import user_router
from api.role.router import role_router
from api.permission.router import permission_router
from api.role_assignment.router import role_assignment_router
from api.permission_assignment.router import permission_assignment_router
from api.health.router import health_router


life_span_service = LifeSpanService()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def life_span(app: FastAPI):
    """A context manager for the lifespan of the FastAPI app.

    Args:
        app (FastAPI): The FastAPI app instance.
    """
    await life_span_service.life_span_pre_checks()
    yield
    await life_span_service.life_span_post_checks()

# FastAPI App instance
app = FastAPI(
    version=config.backend_version,
    lifespan=life_span,
    title=f"{config.fastapi_project_name} - Backend API",
    description=f"""This is the swagger documentation for the {config.fastapi_project_name} backend server.
    """,
)

# Add rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup middleware
register_middleware(app)

# Setup error handlers
register_errors(app)

# Include routers
app.include_router(test_router, tags=["Test"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(role_router, prefix="/roles", tags=["Roles"])
app.include_router(permission_router, prefix="/permission",
                   tags=["Permission"])
app.include_router(role_assignment_router,
                   prefix="/role-assignment", tags=["Role Assignment"])
app.include_router(permission_assignment_router,
                   prefix="/permission-assignment", tags=["Permission Assignment"])
app.include_router(health_router, prefix="/health", tags=["Health"])


@app.get("/", status_code=200)
def read_root():
    return {
        "Message": config.fastapi_welcome_msg
    }


if __name__ == "__main__":
    logger.debug(
        f"Successfully read the config with the following fields: {list(Settings.model_fields.keys())}")
    logger.debug(f"IS_DOCKER = {config.is_docker}")
    logger.debug(f"IS_LOCAL = {config.is_local}")

    if config.is_docker:
        logger.info("Runnning using docker.")
        uvicorn.run("main:app", host="0.0.0.0", port=config.fastapi_port, workers=config.workers,
                    log_level="info")
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=config.fastapi_port,
                    log_level="info", reload=True)
