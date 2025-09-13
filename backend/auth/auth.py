from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from auth.jwt import JWTHandler
from errors import InvalidAccessToken, InvalidRefreshToken, InsufficientRoles, InsufficientPermissions
from core.user.service import UserService
from models.user.response import UserModel
from models.auth import Permission
from database.session import get_session
from database.redis import redis_manager

jwt_handler = JWTHandler()
user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """Overwrite the __call__ method to validate the provided token

        Args:
            request (Request): The HTTP request

        Returns:
            HTTPAuthorizationCredentials | None: The Credentials
        """
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = await jwt_handler.decode_token(token)

        # Check if token in Redis blocklist
        redis_client = redis_manager.get_client()
        if token_data is not None and await jwt_handler.jwt_is_blacklisted(token_data=token_data, redis_client=redis_client):
            if token_data.get('refresh'):
                raise InvalidRefreshToken
            else:
                raise InvalidAccessToken

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data is None or token_data['refresh']:
            raise InvalidAccessToken


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data is None or not token_data['refresh']:
            raise InvalidRefreshToken


async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    id = token_details['user']['id']
    user: UserModel = await user_service.get_user_by_id(id=id, session=session, include_roles=True, include_permissions=True)
    return user


class RoleChecker():
    """Check for specific roles. Raise 403 if user does not have any of the allowed roles."""

    def __init__(self, allowed_roles: list[str]) -> None:
        # Always allow 'admin' role
        self.allowed_roles = list(set(allowed_roles + ['admin']))

    def __call__(self, current_user: UserModel = Depends(get_current_user)) -> bool:
        if any(role.name in self.allowed_roles for role in current_user.roles if role.is_active):
            return True
        raise InsufficientRoles(self.allowed_roles)


class PermissionChecker():
    """Check for specific permissions. Raise 403 if user does not have all required permissions."""

    def __init__(self, required_permissions: list[Permission]):
        self.required_permissions = required_permissions

    def _get_user_permissions(self, current_user: UserModel) -> set:
        """Extract user permissions as a set for efficient lookup"""
        user_permissions = set()
        for role in current_user.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:  # Only include active permissions
                        user_permissions.add(
                            (permission.type, permission.resource, permission.context)
                        )
        return user_permissions

    def __call__(self, current_user: UserModel = Depends(get_current_user)) -> bool:
        # Allow every action for admins
        if any(role.name == "admin" and role.is_active for role in current_user.roles):
            return True

        # Get user permissions
        user_permissions = self._get_user_permissions(current_user)

        # Check if user has all required permissions
        missing_permissions = []
        for required_perm in self.required_permissions:
            perm_tuple = (required_perm.type.value,
                          required_perm.resource.value, required_perm.context.value)
            if perm_tuple not in user_permissions:
                missing_permissions.append(
                    f"{required_perm.type.value}:{required_perm.resource.value}:{required_perm.context.value}")
        if missing_permissions:
            raise InsufficientPermissions(missing_permissions)
        return True


def check_ownership_permissions(
    current_user: UserModel,
    target_id: str,
    own_data_permissions: list[Permission],
    other_data_permissions: list[Permission]
) -> bool:
    """
    Check permissions based on whether the user is accessing their own data or others' data.

    Args:
        current_user: The authenticated user making the request
        target_id: The ID/email of the target resource
        own_data_permissions: List of permissions required for accessing own data
        other_data_permissions: List of permissions required for accessing others' data

    Returns:
        bool: True if user has appropriate permissions

    Raises:
        InsufficientPermissions: If user lacks required permissions
    """
    current_user_id = str(current_user.id)
    current_user_email = current_user.email

    # Check if user is trying to access their own data
    is_own_data = target_id in [current_user_id, current_user_email]

    # Apply appropriate permission check
    if is_own_data:
        # User accessing their own data
        checker = PermissionChecker(own_data_permissions)
        return checker(current_user)
    else:
        # User accessing other's data
        checker = PermissionChecker(other_data_permissions)
        return checker(current_user)
