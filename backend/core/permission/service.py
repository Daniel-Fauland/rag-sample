from sqlmodel.ext.asyncio.session import AsyncSession
from database.schemas.permissions import Permission
from models.permission.request import PermissionCreateRequest
from models.permission.response import ListPermissionModel
from core.permission.helper import PermissionServiceHelper

service_helper = PermissionServiceHelper()


class PermissionService:
    async def get_permission_by_id(self, id: int, session: AsyncSession, include_roles: bool = False) -> Permission | None:
        """Get a permission by its unique identifier.

        Args:
            id: The permission's ID
            session: Database session
            include_roles: Whether to eagerly load permission roles

        Returns:
            Permission object if found, None otherwise
        """
        return await service_helper._get_permissions(session=session, where_clause=Permission.id == id, include_roles=include_roles)

    async def get_permissions(self, session: AsyncSession, include_roles: bool = False, order_by_field: str = "id",
                              order_by_direction: str = "desc", limit: int = 100, offset: int = 0) -> ListPermissionModel:
        """Get all permissions in the database

        Args:
            session: Database session
            include_roles: Whether to eagerly load permission roles
            order_by_field (str, optional): The Field to order the data by. Defaults to Permission.id.
            order_by_direction (str, optional): The order direction. Defaults to 'desc'.
            limit (int): The maximum number of records to return. Defaults to 100
            offset (int): The number of records to offset/skip aka pagination

        Returns:
            ListPermissionModel
        """
        return await service_helper._get_permissions(session=session, include_roles=include_roles,
                                                     order_by_field=order_by_field, order_by_direction=order_by_direction,
                                                     limit=limit, offset=offset, multiple=True)

    async def permission_exists(self, type_value: str, resource: str, context: str, session: AsyncSession) -> bool:
        """Check if a permission already exists in the database

        Args:
            type_value (str): The permission's type
            resource (str): The permission's resource
            context (str): The permission's context
            session (AsyncSession): The db session

        Returns:
            bool: Whether the permission already exists in the db
        """
        permission = await service_helper._get_permissions(
            session=session,
            where_clause=(Permission.type == type_value) &
                         (Permission.resource == resource) &
                         (Permission.context == context)
        )
        return True if permission is not None else False

    async def create_permission(self, permission_data: PermissionCreateRequest, session: AsyncSession) -> Permission:
        """Create a new permission in database

        Args:
            permission_data (PermissionCreateRequest): The data of the new permission to create
            session: Database session

        Returns:
            Permission: The newly created permission
        """
        permission_dict = permission_data.model_dump()
        # Convert enum values to strings for database storage
        permission_dict["type"] = permission_dict["type"].value
        permission_dict["context"] = permission_dict["context"].value
        return await service_helper._create_permission(permission_data=permission_dict, session=session)

    async def update_permission(self, id: int, update_data: dict, session: AsyncSession) -> Permission | None:
        """Update a permission in the database by its unique identifier.

        Args:
            id: The permission's ID
            update_data: Dictionary containing the fields to update
            session: Database session

        Returns:
            Permission object if updated successfully, None if permission was not found

        Raises:
            ValueError: If the permission ID is invalid
        """
        # Convert enum values to strings if present
        if "type" in update_data and hasattr(update_data["type"], "value"):
            update_data["type"] = update_data["type"].value
        if "context" in update_data and hasattr(update_data["context"], "value"):
            update_data["context"] = update_data["context"].value
        return await service_helper._update_permission(session=session, where_clause=Permission.id == id, update_data=update_data)

    async def delete_permission(self, id: int, session: AsyncSession) -> bool:
        """Delete a permission from the database by its unique identifier.

        Args:
            id: The permission's ID
            session: Database session

        Returns:
            bool: True if permission was deleted, False if permission was not found

        Raises:
            ValueError: If the permission ID is invalid
        """
        return await service_helper._delete_permission(session=session, where_clause=Permission.id == id)
