from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from core.permission_assignment.service import PermissionAssignmentService
from models.auth import Permission, Type, Context
from auth.auth import PermissionChecker
from models.permission_assignment.request import PermissionAssignmentCreateRequest, PermissionAssignmentDeleteRequest
from models.permission_assignment.response import PermissionAssignmentCreateResponse, ListPermissionAssignmentResponse
from database.session import get_session
from errors import PermissionAssignmentNotFound
from config import config


permission_assignment_router = APIRouter()
service = PermissionAssignmentService()

# Permissions
read_permission_assignment_all = PermissionChecker(
    [Permission(type=Type.read, resource="permission_assignment", context=Context.all)])
create_permission_assignment_all = PermissionChecker(
    [Permission(type=Type.create, resource="permission_assignment", context=Context.all)])
delete_permission_assignment_all = PermissionChecker(
    [Permission(type=Type.delete, resource="permission_assignment", context=Context.all)])


@permission_assignment_router.get("", status_code=status.HTTP_200_OK, response_model=ListPermissionAssignmentResponse)
async def get_permission_assignments(
        role_id: Optional[int] = Query(None, description="Filter by role ID"),
        permission_id: Optional[int] = Query(
            None, description="Filter by permission ID"),
        order_by_field: str = Query(
            "assigned_at", description="The field to order the records by"),
        order_by_direction: str = Query(
            "desc", description="Whether to sort the field asc or desc"),
        limit: int = Query(100,
                           description="The maximum number of records to return",
                           ge=1,
                           le=config.default_api_pagination_limit),
        offset: int = Query(0,
                            description="How many records to skip",
                            ge=0),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_permission_assignment_all)):
    """Get all permission assignments (role-permission relationships) in the database with optional filtering. <br />

    Args: <br />
        role_id: Optional role ID to filter assignments for a specific role <br />
        permission_id: Optional permission ID to filter assignments for a specific permission <br />
        order_by_field: The field to order the records by <br />
        order_by_direction: Whether to sort the field asc or desc <br />
        limit: The maximum number of records to return <br />
        offset: How many records to skip <br />

    Returns: <br />
        ListPermissionAssignmentResponse: List of permission assignments with role and permission details and pagination metadata <br />
    """

    assignments = await service.get_permission_assignments(
        session=session, role_id=role_id, permission_id=permission_id,
        order_by_field=order_by_field, order_by_direction=order_by_direction, limit=limit, offset=offset
    )

    return assignments


@permission_assignment_router.post("", status_code=status.HTTP_201_CREATED, response_model=PermissionAssignmentCreateResponse)
async def create_permission_assignment(assignment_data: PermissionAssignmentCreateRequest,
                                       session: AsyncSession = Depends(
                                           get_session),
                                       _: bool = Depends(create_permission_assignment_all)):
    """Create a new permission assignment between a role and permission. <br />

    Args: <br />
        assignment_data (PermissionAssignmentCreateRequest): The role ID and permission ID to assign <br />

    Returns: <br />
        PermissionAssignmentCreateResponse: The created assignment details and success status <br />
    """
    new_assignment = await service.create_permission_assignment(assignment_data=assignment_data, session=session)
    return PermissionAssignmentCreateResponse(
        role_id=new_assignment.role_id,
        permission_id=new_assignment.permission_id,
        success=True,
        message="Permission assigned successfully"
    )


@permission_assignment_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_assignment(assignment_data: PermissionAssignmentDeleteRequest,
                                       session: AsyncSession = Depends(
                                           get_session),
                                       _: bool = Depends(delete_permission_assignment_all)):
    """Delete a permission assignment between a role and permission. <br />

    Args: <br />
        assignment_data (PermissionAssignmentDeleteRequest): The role ID and permission ID to unassign <br />

    Returns: <br />
        204 No Content: Permission assignment successfully removed <br />
    """
    deleted = await service.delete_permission_assignment(assignment_data=assignment_data, session=session)

    if not deleted:
        raise PermissionAssignmentNotFound()
