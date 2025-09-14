from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from database.schemas.roles import Role
from typing import Sequence


class RoleServiceHelper:
    async def _get_roles(self, session: AsyncSession, where_clause=None, order_by_field: str = None,
                         order_by_direction: str = "desc", limit: int = None, include_permissions: bool = False,
                         multiple: bool = False) -> Role | Sequence[Role] | None:
        """Helper to get roles by a given where clause"""
        options = []
        if include_permissions:
            options.append(selectinload(Role.permissions))
        statement = select(Role)
        if options:
            statement = statement.options(*options)
        if where_clause is not None:
            statement = statement.where(where_clause)
        if order_by_field:
            # Map allowed fields to Role attributes for ordering
            order_fields = {
                "id": Role.id,
                "name": Role.name,
                "description": Role.description,
                "is_active": Role.is_active,
                "created_at": Role.created_at
            }
            order_field = order_fields.get(order_by_field, Role.id)
            order_direction = desc if order_by_direction != "asc" else asc
            statement = statement.order_by(order_direction(order_field))
        if limit:
            statement = statement.limit(limit)
        result = await session.exec(statement)
        if multiple:
            # Return all roles that match the sql query
            roles = result.all()
        else:
            # Return only the first role that matches the sql query
            roles = result.first()
        return roles

    async def _create_role(self, role_data: dict, session: AsyncSession) -> Role:
        """Helper to create a new role in the database"""
        new_role = Role(**role_data)
        session.add(new_role)
        await session.commit()
        await session.refresh(new_role)
        return new_role

    async def _update_role(self, session: AsyncSession, where_clause, update_data: dict) -> Role | None:
        """Helper to update a role by a given where clause"""
        try:
            # First check if role exists
            role = await self._get_roles(session=session, where_clause=where_clause)
            if not role:
                return None

            # Update only the provided fields
            for field, value in update_data.items():
                if hasattr(role, field) and value is not None:
                    setattr(role, field, value)

            await session.commit()
            await session.refresh(role)
            return role
        except Exception as e:
            await session.rollback()
            raise e

    async def _delete_role(self, session: AsyncSession, where_clause) -> bool:
        """Helper to delete a role by a given where clause"""
        try:
            # First check if role exists
            role = await self._get_roles(session=session, where_clause=where_clause)
            if not role:
                return False

            # Delete the role (cascade will handle related records)
            await session.delete(role)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e
