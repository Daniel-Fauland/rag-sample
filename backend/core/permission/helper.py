from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from database.schemas.permissions import Permission
from typing import Sequence


class PermissionServiceHelper:
    async def _get_permissions(self, session: AsyncSession, where_clause=None, order_by_field: str = None,
                               order_by_direction: str = "desc", limit: int = None, include_roles: bool = False,
                               multiple: bool = False) -> Permission | Sequence[Permission] | None:
        """Helper to get permissions by a given where clause"""
        options = []
        if include_roles:
            options.append(selectinload(Permission.roles))

        statement = select(Permission)
        if options:
            statement = statement.options(*options)
        if where_clause is not None:
            statement = statement.where(where_clause)
        if order_by_field:
            # Map allowed fields to Permission attributes for ordering
            order_fields = {
                "id": Permission.id,
                "type": Permission.type,
                "resource": Permission.resource,
                "context": Permission.context,
                "description": Permission.description,
                "is_active": Permission.is_active,
                "created_at": Permission.created_at
            }
            order_field = order_fields.get(order_by_field, Permission.id)
            order_direction = desc if order_by_direction != "asc" else asc
            statement = statement.order_by(order_direction(order_field))
        if limit:
            statement = statement.limit(limit)

        result = await session.exec(statement)
        if multiple:
            # Return all permissions that match the sql query
            permissions = result.all()
        else:
            # Return only the first permission that matches the sql query
            permissions = result.first()
        return permissions

    async def _create_permission(self, permission_data: dict, session: AsyncSession) -> Permission:
        """Helper to create a new permission in the database"""
        new_permission = Permission(**permission_data)
        session.add(new_permission)
        await session.commit()
        await session.refresh(new_permission)
        return new_permission

    async def _update_permission(self, session: AsyncSession, where_clause, update_data: dict) -> Permission | None:
        """Helper to update a permission by a given where clause"""
        try:
            # First check if permission exists
            permission = await self._get_permissions(session=session, where_clause=where_clause)
            if not permission:
                return None

            # Update only the provided fields
            for field, value in update_data.items():
                if hasattr(permission, field) and value is not None:
                    setattr(permission, field, value)

            await session.commit()
            await session.refresh(permission)
            return permission
        except Exception as e:
            await session.rollback()
            raise e

    async def _delete_permission(self, session: AsyncSession, where_clause) -> bool:
        """Helper to delete a permission by a given where clause"""
        try:
            # First check if permission exists
            permission = await self._get_permissions(session=session, where_clause=where_clause)
            if not permission:
                return False

            # Delete the permission (cascade will handle related records)
            await session.delete(permission)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e
