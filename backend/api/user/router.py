from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from models.user.request import SignupRequest, LoginRequest
from models.user.response import SignupResponse, SigninResponse, UserModel
from core.user.service import UserService
from errors import UserEmailExists, UserInvalidCredentials
from utils.user import UserHelper
from auth.jwt import JWTHandler
from database.session import get_session
from config import config

user_router = APIRouter()
service = UserService()
user_helper = UserHelper()
jwt_handler = JWTHandler()


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

    # Convert roles to serializable format
    serializable_roles = [
        {
            'id': role.id,
            'name': role.name,
            'is_active': role.is_active
        } for role in user.roles
    ]

    access_token = await jwt_handler.create_access_token(
        user_data={'id': str(user.id), 'email': user.email,
                   'roles': serializable_roles},
        refresh=False,
        expiry=timedelta(minutes=config.jwt_access_token_expiry)
    )

    refresh_token = await jwt_handler.create_access_token(
        user_data={'id': str(user.id), 'email': user.email},
        refresh=True,
        expiry=timedelta(days=config.jwt_refresh_token_expiry)
    )

    return SigninResponse(
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
    )
