from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from database.schemas.users import User
from database.schemas.roles import Role
from database.schemas.user_roles import UserRole
from models.user.request import SignupRequest
from utils.user import UserHelper
# from schemas.users import UserCreateModel
# from utils.current_user import generate_password_hash

user_helper = UserHelper()


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession, include_roles: bool = False) -> User | None:
        """Get a user by email"""
        options = []
        if include_roles:
            options.append(selectinload(User.roles))
        statement = select(User)

        if options:
            statement = statement.options(*options)
        statement = statement.where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
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

    async def create_user(self, user_data: SignupRequest, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = await user_helper.hash_password(user_data_dict["password"])

        session.add(new_user)
        await session.flush()  # Flush to get the user ID

        # Get the default 'user' role
        default_role = await self.get_user_role("user", session)

        # Create the user-role relationship
        user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
        session.add(user_role)

        await session.commit()
        return new_user
