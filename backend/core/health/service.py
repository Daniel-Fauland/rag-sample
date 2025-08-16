import subprocess
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from utils.logging import logger
from utils.helper import Utils
from errors import HealthCheckError


class HealthService:
    async def check_FastAPI_version(self) -> dict:
        """Internal function to check the FastAPI CLI version.

        Returns:
            dict: A dictionary containing the FastAPI CLI version.

        Raises:
            HTTPException: If there's an error checking the CLI version.
        """
        command = "fastapi --version"
        try:
            FastAPI_version = await Utils.run_command(command)
            return {"status": "healthy", "fastapi_version": FastAPI_version}
        except subprocess.CalledProcessError as e:
            logger.error(
                "Error checking FastAPI CLI version in health check: %s",
                e.stderr.decode().strip(),
            )
            raise HealthCheckError()

    async def check_db_health(self, session: AsyncSession) -> dict:
        """Check if the db connection works by querying the active database and user

        Args:
            session (AsyncSession): The async database session

        Returns:
            dict: The query result
        """
        try:
            statement = text(
                "SELECT current_database() as database, current_user as user;")
            db_result = await session.exec(statement)

            # Get the first row - session.exec() returns a Result object
            row = db_result.first()
            return {"result": "success",
                    "current_database": row.database,
                    "current_user": row.user}
        except Exception as e:
            logger.error(f"Error checking the current database & user: {e}")
            return None
