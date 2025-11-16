from datetime import datetime, timezone
from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from database.schemas.permissions import Permission
from models.permission.response import ListPermissionModel


class PermissionServiceHelper:
    async def _get_permissions(self, session: AsyncSession, where_clause=None, order_by_field: str = None,
                               order_by_direction: str = "desc", limit: int = 100, offset: int = 0, include_roles: bool = False,
                               multiple: bool = False) -> Permission | ListPermissionModel | None:
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
        if offset:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        result = await session.exec(statement)
        if multiple:
            # Get total count of permissions matching the where clause (without limit/offset)
            count_statement = select(func.count(Permission.id))
            if where_clause is not None:
                count_statement = count_statement.where(where_clause)
            count_result = await session.exec(count_statement)
            total_permissions = count_result.one()

            # Return all permissions that match the sql query
            permissions = result.all()
            return ListPermissionModel(limit=limit, offset=offset, total_permissions=total_permissions, current_permissions=len(permissions), permissions=permissions)
        else:
            # Return only the first permission that matches the sql query
            return result.first()

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
            permission.modified_at = datetime.now(timezone.utc)

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
