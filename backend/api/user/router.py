from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.user.service import UserService
from utils.user import UserHelper
from auth.jwt import JWTHandler
from auth.auth import get_current_user
from models.user.request import SignupRequest, LoginRequest, LogoutRequest
from models.user.response import SignupResponse, SigninResponse, RefreshResponse, SignoutResponse, UserModel
from errors import UserEmailExists, UserInvalidCredentials, UserNotFound, UserNotVerified, InvalidRefreshToken
from auth.auth import AccessTokenBearer, RefreshTokenBearer
from database.session import get_session
from database.redis import redis_manager


user_router = APIRouter()
service = UserService()
user_helper = UserHelper()
jwt_handler = JWTHandler()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()

# Rate limiter for user endpoints
limiter = Limiter(key_func=get_remote_address)


@user_router.post("/signup", status_code=201, response_model=SignupResponse)
@limiter.limit("5/minute")  # 5 signups per minute per IP
async def signup(request: Request, user_data: SignupRequest, session: AsyncSession = Depends(get_session)):
    """Create a new user in the database <br />

    Args: <br />
        request (SignupRequest): The user to sign up <br />

    Returns: <br />
        SignupResponse: The users email and a success flag <br />
    """
    email = user_data.email
    user_exists = await service.user_exists(email=email, session=session)
    if user_exists:
        raise UserEmailExists()

    new_user = await service.create_user(user_data, session)
    return SignupResponse(email=new_user.email, sucess=True)


@user_router.post("/login", status_code=201, response_model=SigninResponse)
@limiter.limit("10/minute")  # 10 login attempts per minute per IP
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
    user: UserModel | None = await service.get_user_by_email(email=email, session=session, include_roles=True)

    if not user:
        raise UserInvalidCredentials

    password_valid = await user_helper.verify_password(password, user.password_hash)
    if not password_valid:
        raise UserInvalidCredentials

    if not user.is_verified:
        raise UserNotVerified

    access_token, refresh_token = await service.create_access_tokens(user)
    return SigninResponse(
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@user_router.get("/refresh", status_code=200, response_model=RefreshResponse)
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
    user: UserModel | None = await service.get_user_by_id(id=user_id, session=session, include_roles=True)

    if not user:
        raise UserNotFound

    if not user.is_verified:
        raise UserNotVerified

    access_token, refresh_token = await service.create_access_tokens(user)

    # Invalidate old refresh token by adding it to redis blacklist
    redis = redis_manager.get_client()
    await jwt_handler.add_jwt_to_blacklist(token_data=token_data, redis_client=redis)

    return SigninResponse(
        message="Refresh successful",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@user_router.post("/logout", status_code=200, response_model=SignoutResponse)
async def logout(
    request: LogoutRequest,
    token_data_access: dict = Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session)
):
    """Logout the user by invalidating the users access token. Optionally the refresh token can be provided in the request body to invalidate as well. <br />

    Args: <br />
        request (LogoutRequest): The request body containing the refresh_token <br />

    Raises:
        UserNotFound: If the user related to the token was not found in the db <br />
        UserNotVerified: If the user was found in the db but has the status "is_verified=False" <br />
        InvalidRefreshToken: If the RefreshToken is expired or invalid <br />

    Returns: <br />
        SignoutResponse: A status message about the signout <br />
    """
    user_id = token_data_access["user"]["id"]
    user: UserModel | None = await service.get_user_by_id(id=user_id, session=session, include_roles=True)

    if not user:
        raise UserNotFound

    if not user.is_verified:
        raise UserNotVerified

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

    return SignoutResponse(
        message="Signout successful",
    )


@user_router.get("/me", status_code=200, response_model=UserModel)
async def get_active_user(user: UserModel = Depends(get_current_user)):
    """Get the current logged in user and return the user data <br />

    Returns: <br />
        UserModel: The user data including the associated roles <br />
    """
    return user
