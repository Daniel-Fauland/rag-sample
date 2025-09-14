from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence, Optional
from database.schemas.role_permissions import RolePermission


class PermissionAssignmentServiceHelper:
    """Helper class for permission assignment database operations."""

    async def _get_permission_assignments(self, session: AsyncSession, role_id: Optional[int] = None,
                                          permission_id: Optional[int] = None, order_by_field: str = "assigned_at",
                                          order_by_direction: str = "desc", limit: int = None) -> Sequence[RolePermission]:
        """Get permission assignments with optional filtering.

        Args:
            session: Database session
            role_id: Optional role ID to filter by
            permission_id: Optional permission ID to filter by
            order_by_field: Field to order by
            order_by_direction: Order direction (asc/desc)
            limit: Maximum number of records to return

        Returns:
            Sequence of RolePermission objects from the role_permissions table
        """
        query = select(RolePermission)

        # Apply filters
        if role_id is not None:
            query = query.where(RolePermission.role_id == role_id)
        if permission_id is not None:
            query = query.where(RolePermission.permission_id == permission_id)

        # Apply ordering
        if hasattr(RolePermission, order_by_field):
            order_column = getattr(RolePermission, order_by_field)
            if order_by_direction.lower() == "asc":
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())

        # Apply limit
        if limit:
            query = query.limit(limit)

        result = await session.exec(query)
        return result.all()

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
        query = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
        result = await session.exec(query)
        return result.first() is not None
