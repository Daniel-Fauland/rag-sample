from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from database.schemas.role_permissions import RolePermission
from models.permission_assignment.response import ListPermissionAssignmentModel
from typing import Sequence, Optional


class PermissionAssignmentServiceHelper:
    """Helper class for permission assignment database operations."""

    async def _get_permission_assignments(self, session: AsyncSession, where_clause=None, order_by_field: str = "assigned_at",
                                          order_by_direction: str = "desc", limit: int = 100, offset: int = 0, multiple: bool = False) -> RolePermission | ListPermissionAssignmentModel | None:
        """Helper to get permission assignments by a given where clause

        Args:
            session: Database session
            where_clause: Optional SQLAlchemy where clause for filtering
            order_by_field: Field to order by
            order_by_direction: Order direction (asc/desc)
            limit: Maximum number of records to return. Defaults to 100
            offset: The number of records to offset/skip aka pagination
            multiple: Whether to return multiple results or just the first one

        Returns:
            RolePermission, ListPermissionAssignmentModel, or None
        """
        statement = select(RolePermission)

        if where_clause is not None:
            statement = statement.where(where_clause)

        if order_by_field:
            # Map allowed fields to RolePermission attributes for ordering
            order_fields = {
                "role_id": RolePermission.role_id,
                "permission_id": RolePermission.permission_id,
                "assigned_at": RolePermission.assigned_at
            }
            order_field = order_fields.get(order_by_field, RolePermission.assigned_at)
            order_direction = desc if order_by_direction != "asc" else asc
            statement = statement.order_by(order_direction(order_field))

        if offset:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        result = await session.exec(statement)

        if multiple:
            # Get total count of permission assignments matching the where clause (without limit/offset)
            # Use func.count(1) since RolePermission has a composite primary key
            count_statement = select(func.count(1)).select_from(RolePermission)
            if where_clause is not None:
                count_statement = count_statement.where(where_clause)
            count_result = await session.exec(count_statement)
            total_assignments = count_result.one()

            # Return all permission assignments that match the sql query
            assignments = result.all()
            return ListPermissionAssignmentModel(limit=limit, offset=offset, total_assignments=total_assignments, current_assignments=len(assignments), assignments=assignments)
        else:
            # Return only the first permission assignment that matches the sql query
            return result.first()

    async def _create_permission_assignment(self, role_id: int, permission_id: int, session: AsyncSession) -> RolePermission:
        """Create a new permission assignment.

        Args:
            role_id: The role ID
            permission_id: The permission ID
            session: Database session

        Returns:
            The newly created RolePermission object
        """
        assignment = RolePermission(
            role_id=role_id, permission_id=permission_id)
        session.add(assignment)
        await session.commit()
        await session.refresh(assignment)
        return assignment

    async def _delete_permission_assignment(self, role_id: int, permission_id: int, session: AsyncSession) -> bool:
        """Delete a permission assignment.

        Args:
            role_id: The role ID
            permission_id: The permission ID
            session: Database session

        Returns:
            True if assignment was deleted, False if not found
        """
        query = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
        result = await session.exec(query)
        assignment = result.first()

        if assignment:
            await session.delete(assignment)
            await session.commit()
            return True
        return False

    async def _permission_assignment_exists(self, role_id: int, permission_id: int, session: AsyncSession) -> bool:
        """Check if a permission assignment already exists.

        Args:
            role_id: The role ID
            permission_id: The permission ID
            session: Database session

        Returns:
            True if assignment exists, False otherwise
        """
        where_clause = (RolePermission.role_id == role_id) & (
            RolePermission.permission_id == permission_id)
        assignment = await self._get_permission_assignments(
            session=session,
            where_clause=where_clause,
            multiple=False
        )
        return assignment is not None
