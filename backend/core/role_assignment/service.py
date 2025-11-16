import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from database.schemas.user_roles import UserRole
from models.role_assignment.request import RoleAssignmentCreateRequest, RoleAssignmentDeleteRequest
from models.role_assignment.response import ListRoleAssignmentModel
from core.role_assignment.helper import RoleAssignmentServiceHelper
from core.user.service import UserService
from core.role.service import RoleService
from errors import UserNotFound, RoleNotFound, RoleAssignmentAlreadyExists

service_helper = RoleAssignmentServiceHelper()
user_service = UserService()
role_service = RoleService()


class RoleAssignmentService:
    async def get_role_assignments(self, session: AsyncSession, user_id: Optional[uuid.UUID] = None,
                                   role_id: Optional[int] = None, order_by_field: str = "assigned_at",
                                   order_by_direction: str = "desc", limit: int = 100, offset: int = 0) -> ListRoleAssignmentModel:
        """Get role assignments with optional filtering by user_id and/or role_id

        Args:
            session: Database session
            user_id: Optional filter by user ID
            role_id: Optional filter by role ID
            order_by_field: Field to order by (default: assigned_at)
            order_by_direction: Order direction (asc/desc)
            limit: Maximum number of records to return. Defaults to 100
            offset: The number of records to offset/skip aka pagination

        Returns:
            ListRoleAssignmentModel
        """
        # Build where clause based on filters
        where_clause = None
        if user_id and role_id:
            where_clause = (UserRole.user_id == user_id) & (
                UserRole.role_id == role_id)
        elif user_id:
            where_clause = UserRole.user_id == user_id
        elif role_id:
            where_clause = UserRole.role_id == role_id

        return await service_helper._get_role_assignments(
            session=session,
            where_clause=where_clause,
            order_by_field=order_by_field,
            order_by_direction=order_by_direction,
            limit=limit,
            offset=offset,
            multiple=True
        )

    async def create_role_assignment(self, assignment_data: RoleAssignmentCreateRequest,
                                     session: AsyncSession) -> UserRole:
        """Create a new role assignment

        Args:
            assignment_data: Role assignment creation data
            session: Database session

        Returns:
            UserRole: The newly created role assignment

        Raises:
            UserNotFound: If user doesn't exist
            RoleNotFound: If role doesn't exist
            RoleAssignmentAlreadyExists: If assignment already exists
        """
        user_id = assignment_data.user_id
        role_id = assignment_data.role_id

        # Check if user exists
        user = await user_service.get_user_by_id(user_id, session)
        if not user:
            raise UserNotFound()

        # Check if role exists
        role = await role_service.get_role_by_id(role_id, session)
        if not role:
            raise RoleNotFound()

        # Check if assignment already exists
        if await service_helper._role_assignment_exists(user_id, role_id, session):
            raise RoleAssignmentAlreadyExists()

        return await service_helper._create_role_assignment(user_id, role_id, session)

    async def delete_role_assignment(self, assignment_data: RoleAssignmentDeleteRequest,
                                     session: AsyncSession) -> bool:
        """Delete a role assignment

        Args:
            assignment_data: Role assignment deletion data
            session: Database session

        Returns:
            bool: True if assignment was deleted, False if it didn't exist
        """
        user_id = assignment_data.user_id
        role_id = assignment_data.role_id

        where_clause = (UserRole.user_id == user_id) & (
            UserRole.role_id == role_id)
        return await service_helper._delete_role_assignment(session=session, where_clause=where_clause)

    async def role_assignment_exists(self, user_id: uuid.UUID, role_id: int, session: AsyncSession) -> bool:
        """Check if a role assignment exists

        Args:
            user_id: User ID
            role_id: Role ID
            session: Database session

        Returns:
            bool: True if assignment exists, False otherwise
        """
        return await service_helper._role_assignment_exists(user_id, role_id, session)
