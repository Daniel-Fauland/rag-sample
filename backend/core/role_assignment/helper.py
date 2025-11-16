import uuid
from sqlmodel import select, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from database.schemas.user_roles import UserRole
from models.role_assignment.response import ListRoleAssignmentModel


class RoleAssignmentServiceHelper:
    async def _get_role_assignments(self, session: AsyncSession, where_clause=None, order_by_field: str = None,
                                    order_by_direction: str = "desc", limit: int = 100, offset: int = 0, multiple: bool = False) -> UserRole | ListRoleAssignmentModel | None:
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
        if offset:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        result = await session.exec(statement)
        if multiple:
            # Get total count of role assignments matching the where clause (without limit/offset)
            # Use func.count(1) since UserRole has a composite primary key
            count_statement = select(func.count(1)).select_from(UserRole)
            if where_clause is not None:
                count_statement = count_statement.where(where_clause)
            count_result = await session.exec(count_statement)
            total_assignments = count_result.one()

            # Return all role assignments that match the sql query
            assignments = result.all()
            return ListRoleAssignmentModel(limit=limit, offset=offset, total_assignments=total_assignments, current_assignments=len(assignments), assignments=assignments)
        else:
            # Return only the first role assignment that matches the sql query
            return result.first()

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
