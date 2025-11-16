from datetime import timedelta, datetime, timezone
from sqlmodel import select, asc, desc, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from database.schemas.users import User
from database.schemas.roles import Role
from database.schemas.user_roles import UserRole
from models.user.request import SignupRequest, BatchSignupRequest, BatchDeleteRequest, BatchUserUpdateRequest
from models.user.response import UserModel, BatchSignupResponseBase, BatchUpdateResponseBase, ListUserModel
from utils.user import UserHelper
from auth.jwt import JWTHandler
from errors import UserInvalidPassword, InternalServerError
from utils.logging import logger
from config import config
import asyncio
import uuid

user_helper = UserHelper()
jwt_handler = JWTHandler()


class ServiceHelper():
    async def _get_users(self, session: AsyncSession, where_clause=None, order_by_field: str = None, order_by_direction: str = "desc", limit: int = 100, offset: int = 0, include_roles: bool = False, include_permissions: bool = False, multiple: bool = False) -> ListUserModel | User | None:
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
        if offset:
            statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)
        result = await session.exec(statement)
        if multiple:
            # Get total count of users matching the where clause (without limit/offset)
            count_statement = select(func.count(User.id))
            if where_clause is not None:
                count_statement = count_statement.where(where_clause)
            count_result = await session.exec(count_statement)
            total_users = count_result.one()

            # Return all users that match the sql query
            users = result.all()
            return ListUserModel(limit=limit, offset=offset, total_users=total_users, current_users=len(users), users=users)
        else:
            # Return only the first user that matches the sql query
            return result.first()

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

    async def _create_users(self, user_data: BatchSignupRequest, session: AsyncSession) -> list[BatchSignupResponseBase]:
        """Helper to create new users in the database in batch

        This method efficiently creates multiple users by:
        1. Detecting duplicate emails within the batch
        2. Checking all emails against existing users in a single query
        3. Hashing passwords in parallel
        4. Creating all users in a single bulk insert
        5. Creating all user-role relationships in a single bulk insert

        Args:
            user_data (BatchSignupRequest): The data of the new users to create
            session (AsyncSession): The database session

        Returns:
            list[BatchSignupResponseBase]: List of results for each user with email, success flag, and reason
        """
        results: list[BatchSignupResponseBase] = []
        users_to_create: list[SignupRequest] = user_data.users

        # Step 1: Detect duplicate emails within the batch itself
        seen_emails = {}
        unique_users = []
        for user in users_to_create:
            if user.email in seen_emails:
                # Duplicate within the batch
                results.append(
                    BatchSignupResponseBase(
                        email=user.email,
                        success=False,
                        reason="Duplicate email in the batch request"
                    )
                )
            else:
                seen_emails[user.email] = True
                unique_users.append(user)

        # If no unique users to process, return early
        if not unique_users:
            return results

        # Step 2: Extract all unique emails and check which ones already exist in database
        emails = [user.email for user in unique_users]
        statement = select(User.email).where(User.email.in_(emails))
        result = await session.exec(statement)
        existing_emails = set(result.all())

        # Step 3: Separate users into existing and new
        new_users_data = []
        for user in unique_users:
            if user.email in existing_emails:
                # User already exists in database
                results.append(
                    BatchSignupResponseBase(
                        email=user.email,
                        success=False,
                        reason="User with this email already exists in the database"
                    )
                )
            else:
                new_users_data.append(user)

        # If no new users to create, return early
        if not new_users_data:
            return results

        # Step 4: Get the default role once (used for all users)
        default_role = await self._get_user_role(config.default_user_role, session)

        # Step 5: Hash all passwords in parallel for better performance
        password_hash_tasks = [
            user_helper.hash_password(user.password)
            for user in new_users_data
        ]
        password_hashes = await asyncio.gather(*password_hash_tasks)

        # Step 6: Create User objects in bulk
        new_users = []
        for user_data, password_hash in zip(new_users_data, password_hashes):
            user_data_dict = user_data.model_dump()
            new_user = User(**user_data_dict)
            new_user.password_hash = password_hash
            new_users.append(new_user)

        # Step 7: Add all users to session and flush to get IDs
        session.add_all(new_users)
        await session.flush()

        # Step 8: Create user-role relationships in bulk
        user_roles = [
            UserRole(user_id=user.id, role_id=default_role.id)
            for user in new_users
        ]
        session.add_all(user_roles)

        # Step 9: Commit all changes
        await session.commit()

        # Step 10: Add successful results
        for user in new_users:
            results.append(
                BatchSignupResponseBase(
                    email=user.email,
                    success=True,
                    reason=""
                )
            )

        return results

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

    async def _delete_users(self, delete_data: BatchDeleteRequest, session: AsyncSession) -> None:
        """Helper to delete multiple users from the database in batch

        This method efficiently deletes multiple users by:
        1. Parsing identifiers (emails and UUIDs)
        2. Deleting all matching users in a single database operation
        3. Related records (user_roles) are automatically deleted via CASCADE

        Args:
            delete_data (BatchDeleteRequest): The identifiers (emails or UUIDs) of users to delete
            session (AsyncSession): The database session

        Returns:
            None: Always returns None (204 No Content), even if users don't exist
        """
        identifiers = delete_data.identifiers

        if not identifiers:
            return

        # Step 1: Separate emails from UUIDs
        emails = []
        user_ids = []

        for identifier in identifiers:
            if "@" in identifier:
                # It's an email
                emails.append(identifier)
            else:
                # Try to parse as UUID
                try:
                    user_id = uuid.UUID(identifier)
                    user_ids.append(user_id)
                except ValueError:
                    # Invalid UUID format - skip silently (don't throw error)
                    logger.warning(
                        f"Invalid UUID format in batch delete: {identifier}")
                    continue

        # Step 2: Build OR conditions for deletion
        conditions = []
        if emails:
            conditions.append(User.email.in_(emails))
        if user_ids:
            conditions.append(User.id.in_(user_ids))

        # If no valid identifiers, return early
        if not conditions:
            return

        # Step 3: Delete all matching users in a single operation
        # Related records in user_roles are automatically deleted via CASCADE
        from sqlalchemy import or_
        statement = delete(User).where(or_(*conditions))

        try:
            await session.exec(statement)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during batch delete: {e}")
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

    async def _update_users(self, update_data: BatchUserUpdateRequest, session: AsyncSession) -> list[BatchUpdateResponseBase]:
        """Helper to update multiple users in the database in batch

        This method efficiently updates multiple users by:
        1. Parsing identifiers (emails and UUIDs) and validating update data
        2. Fetching all matching users in a single query
        3. Applying updates to all users in memory
        4. Committing all changes in a single transaction

        Args:
            update_data (BatchUserUpdateRequest): The users to update with their respective changes
            session (AsyncSession): The database session

        Returns:
            list[BatchUpdateResponseBase]: List of results for each user with identifier, success flag, and reason
        """
        results: list[BatchUpdateResponseBase] = []
        users_to_update = update_data.users

        if not users_to_update:
            return results

        # Step 1: Parse identifiers and prepare update data
        emails = []
        user_ids = []
        identifier_to_updates = {}  # Map identifier to update data

        for user_update in users_to_update:
            identifier = user_update.identifier
            update_dict = user_update.updates.model_dump(exclude_none=True)

            # Check if any fields provided for update
            if not update_dict:
                results.append(
                    BatchUpdateResponseBase(
                        identifier=identifier,
                        success=False,
                        reason="No fields provided for update"
                    )
                )
                continue

            # Parse identifier
            if "@" in identifier:
                emails.append(identifier)
                identifier_to_updates[identifier] = update_dict
            else:
                try:
                    user_id = uuid.UUID(identifier)
                    user_ids.append(user_id)
                    identifier_to_updates[str(user_id)] = update_dict
                except ValueError:
                    results.append(
                        BatchUpdateResponseBase(
                            identifier=identifier,
                            success=False,
                            reason="Invalid UUID format"
                        )
                    )
                    continue

        # If no valid users to update, return early
        if not emails and not user_ids:
            return results

        # Step 2: Fetch all matching users in a single query
        from sqlalchemy import or_
        conditions = []
        if emails:
            conditions.append(User.email.in_(emails))
        if user_ids:
            conditions.append(User.id.in_(user_ids))

        statement = select(User).where(or_(*conditions))
        result = await session.exec(statement)
        users = result.all()

        # Create a map of identifier to user for easy lookup
        identifier_to_user = {}
        for user in users:
            identifier_to_user[user.email] = user
            identifier_to_user[str(user.id)] = user

        # Step 3: Apply updates to all users in memory
        updated_identifiers = set()
        current_time = datetime.now(timezone.utc)

        try:
            for identifier, update_dict in identifier_to_updates.items():
                user = identifier_to_user.get(identifier)

                if not user:
                    results.append(
                        BatchUpdateResponseBase(
                            identifier=identifier,
                            success=False,
                            reason="User not found"
                        )
                    )
                    continue

                # Apply updates
                for field, value in update_dict.items():
                    if hasattr(user, field) and value is not None:
                        setattr(user, field, value)

                # Update modified_at timestamp
                user.modified_at = current_time
                updated_identifiers.add(identifier)

            # Step 4: Commit all changes in a single transaction
            await session.commit()

            # Step 5: Add successful results for updated users
            for identifier in updated_identifiers:
                results.append(
                    BatchUpdateResponseBase(
                        identifier=identifier,
                        success=True,
                        reason=""
                    )
                )

            return results

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during batch update: {e}")
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
