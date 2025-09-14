from datetime import timedelta, datetime, timezone
from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from database.schemas.users import User
from database.schemas.roles import Role
from database.schemas.user_roles import UserRole
from models.user.request import SignupRequest
from models.user.response import UserModel
from utils.user import UserHelper
from auth.jwt import JWTHandler
from errors import UserInvalidPassword, InternalServerError
from utils.logging import logger
from config import config

user_helper = UserHelper()
jwt_handler = JWTHandler()


class ServiceHelper():
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

    async def _create_user(self, user_data: SignupRequest, session: AsyncSession) -> User:
        """Helper to create a new user in the database"""
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = await user_helper.hash_password(user_data_dict["password"])

        session.add(new_user)
        await session.flush()  # Flush to get the user ID

        # Get the default user role for new users
        default_role = await self._get_user_role(config.default_user_role, session)

        # Create the user-role relationship
        user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
        session.add(user_role)

        await session.commit()
        return new_user

    async def _delete_user(self, session: AsyncSession, where_clause) -> bool:
        """Helper to delete a user by a given where clause"""
        try:
            # First check if user exists
            user = await self._get_users(session=session, where_clause=where_clause)
            if not user:
                return False

            # Delete the user (cascade will handle related records)
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e

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

            # Automatically update the modified_at timestamp
            user.modified_at = datetime.now(timezone.utc)

            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            raise e

    async def _get_user_role(self, role: str, session: AsyncSession) -> Role:
        """Get the default 'user' role for new users"""
        statement = select(Role).where(Role.name == role)
        result = await session.exec(statement)
        role = result.first()
        if not role:
            raise ValueError(f"Role '{role}' does not exist in database")
        return role

    async def _create_access_tokens(self, user: UserModel, access: bool = True, refresh: bool = True) -> dict:
        """Helper to create jwt tokens"""
        # Convert roles to serializable format
        serializable_roles = [
            {
                'id': role.id,
                'name': role.name,
                'is_active': role.is_active
            } for role in user.roles
        ]

        tokens = {}
        if access:
            access_token = await jwt_handler.create_access_token(
                user_data={'id': str(user.id),
                           'roles': serializable_roles},
                refresh=False,
                expiry=timedelta(minutes=config.jwt_access_token_expiry)
            )
            tokens["access_token"] = access_token
        if refresh:
            refresh_token = await jwt_handler.create_access_token(
                user_data={'id': str(user.id)},
                refresh=True,
                expiry=timedelta(days=config.jwt_refresh_token_expiry)
            )
            tokens["refresh_token"] = refresh_token
        return tokens

    async def _update_user_password(self, user: UserModel, old_password: str, new_password: str, session: AsyncSession) -> bool:
        """Helper to update the users password"""
        # Verify old password
        is_old_password_correct = await user_helper.verify_password(old_password, user.password_hash)
        if not is_old_password_correct:
            raise UserInvalidPassword

        # Hash new password
        new_password_hash = await user_helper.hash_password(new_password)
        try:
            # Update password
            user.password_hash = new_password_hash
            user.modified_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(user)
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Could not update users password: {e}")
            raise InternalServerError("_update_user_password")
