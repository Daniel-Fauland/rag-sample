import subprocess
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
