import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence
from database.schemas.users import User
from models.user.request import SignupRequest
from models.user.response import UserModel
from core.user.helper import ServiceHelper

service_helper = ServiceHelper()


class UserService:
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
        return await service_helper._get_users(session=session, where_clause=User.id == id, include_roles=include_roles, include_permissions=include_permissions)

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
        return await service_helper._get_users(session=session, where_clause=User.email == email, include_roles=include_roles, include_permissions=include_permissions)

    async def get_users(self, session: AsyncSession, include_roles: bool = False, include_permissions: bool = False, order_by_field: str = "id", order_by_direction: str = "desc", limit: int = None) -> Sequence[User]:
        """Get all users in the database

        Args:
            session: Database session
            include_roles: Whether to eagerly load user roles
            include_permissions: Whether to eagerly load permissions for each role
            order_by_field (str, optional): The Field to order the data by. Defaults to User.id.
            order_by_direction (str, optional): The order direction. Defaults to 'desc'.
            limit (int): The maximum number of records to return. Defaults no None which means no limit

        Returns:
            A sequence of User objects
        """
        return await service_helper._get_users(session=session, include_roles=include_roles, include_permissions=include_permissions, order_by_field=order_by_field, order_by_direction=order_by_direction, limit=limit, multiple=True)

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        """Check if a user already exists in the database

        Args:
            email (str): The users email
            session (AsyncSession): The db session

        Returns:
            bool: Wheter the user already exists in the db
        """
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(self, user_data: SignupRequest, session: AsyncSession) -> User:
        """Create a new user in database including the user-role relationship

        Args:
            user_data (SignupRequest): The data of the new user to create

        Returns:
            User: The newly created user
        """
        return await service_helper._create_user(user_data=user_data, session=session)

    async def create_access_tokens(self, user: UserModel, access: bool = True, refresh: bool = True) -> dict:
        """
        Create access and refresh JWT tokens for a given user.

        Args:
            user (UserModel): The user for whom to create the tokens.

        Returns:
            dict: A dict containing access and/or refresh token
        """
        return await service_helper._create_access_tokens(user=user, access=access, refresh=refresh)

    async def delete_user(self, id: uuid.UUID, session: AsyncSession) -> bool:
        """Delete a user from the database by their unique identifier.

        Args:
            id: The user's UUID
            session: Database session

        Returns:
            bool: True if user was deleted, False if user was not found

        Raises:
            ValueError: If the user ID is invalid
        """
        return await service_helper._delete_user(session=session, where_clause=User.id == id)

    async def delete_user_by_email(self, email: str, session: AsyncSession) -> bool:
        """Delete a user from the database by their email.

        Args:
            email: The user's email
            session: Database session

        Returns:
            bool: True if user was deleted, False if user was not found
        """
        return await service_helper._delete_user(session=session, where_clause=User.email == email)

    async def update_user(self, id: uuid.UUID, update_data: dict, session: AsyncSession) -> User | None:
        """Update a user in the database by their unique identifier.

        Args:
            id: The user's UUID
            update_data: Dictionary containing the fields to update
            session: Database session

        Returns:
            User object if updated successfully, None if user was not found

        Raises:
            ValueError: If the user ID is invalid
        """
        return await service_helper._update_user(session=session, where_clause=User.id == id, update_data=update_data)

    async def update_user_by_email(self, email: str, update_data: dict, session: AsyncSession) -> User | None:
        """Update a user in the database by their email.

        Args:
            email: The user's email
            update_data: Dictionary containing the fields to update
            session: Database session

        Returns:
            User object if updated successfully, None if user was not found
        """
        return await service_helper._update_user(session=session, where_clause=User.email == email, update_data=update_data)

    async def update_user_password(self, user: UserModel, old_password: str, new_password: str, session: AsyncSession) -> bool:
        """Update a user's password after verifying the old password.

        Args:
            user: The user model
            old_password: The user's current password
            new_password: The user's new password
            session: Database session

        Returns:
            bool: True if password was updated successfully

        Raises:
            UserInvalidPassword: If old password is incorrect
            InternalServerError: If password updating fails
        """
        return await service_helper._update_user_password(user=user, old_password=old_password, new_password=new_password, session=session)
