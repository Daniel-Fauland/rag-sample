from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence, Optional
from database.schemas.role_permissions import RolePermission
from models.permission_assignment.request import PermissionAssignmentCreateRequest, PermissionAssignmentDeleteRequest
from core.permission_assignment.helper import PermissionAssignmentServiceHelper
from core.role.service import RoleService
from core.permission.service import PermissionService
from errors import RoleNotFound, PermissionNotFound, PermissionAssignmentAlreadyExists

service_helper = PermissionAssignmentServiceHelper()
role_service = RoleService()
permission_service = PermissionService()


class PermissionAssignmentService:
    """Service for managing permission assignments (role-permission relationships)."""

    async def get_permission_assignments(self, session: AsyncSession, role_id: Optional[int] = None,
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
            A sequence of RolePermission objects from the role_permissions table
        """
        return await service_helper._get_permission_assignments(
            session=session, role_id=role_id, permission_id=permission_id,
            order_by_field=order_by_field, order_by_direction=order_by_direction, limit=limit
        )

    async def create_permission_assignment(self, assignment_data: PermissionAssignmentCreateRequest,
                                           session: AsyncSession) -> RolePermission:
        """Create a new permission assignment.

        Args:
            assignment_data: The permission assignment data containing role_id and permission_id
            session: Database session

        Returns:
            RolePermission: The newly created permission assignment

        Raises:
            RoleNotFound: If role doesn't exist
            PermissionNotFound: If permission doesn't exist
            PermissionAssignmentAlreadyExists: If assignment already exists
        """
        role_id = assignment_data.role_id
        permission_id = assignment_data.permission_id

        # Check if role exists
        role = await role_service.get_role_by_id(role_id, session)
        if not role:
            raise RoleNotFound()

        # Check if permission exists
        permission = await permission_service.get_permission_by_id(permission_id, session)
        if not permission:
            raise PermissionNotFound()

        # Check if assignment already exists
        if await service_helper._permission_assignment_exists(role_id, permission_id, session):
            raise PermissionAssignmentAlreadyExists()

        return await service_helper._create_permission_assignment(role_id, permission_id, session)

    async def delete_permission_assignment(self, assignment_data: PermissionAssignmentDeleteRequest,
                                           session: AsyncSession) -> bool:
        """Delete a permission assignment.

        Args:
            assignment_data: The permission assignment data containing role_id and permission_id
            session: Database session

        Returns:
            bool: True if assignment was deleted, False if not found
        """
        return await service_helper._delete_permission_assignment(
            assignment_data.role_id, assignment_data.permission_id, session
        )
