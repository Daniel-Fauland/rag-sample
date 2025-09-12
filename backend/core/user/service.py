import uuid
from datetime import timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from database.schemas.users import User
from database.schemas.roles import Role
from database.schemas.user_roles import UserRole
from models.user.request import SignupRequest
from models.user.response import UserModel
from utils.user import UserHelper
from auth.jwt import JWTHandler
from config import config

user_helper = UserHelper()
jwt_handler = JWTHandler()


class UserService:
    async def _get_user(self, session: AsyncSession, where_clause, include_roles: bool = False, include_permissions: bool = False) -> User | None:
        """Helper to get a user by a given where clause"""
        options = []
        if include_roles:
            options.append(selectinload(User.roles))
            if include_permissions:
                # Also load permissions for each role
                options.append(selectinload(
                    User.roles).selectinload(Role.permissions))
        statement = select(User)
        if options:
            statement = statement.options(*options)
        statement = statement.where(where_clause)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def get_user_by_id(self, id: uuid.UUID, session: AsyncSession, include_roles: bool = False, include_permissions: bool = False) -> User | None:
        """Get a user by their unique identifier.

        Args:
            id: The user's UUID
            session: Database session
            include_roles: Whether to eagerly load user roles
            include_permissions: Whether to eagerly load permissions for each role

        Returns:
            User object if found, None otherwise
        """
        return await self._get_user(session=session, where_clause=User.id == id, include_roles=include_roles, include_permissions=include_permissions)

    async def get_user_by_email(self, email: str, session: AsyncSession, include_roles: bool = False, include_permissions: bool = False) -> User | None:
        """Get a user by their email.

        Args:
            email: The user's email
            session: Database session
            include_roles: Whether to eagerly load user roles
            include_permissions: Whether to eagerly load permissions for each role

        Returns:
            User object if found, None otherwise
        """
        return await self._get_user(session=session, where_clause=User.email == email, include_roles=include_roles, include_permissions=include_permissions)

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        """Check if a user already exists in the database"""
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def get_user_role(self, role: str, session: AsyncSession) -> Role:
        """Get the default 'user' role for new users"""
        statement = select(Role).where(Role.name == role)
        result = await session.exec(statement)
        role = result.first()
        if not role:
            raise ValueError(f"Role '{role}' does not exist in database")
        return role

    async def create_user(self, user_data: SignupRequest, session: AsyncSession) -> User:
        """Create a new user in database including the user-role relationship

        Args:
            user_data (SignupRequest): The data of the new user to create

        Returns:
            User: The newly created user
        """
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = await user_helper.hash_password(user_data_dict["password"])

        session.add(new_user)
        await session.flush()  # Flush to get the user ID

        # Get the default user role for new users
        default_role = await self.get_user_role(config.default_user_role, session)

        # Create the user-role relationship
        user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
        session.add(user_role)

        await session.commit()
        return new_user

    async def create_access_tokens(self, user: UserModel) -> tuple[str, str]:
        """
        Create access and refresh JWT tokens for a given user.

        Args:
            user (UserModel): The user for whom to create the tokens.

        Returns:
            tuple[str, str]: A tuple containing the access token and refresh token.
        """
        # Convert roles to serializable format
        serializable_roles = [
            {
                'id': role.id,
                'name': role.name,
                'is_active': role.is_active
            } for role in user.roles
        ]

        access_token = await jwt_handler.create_access_token(
            user_data={'id': str(user.id),
                       'roles': serializable_roles},
            refresh=False,
            expiry=timedelta(minutes=config.jwt_access_token_expiry)
        )

        refresh_token = await jwt_handler.create_access_token(
            user_data={'id': str(user.id)},
            refresh=True,
            expiry=timedelta(days=config.jwt_refresh_token_expiry)
        )
        return access_token, refresh_token
