
import anyio.to_thread
from config import config
from utils.helper import color
from utils.logging import logger
from database.session import get_session_direct
from database.redis import redis_manager
from core.health.service import HealthService
health_service = HealthService()


class LifeSpanService():
    @staticmethod
    async def life_span_pre_checks():
        logger.info(f"{await color("SYSTEM")}:   Server is starting...")
        limiter = anyio.to_thread.current_default_thread_limiter()
        limiter.total_tokens = config.thread_pool
        logger.debug(f"Thread pool size is: {await color(limiter.total_tokens)}")
        logger.debug(f"Number of workers are: {await color(config.workers)}")
        health_check = await health_service.check_FastAPI_version()
        logger.debug(health_check)

        # Get a database session directly for startup health check
        db_session = await get_session_direct()
        try:
            health_check_db = await health_service.check_db_health(db_session)
            if health_check_db:
                logger.debug(health_check_db)
        finally:
            # Always close the session to prevent resource leaks
            await db_session.close()

        # Initialize Redis connection
        await redis_manager.connect()
        logger.debug("Redis connection pool initialized")

        # Test Redis connection
        try:
            client = redis_manager.get_client()
            await client.ping()
            logger.debug("Redis health check passed")
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")

    @staticmethod
    async def life_span_post_checks():
        logger.info(f"{await color("SYSTEM")}:   Server is stopping...")

        # Close Redis connections
        await redis_manager.disconnect()
        logger.debug("Redis connection pool closed")
