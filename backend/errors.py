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
    """An error occurred during the fastapi cli health check
    """
    pass


class HealthCheckDBError(FastAPIExceptions):
    """An error occurred during the database health check
    """
    pass


class XValueError(FastAPIExceptions):
    """One or more wrong provided arguments led to a ValueError
    """

    def __init__(self, message: str = None):
        if message is not None:
            self.message = f"{message}"
        super().__init__(self.message)


class InvalidAccessToken(FastAPIExceptions):
    """User has provided an invalid or expired access token
    """
    pass


class InvalidRefreshToken(FastAPIExceptions):
    """User has provided an invalid or expired refresh token
    """
    pass


class InsufficientPermissions(FastAPIExceptions):
    """User does not have the necessary permissions to perform this action
    """

    def __init__(self, message: str = None):
        if message is not None:
            self.message = f"Missing permission(s): {message}"
        super().__init__(self.message)


class InsufficientRoles(FastAPIExceptions):
    """User does not have the necessary role to perform this action
    """

    def __init__(self, message: str = None):
        if message is not None:
            self.message = f"Any one of these roles is needed: {message}"
        super().__init__(self.message)


class UserEmailExists(FastAPIExceptions):
    """The user email already exists in the database"""
    pass


class UserNotFound(FastAPIExceptions):
    """The provided email or id does not exist in the database"""
    pass


class RoleNotFound(FastAPIExceptions):
    """The provided role id does not exist in the database"""
    pass


class RoleAlreadyExists(FastAPIExceptions):
    """A role with this name already exists in the database"""
    pass


class PermissionNotFound(FastAPIExceptions):
    """The provided permission id does not exist in the database"""
    pass


class PermissionAlreadyExists(FastAPIExceptions):
    """A permission with this type, resource, and context combination already exists in the database"""
    pass


class RoleAssignmentNotFound(FastAPIExceptions):
    """The specified role assignment does not exist in the database"""
    pass


class RoleAssignmentAlreadyExists(FastAPIExceptions):
    """A role assignment already exists for this user and role combination"""
    pass


class UserInvalidCredentials(FastAPIExceptions):
    """The provided email/password combination does not not match any database entries"""
    pass


class UserNotVerified(FastAPIExceptions):
    """The user account is not verified"""
    pass


class InvalidUUID(FastAPIExceptions):
    """The provided uuid is not a valid"""

    def __init__(self, message: str = None):
        if message is not None:
            self.message = f"Invalid UUID: {message}"
        super().__init__(self.message)


class UserInvalidPassword(FastAPIExceptions):
    """The provided password does not match the users password"""


class InternalServerError(FastAPIExceptions):
    """An internal server error occured"""

    def __init__(self, message: str = None):
        if message is not None:
            self.message = f"An internal server error occured at method: {message}"
        super().__init__(self.message)


def create_exception_handler(status_code: int, detail: str) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: FastAPIExceptions):
        # Use dynamic message if available, otherwise use the static detail
        if hasattr(exc, 'message') and exc.message:
            # For exceptions with dynamic messages, update the detail
            if isinstance(detail, dict) and 'message' in detail:
                content = detail.copy()
                content['message'] = exc.message
            else:
                content = detail
        else:
            content = detail

        return JSONResponse(
            content=content,
            status_code=status_code
        )
    return exception_handler


def register_errors(app: FastAPI):
    app.add_exception_handler(
        HealthCheckError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "FastAPI CLI is not working properly.",
                    "error_code": "100_health_check_fastapi_cli_error",
                    "solution": "Make sure FastAPI (CLI) is installed and configured properly."}
        )
    )

    app.add_exception_handler(
        HealthCheckDBError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Database connection could not be established properly",
                    "error_code": "101_health_check_db_error",
                    "solution": "Make sure the database is running, you provide valid credentials & there are no ip/firewall restrictions that block the connection"}
        )
    )

    app.add_exception_handler(
        XValueError,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "ValueError due to one or more wrong arguments",
                    "error_code": "102_value_error",
                    "solution": "Make sure you provide valid arguments to the api."}
        )
    )

    app.add_exception_handler(
        InvalidAccessToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Access Token is invalid or expired.",
                    "error_code": "103_invalid_access_token",
                    "solution": "Provide a valid Access Token"}
        )
    )

    app.add_exception_handler(
        InvalidRefreshToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Refresh token is invalid or expired",
                    "error_code": "104_invalid_refresh_token",
                    "solution": "Provide a valid Refresh token"}
        )
    )

    app.add_exception_handler(
        InsufficientPermissions,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "User does not have the necessary permissions to perform this action",
                    "error_code": "105_insufficient_permissions",
                    "solution": "Contact your administrator for assistance"}
        )
    )

    app.add_exception_handler(
        InsufficientRoles,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "User does not have the necessary role to perform this action",
                    "error_code": "106_insufficient_roles",
                    "solution": "Contact your administrator for assistance"}
        )
    )

    app.add_exception_handler(
        UserEmailExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "User email already exists in the db",
                    "error_code": "107_user_email_exists",
                    "solution": "Use a different email address"}
        )
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "The email or id provided does not exist in the database",
                    "error_code": "108_user_not_found",
                    "solution": "Provide a valid email or id"}
        )
    )

    app.add_exception_handler(
        UserInvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "The provided email/password combination does not not match any database entries",
                    "error_code": "109_user_invalid_credentials",
                    "solution": "Provide valid user credentials"}
        )
    )

    app.add_exception_handler(
        UserNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "The user is not verified",
                    "error_code": "110_user_unverified",
                    "solution": "Contact your administrator for assistance"}
        )
    )

    app.add_exception_handler(
        InvalidUUID,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "The provided uuid is not valid",
                    "error_code": "111_invalid_uuid",
                    "solution": "Provide a valid UUID"}
        )
    )

    app.add_exception_handler(
        UserInvalidPassword,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "The provided password does not match the users password",
                    "error_code": "112_invalid_password",
                    "solution": "Provide the correct user password"}
        )
    )

    app.add_exception_handler(
        InternalServerError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "An internal server error occured",
                    "error_code": "113_internal_server_error",
                    "solution": "Contact the administrator for assistance"}
        )
    )

    app.add_exception_handler(
        RoleNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "The role id provided does not exist in the database",
                    "error_code": "114_role_not_found",
                    "solution": "Provide a valid role id"}
        )
    )

    app.add_exception_handler(
        RoleAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "A role with this name already exists in the database",
                    "error_code": "115_role_already_exists",
                    "solution": "Use a different role name"}
        )
    )

    app.add_exception_handler(
        PermissionNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "The permission id provided does not exist in the database",
                    "error_code": "116_permission_not_found",
                    "solution": "Provide a valid permission id"}
        )
    )

    app.add_exception_handler(
        PermissionAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "A permission with this type, resource, and context combination already exists",
                    "error_code": "117_permission_already_exists",
                    "solution": "Use a different combination of type, resource, and context"}
        )
    )

    app.add_exception_handler(
        RoleAssignmentNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "The specified role assignment does not exist",
                    "error_code": "118_role_assignment_not_found",
                    "solution": "Provide a valid user ID and role ID combination"}
        )
    )

    app.add_exception_handler(
        RoleAssignmentAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "A role assignment already exists for this user and role combination",
                    "error_code": "119_role_assignment_already_exists",
                    "solution": "The user already has this role assigned"}
        )
    )
