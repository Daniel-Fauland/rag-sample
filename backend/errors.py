from fastapi import FastAPI
from typing import Callable
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class FastAPIExceptions(Exception):
    """This is the base class for all exceptions in this application
    """
    pass


class HealthCheckError(FastAPIExceptions):
    """An error occurred during the health check
    """
    pass


class FilePathNotFoundError(FastAPIExceptions):
    """A provided filepath was invalid leading to a FilePathNotFoundError
    """
    pass


class InvalidAccessToken(FastAPIExceptions):
    """User has provided an invalid or expired access token
    """
    pass


class InvalidRefreshToken(FastAPIExceptions):
    """User has provided an invalid or expired refresh token
    """
    pass


def create_exception_handler(status_code: int, detail: str) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: FastAPIExceptions):
        return JSONResponse(
            content=detail,
            status_code=status_code
        )
    return exception_handler


def register_errors(app: FastAPI):
    app.add_exception_handler(
        HealthCheckError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "FastAPI CLI is not working properly.",
                    "error_code": "100_health_check_error",
                    "solution": "Make sure FastAPI (CLI) is installed and configured properly."}
        )
    )

    app.add_exception_handler(
        FilePathNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "The file at the provided path was not found.",
                    "error_code": "101_file_not_found_error",
                    "solution": "Make sure you provide a valid file path."}
        )
    )

    app.add_exception_handler(
        InvalidAccessToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Access Token is invalid or expired.",
                    "error_code": "102_invalid_access_token",
                    "solution": "Provide a valid Access Token"}
        )
    )

    app.add_exception_handler(
        InvalidRefreshToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Refresh token is invalid or expired",
                    "error_code": "103_invalid_refresh_token",
                    "solution": "Provide a valid Refresh token"}
        )
    )
