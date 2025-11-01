import uuid
from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from database.schemas.user_roles import UserRole
from typing import Sequence


class RoleAssignmentServiceHelper:
    async def _get_role_assignments(self, session: AsyncSession, where_clause=None, order_by_field: str = None,
                                    order_by_direction: str = "desc", limit: int = None, multiple: bool = False) -> UserRole | Sequence[UserRole] | None:
        """Helper to get role assignments by a given where clause"""

        statement = select(UserRole)
        if where_clause is not None:
            statement = statement.where(where_clause)
        if order_by_field:
            # Map allowed fields to UserRole attributes for ordering
            order_fields = {
                "user_id": UserRole.user_id,
                "role_id": UserRole.role_id,
                "assigned_at": UserRole.assigned_at
            }
            order_field = order_fields.get(
                order_by_field, UserRole.assigned_at)
            order_direction = desc if order_by_direction != "asc" else asc
            statement = statement.order_by(order_direction(order_field))
        if limit:
            statement = statement.limit(limit)

        result = await session.exec(statement)
        if multiple:
            # Return all role assignments that match the sql query
            assignments = result.all()
        else:
            # Return only the first role assignment that matches the sql query
            assignments = result.first()
        return assignments

    async def _create_role_assignment(self, user_id: uuid.UUID, role_id: int, session: AsyncSession) -> UserRole:
        """Helper to create a new role assignment in the database"""
        new_assignment = UserRole(user_id=user_id, role_id=role_id)
        session.add(new_assignment)
        await session.commit()
        await session.refresh(new_assignment)
        return new_assignment

    async def _delete_role_assignment(self, session: AsyncSession, where_clause) -> bool:
        """Helper to delete a role assignment by a given where clause"""
        try:
            # First check if role assignment exists
            assignment = await self._get_role_assignments(session=session, where_clause=where_clause)
            if not assignment:
                return False

            # Delete the role assignment
            await session.delete(assignment)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e

    async def _role_assignment_exists(self, user_id: uuid.UUID, role_id: int, session: AsyncSession) -> bool:
        """Check if a role assignment already exists"""
        assignment = await self._get_role_assignments(
            session=session,
            where_clause=(UserRole.user_id == user_id) & (
                UserRole.role_id == role_id)
        )
        return assignment is not None
