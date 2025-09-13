import uuid
from datetime import timedelta
from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Sequence
from database.schemas.users import User
from database.schemas.roles import Role
from database.schemas.user_roles import UserRole
from models.user.request import SignupRequest
from models.user.response import UserModel
from errors import UserInvalidPassword
from utils.user import UserHelper
from auth.jwt import JWTHandler
from utils.logging import logger
from config import config

user_helper = UserHelper()
jwt_handler = JWTHandler()


class UserService:
    async def _get_users(self, session: AsyncSession, where_clause=None, order_by_field: str = None, order_by_direction: str = "desc", limit: int = None, include_roles: bool = False, include_permissions: bool = False, multiple: bool = False) -> User | None:
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
        if where_clause is not None:
            statement = statement.where(where_clause)
        if order_by_field:
            # Map allowed fields to User attributes for ordering
            order_fields = {
                "id": User.id,
                "email": User.email,
                "first_name": User.first_name,
                "last_name": User.last_name,
                "is_verified": User.is_verified,
                "account_type": User.account_type,
                "created_at": User.created_at,
                "modified_at": User.modified_at
            }
            order_field = order_fields.get(order_by_field, User.id)
            order_direction = desc if order_by_direction != "asc" else asc
            statement = statement.order_by(order_direction(order_field))
        if limit:
            statement = statement.limit(limit)
        result = await session.exec(statement)
        if multiple:
            # Return all users that match the sql query
            users = result.all()
        else:
            # Return only the first user that matches the sql query
            users = result.first()
        return users

    async def _update_user(self, session: AsyncSession, where_clause, update_data: dict) -> User | None:
        """Helper to update a user by a given where clause"""
        try:
            # First check if user exists
            user = await self._get_users(session=session, where_clause=where_clause)
            if not user:
                return None

            # Update only the provided fields
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)

            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            raise e

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
        return await self._get_users(session=session, where_clause=User.id == id, include_roles=include_roles, include_permissions=include_permissions)

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
        return await self._get_users(session=session, where_clause=User.email == email, include_roles=include_roles, include_permissions=include_permissions)

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
        return await self._get_users(session=session, include_roles=include_roles, include_permissions=include_permissions, order_by_field=order_by_field, order_by_direction=order_by_direction, limit=limit, multiple=True)

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
        try:
            # First check if user exists
            user = await self.get_user_by_id(id=id, session=session)
            if not user:
                return False

            # Delete the user (cascade will handle related records)
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e

    async def delete_user_by_email(self, email: str, session: AsyncSession) -> bool:
        """Delete a user from the database by their email.

        Args:
            email: The user's email
            session: Database session

        Returns:
            bool: True if user was deleted, False if user was not found
        """
        try:
            # First check if user exists
            user = await self.get_user_by_email(email=email, session=session)
            if not user:
                return False

            # Delete the user (cascade will handle related records)
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e

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
        return await self._update_user(session=session, where_clause=User.id == id, update_data=update_data)

    async def update_user_by_email(self, email: str, update_data: dict, session: AsyncSession) -> User | None:
        """Update a user in the database by their email.

        Args:
            email: The user's email
            update_data: Dictionary containing the fields to update
            session: Database session

        Returns:
            User object if updated successfully, None if user was not found
        """
        return await self._update_user(session=session, where_clause=User.email == email, update_data=update_data)

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
            ValueError: If old password is incorrect
            Exception: If password hashing fails
        """
        # Verify old password
        is_old_password_correct = await user_helper.verify_password(old_password, user.password_hash)
        if not is_old_password_correct:
            raise UserInvalidPassword

        # Hash new password
        new_password_hash = await user_helper.hash_password(new_password)
        try:
            # Update password
            user.password_hash = new_password_hash
            await session.commit()
            await session.refresh(user)
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Could not update users password: {e}")
            return False
