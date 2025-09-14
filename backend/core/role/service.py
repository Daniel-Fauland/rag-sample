from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence
from database.schemas.roles import Role
from models.role.request import RoleCreateRequest
from core.role.helper import RoleServiceHelper

service_helper = RoleServiceHelper()


class RoleService:
    async def get_role_by_id(self, id: int, session: AsyncSession, include_permissions: bool = False) -> Role | None:
        """Get a role by its unique identifier.

        Args:
            id: The role's ID
            session: Database session
            include_permissions: Whether to eagerly load role permissions

        Returns:
            Role object if found, None otherwise
        """
        return await service_helper._get_roles(session=session, where_clause=Role.id == id, include_permissions=include_permissions)

    async def get_role_by_name(self, name: str, session: AsyncSession, include_permissions: bool = False) -> Role | None:
        """Get a role by its name.

        Args:
            name: The role's name
            session: Database session
            include_permissions: Whether to eagerly load role permissions

        Returns:
            Role object if found, None otherwise
        """
        return await service_helper._get_roles(session=session, where_clause=Role.name == name, include_permissions=include_permissions)

    async def get_roles(self, session: AsyncSession, include_permissions: bool = False, order_by_field: str = "id",
                        order_by_direction: str = "desc", limit: int = None) -> Sequence[Role]:
        """Get all roles in the database

        Args:
            session: Database session
            include_permissions: Whether to eagerly load role permissions
            order_by_field (str, optional): The Field to order the data by. Defaults to Role.id.
            order_by_direction (str, optional): The order direction. Defaults to 'desc'.
            limit (int): The maximum number of records to return. Defaults to None which means no limit

        Returns:
            A sequence of Role objects
        """
        return await service_helper._get_roles(session=session, include_permissions=include_permissions,
                                               order_by_field=order_by_field, order_by_direction=order_by_direction,
                                               limit=limit, multiple=True)

    async def role_exists(self, name: str, session: AsyncSession) -> bool:
        """Check if a role already exists in the database

        Args:
            name (str): The role's name
            session (AsyncSession): The db session

        Returns:
            bool: Whether the role already exists in the db
        """
        role = await self.get_role_by_name(name, session)
        return True if role is not None else False

    async def create_role(self, role_data: RoleCreateRequest, session: AsyncSession) -> Role:
        """Create a new role in database

        Args:
            role_data (RoleCreateRequest): The data of the new role to create
            session: Database session

        Returns:
            Role: The newly created role
        """
        role_dict = role_data.model_dump()
        return await service_helper._create_role(role_data=role_dict, session=session)

    async def update_role(self, id: int, update_data: dict, session: AsyncSession) -> Role | None:
        """Update a role in the database by its unique identifier.

        Args:
            id: The role's ID
            update_data: Dictionary containing the fields to update
            session: Database session

        Returns:
            Role object if updated successfully, None if role was not found

        Raises:
            ValueError: If the role ID is invalid
        """
        return await service_helper._update_role(session=session, where_clause=Role.id == id, update_data=update_data)

    async def delete_role(self, id: int, session: AsyncSession) -> bool:
        """Delete a role from the database by its unique identifier.

        Args:
            id: The role's ID
            session: Database session

        Returns:
            bool: True if role was deleted, False if role was not found

        Raises:
            ValueError: If the role ID is invalid
        """
        return await service_helper._delete_role(session=session, where_clause=Role.id == id)
