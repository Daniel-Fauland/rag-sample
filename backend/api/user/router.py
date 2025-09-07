from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from core.user.service import UserService
from utils.user import UserHelper
from auth.jwt import JWTHandler
from auth.auth import get_current_user
from models.user.request import SignupRequest, LoginRequest
from models.user.response import SignupResponse, SigninResponse, RefreshResponse, UserModel
from errors import UserEmailExists, UserInvalidCredentials, UserNotFound, UserNotVerified
from auth.auth import RefreshTokenBearer
from database.session import get_session

user_router = APIRouter()
service = UserService()
user_helper = UserHelper()
jwt_handler = JWTHandler()
refresh_token_bearer = RefreshTokenBearer()


@user_router.post("/signup", status_code=201, response_model=SignupResponse)
async def signup(user_data: SignupRequest, session: AsyncSession = Depends(get_session)):
    """Create a new user in the database

    Args:
        request (SignupRequest): The user to sign up

    Returns:
        SignupResponse: The users email and a success flag
    """
    email = user_data.email
    user_exists = await service.user_exists(email=email, session=session)
    if user_exists:
        raise UserEmailExists()

    new_user = await service.create_user(user_data, session)
    return SignupResponse(email=new_user.email, sucess=True)


@user_router.post("/login", status_code=201, response_model=SigninResponse)
async def login(user_credentials: LoginRequest, session: AsyncSession = Depends(get_session)):
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
async def get_new_refresh_token(token_details: dict = Depends(refresh_token_bearer), session: AsyncSession = Depends(get_session)):
    user_id = token_details["user"]["id"]
    user: UserModel | None = await service.get_user_by_id(id=user_id, session=session, include_roles=True)

    if not user:
        raise UserNotFound

    if not user.is_verified:
        raise UserNotVerified

    access_token, refresh_token = await service.create_access_tokens(user)
    return SigninResponse(
        message="Refresh successful",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@user_router.get("/me", status_code=200, response_model=UserModel)
async def get_active_user(user: UserModel = Depends(get_current_user)):
    """Get the current logged in user and return the user data

    Returns:
        UserModel: The user data including the associated roles
    """
    return user
