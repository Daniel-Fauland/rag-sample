import uuid
from fastapi import APIRouter, Depends, Request, status, Query, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.user.service import UserService
from utils.user import UserHelper
from auth.jwt import JWTHandler
from auth.auth import get_current_user, check_ownership_permissions
from models.user.request import SignupRequest, BatchSignupRequest, BatchDeleteRequest, BatchUserUpdateRequest, LoginRequest, LogoutRequest, UserUpdateRequest, PasswordUpdateRequest
from models.user.response import SignupResponse, BatchSignupResponse, BatchUpdateResponse, SigninResponse, RefreshResponse, UserModel, PasswordUpdateResponse, ListUserResponse, ListUserWithPermissionsResponse
from models.auth import Permission, Type, Context
from auth.auth import PermissionChecker
from errors import UserEmailExists, UserInvalidCredentials, UserNotFound, UserNotVerified, InvalidRefreshToken, InvalidUUID, XValueError
from auth.auth import AccessTokenBearer, RefreshTokenBearer
from database.session import get_session
from database.redis import redis_manager
from config import config


user_router = APIRouter()
service = UserService()
user_helper = UserHelper()
jwt_handler = JWTHandler()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()

# Rate limiter for user endpoints
limiter = Limiter(key_func=get_remote_address)

# Permissions
resource = "user"
read_user_me = PermissionChecker(
    [Permission(type=Type.read, resource=resource, context=Context.me)])
read_user_all = PermissionChecker(
    [Permission(type=Type.read, resource=resource, context=Context.all)])
create_user_all = PermissionChecker(
    [Permission(type=Type.create, resource=resource, context=Context.all)]
)
update_user_all = PermissionChecker(
    [Permission(type=Type.update, resource=resource, context=Context.all)]
)
delete_user_all = PermissionChecker(
    [Permission(type=Type.delete, resource=resource, context=Context.all)]
)


@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
@limiter.limit(f"{config.rate_limit_unprotected_routes}/minute")
async def signup(request: Request, user_data: SignupRequest, session: AsyncSession = Depends(get_session)):
    """Create a new user in the database <br />

    Args: <br />
        user_data (SignupRequest): The user to sign up <br />

    Returns: <br />
        SignupResponse: The users email and a success flag <br />
    """
    email = user_data.email
    user_exists = await service.user_exists(email=email, session=session)
    if user_exists:
        raise UserEmailExists()

    new_user = await service.create_user(user_data, session)
    return SignupResponse(email=new_user.email, success=True)


@user_router.post("/batch-signup", status_code=status.HTTP_201_CREATED, response_model=BatchSignupResponse)
async def batch_signup(user_data: BatchSignupRequest, session: AsyncSession = Depends(get_session), _: bool = Depends(create_user_all)):
    """Create new users in the database <br />

    Args: <br />
        user_data (BatchSignupRequest): The users to sign up <br />

    Returns: <br />
        BatchSignupResponse: A list of users email, success flag & the reason for failed signup <br />
    """
    results = await service.create_users(user_data, session)
    return BatchSignupResponse(result=results)


@user_router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete(delete_data: BatchDeleteRequest,
                       session: AsyncSession = Depends(get_session),
                       _: bool = Depends(delete_user_all)):
    """Delete multiple users from the database by their emails or UUIDs <br />

    Args: <br />
        delete_data (BatchDeleteRequest): List of user identifiers (emails or UUIDs) to delete <br />

    Returns: <br />
        204 No Content: Users successfully deleted (or didn't exist) <br />

    Note: <br />
        This endpoint does not return an error if a user doesn't exist. <br />
        It silently ignores non-existent users and invalid UUIDs. <br />
    """
    await service.delete_users(delete_data, session)


@user_router.post("/batch-edit", status_code=status.HTTP_200_OK, response_model=BatchUpdateResponse)
async def batch_edit(update_data: BatchUserUpdateRequest,
                     session: AsyncSession = Depends(get_session),
                     _: bool = Depends(update_user_all)):
    """Update multiple users in the database by their emails or UUIDs <br />

    Args: <br />
        update_data (BatchUserUpdateRequest): List of users with their identifiers and fields to update <br />

    Returns: <br />
        BatchUpdateResponse: A list of results for each user with identifier, success flag, and reason <br />

    Note: <br />
        - Supports partial updates (only provided fields will be updated) <br />
        - Each user can have different fields updated <br />
        - Returns detailed status for each user in the batch <br />
    """
    results = await service.update_users(update_data, session)
    return BatchUpdateResponse(result=results)


@user_router.post("/login", status_code=status.HTTP_201_CREATED, response_model=SigninResponse)
@limiter.limit(f"{config.rate_limit_unprotected_routes}/minute")
async def login(request: Request, user_credentials: LoginRequest, session: AsyncSession = Depends(get_session)):
    """Authenticate a user and return access and refresh tokens. <br />

    This endpoint validates user credentials (email and password) and returns
    JWT access and refresh tokens upon successful authentication. The user must
    be verified to successfully log in. <br />

    Args: <br />
        user_credentials (LoginRequest): User login credentials containing email and password <br />
        session (AsyncSession): Database session for user validation <br />

    Raises: <br />
        UserInvalidCredentials: If the email doesn't exist or password is incorrect <br />
        UserNotVerified: If the user exists but has not been verified yet <br />

    Returns: <br />
        SigninResponse: Access and refresh tokens with success message <br />
    """
    email: str = user_credentials.email
    password: str = user_credentials.password
    user: UserModel | None = await service.get_user_by_email(email=email, session=session, include_roles=True, include_permissions=True)

    if not user:
        raise UserInvalidCredentials

    password_valid = await user_helper.verify_password(password, user.password_hash)
    if not password_valid:
        raise UserInvalidCredentials

    if not user.is_verified:
        raise UserNotVerified

    tokens = await service.create_access_tokens(user)
    return SigninResponse(
        message="Login successful",
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )


@user_router.get("/refresh", status_code=status.HTTP_200_OK, response_model=RefreshResponse)
async def get_new_refresh_token(token_data: dict = Depends(refresh_token_bearer), session: AsyncSession = Depends(get_session)):
    """Refresh the user's access and refresh tokens by providing a valid refresh token. <br />

    This endpoint generates new access and refresh tokens for the user and invalidates
    the old refresh token by adding it to the Redis blacklist. The user must provide
    a valid refresh token in the Authorization header. <br />

    Args: <br />
        token_data (dict): The decoded refresh token data from the Authorization header <br />
        session (AsyncSession): Database session for user validation <br />

    Raises: <br />
        UserNotFound: If the user related to the token was not found in the database <br />
        UserNotVerified: If the user was found but has the status "is_verified=False" <br />
        InvalidRefreshToken: If the refresh token is expired, invalid, or blacklisted <br />

    Returns: <br />
        SigninResponse: New access and refresh tokens with success message <br />
    """
    user_id = token_data["user"]["id"]
    user: UserModel | None = await service.get_user_by_id(id=user_id, session=session, include_roles=True, include_permissions=True)

    if not user:
        raise UserNotFound

    if not user.is_verified:
        raise UserNotVerified

    tokens = await service.create_access_tokens(user)

    # Invalidate old refresh token by adding it to redis blacklist
    redis = redis_manager.get_client()
    await jwt_handler.add_jwt_to_blacklist(token_data=token_data, redis_client=redis)

    return SigninResponse(
        message="Refresh successful",
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )


@user_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    token_data_access: dict = Depends(access_token_bearer)
):
    """Logout the user by invalidating the users access token. Optionally the refresh token can be provided in the request body to invalidate as well. <br />

    Args: <br />
        request (LogoutRequest): The request body containing the refresh_token <br />

    Raises:
        InvalidRefreshToken: If the RefreshToken is expired or invalid <br />

    Returns: <br />
        SignoutResponse: A status message about the signout <br />
    """
    # Invalidate access token by adding it to redis blacklist
    redis = redis_manager.get_client()
    await jwt_handler.add_jwt_to_blacklist(token_data=token_data_access, redis_client=redis)

    # If refresh token is provided, invalidate it as well
    if request.refresh_token:
        refresh_token_data = await jwt_handler.decode_token(request.refresh_token)
        if not refresh_token_data:
            raise InvalidRefreshToken

        # Verify it's actually a refresh token
        if not refresh_token_data.get('refresh'):
            raise InvalidRefreshToken

        await jwt_handler.add_jwt_to_blacklist(token_data=refresh_token_data, redis_client=redis)


@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserModel)
async def get_active_user(user: UserModel = Depends(get_current_user)):
    """Get the current logged in user and return the user data <br />

    Returns: <br />
        UserModel: The user data including the associated roles <br />
    """
    return user


@user_router.post("/update-password", status_code=status.HTTP_201_CREATED, response_model=PasswordUpdateResponse)
async def update_active_user_password(password_data: PasswordUpdateRequest,
                                      session: AsyncSession = Depends(
                                          get_session),
                                      current_user: UserModel = Depends(get_current_user)):
    """Update the current user's password <br />

    Args: <br />
        password_data: The old and new password data <br />

    Returns: <br />
        201 Created: Password successfully updated <br />
    """
    # Update password using the current user's id
    _ = await service.update_user_password(
        user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
        session=session
    )
    return PasswordUpdateResponse(message="Password changed successfully")


@user_router.get("", status_code=status.HTTP_200_OK, response_model=ListUserResponse)
async def get_all_users(order_by_field: str = Query(
        None, description="The field to order the records by", example="id"),
        order_by_direction: str = Query(
        None, description="Wheter to sort the field asc or desc", example="desc"),
        limit: int = Query(100,
                           description="The maximum number of records to return",
                           ge=1,
                           le=config.default_api_pagination_limit),
        offset: int = Query(0,
                            description="How many records to skip",
                            ge=0),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_user_all)):
    """Get all users in the database <br />

    Returns: <br />
        list[UserModelBase]: The user data without the associated roles & permissions <br />
    """
    users = await service.get_users(session=session,
                                    include_roles=False,
                                    include_permissions=False,
                                    order_by_field=order_by_field,
                                    order_by_direction=order_by_direction,
                                    limit=limit,
                                    offset=offset)

    return users


@user_router.get("-with-permissions", status_code=status.HTTP_200_OK, response_model=ListUserWithPermissionsResponse)
async def get_all_users_with_permissions(order_by_field: str = Query(
        None, description="The field to order the records by", example="id"),
        order_by_direction: str = Query(
        None, description="Wheter to sort the field asc or desc", example="desc"),
        limit: int = Query(100,
                           description="The maximum number of records to return",
                           ge=1,
                           le=config.default_api_pagination_limit),
        offset: int = Query(0,
                            description="How many records to skip",
                            ge=0),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_user_all)):
    """Get all users in the database <br />

    Returns: <br />
        ListUserResponseWithPermissions: The user data including the associated roles & permissions with pagination metadata <br />
    """
    users = await service.get_users(session=session,
                                    include_roles=True,
                                    include_permissions=True,
                                    order_by_field=order_by_field,
                                    order_by_direction=order_by_direction,
                                    limit=limit,
                                    offset=offset)
    return users


@user_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserModel)
async def get_specific_user(id: str = Path(..., description="The user email or uuid", example="0198c7ff-7032-7649-88f0-438321150e2c"),
                            session: AsyncSession = Depends(get_session),
                            current_user: UserModel = Depends(get_current_user)):
    """Get a specific user in the database by the email **OR** the UUID <br />

    Returns: <br />
        UserModel: The user data including the associated roles & permissions <br />
    """
    # Check permissions based on ownership
    check_ownership_permissions(
        current_user=current_user,
        target_id=id,
        own_data_permissions=[Permission(
            type="read", resource=resource, context="me")],
        other_data_permissions=[Permission(
            type="read", resource=resource, context="all")]
    )

    # Now proceed with the database query
    if "@" in id:
        user = await service.get_user_by_email(email=id, session=session, include_roles=True, include_permissions=True)
    else:
        try:
            uuid.UUID(id)
        except ValueError:
            raise InvalidUUID(id)
        user = await service.get_user_by_id(id=id, session=session, include_roles=True, include_permissions=True)

    if not user:
        raise UserNotFound
    return user


@user_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=UserModel)
async def update_user(id: str = Path(..., description="The user email or uuid", example="0198c7ff-7032-7649-88f0-438321150e2c"),
                      update_data: UserUpdateRequest = None,
                      session: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)):
    """Update a specific user in the database by the email **OR** the UUID <br />

    Args: <br />
        id: The user email or UUID to update <br />
        update_data: The user data to update (all fields optional for PATCH-like behavior) <br />

    Returns: <br />
        UserModel: The updated user data including the associated roles & permissions <br />
    """
    # Check permissions based on ownership
    check_ownership_permissions(
        current_user=current_user,
        target_id=id,
        own_data_permissions=[Permission(
            type="update", resource=resource, context="me")],
        other_data_permissions=[Permission(
            type="update", resource=resource, context="all")]
    )

    # Convert Pydantic model to dict, excluding None values
    update_dict = update_data.model_dump(
        exclude_none=True) if update_data else {}

    if not update_dict:
        raise XValueError("No fields provided for update")

    # Now proceed with the database update
    if "@" in id:
        updated_user = await service.update_user_by_email(email=id, update_data=update_dict, session=session)
    else:
        try:
            user_id = uuid.UUID(id)
        except ValueError:
            raise InvalidUUID(id)
        updated_user = await service.update_user(id=user_id, update_data=update_dict, session=session)

    if not updated_user:
        raise UserNotFound
    return await service.get_user_by_id(id=updated_user.id, session=session, include_roles=True, include_permissions=True)


@user_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str = Path(..., description="The user email or uuid", example="0198c7ff-7032-7649-88f0-438321150e2c"),
                      session: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)):
    """Delete a specific user from the database by the email **OR** the UUID <br />

    Returns: <br />
        204 No Content: User successfully deleted <br />
    """
    # Check permissions based on ownership
    check_ownership_permissions(
        current_user=current_user,
        target_id=id,
        own_data_permissions=[Permission(
            type="delete", resource=resource, context="me")],
        other_data_permissions=[Permission(
            type="delete", resource=resource, context="all")]
    )

    # Now proceed with the database deletion
    if "@" in id:
        user_deleted = await service.delete_user_by_email(email=id, session=session)
    else:
        try:
            user_id = uuid.UUID(id)
        except ValueError:
            raise InvalidUUID(id)
        user_deleted = await service.delete_user(id=user_id, session=session)

    if not user_deleted:
        raise UserNotFound
