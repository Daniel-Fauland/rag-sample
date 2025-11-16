from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from core.role_assignment.service import RoleAssignmentService
from models.auth import Permission, Type, Context
from auth.auth import PermissionChecker, get_current_user, check_ownership_permissions
from models.role_assignment.request import RoleAssignmentCreateRequest, RoleAssignmentDeleteRequest
from models.role_assignment.response import RoleAssignmentCreateResponse, ListRoleAssignmentResponse
from models.user.response import UserModel
from database.session import get_session
from errors import RoleAssignmentNotFound
from config import config


role_assignment_router = APIRouter()
service = RoleAssignmentService()

# Permissions
create_role_assignment_all = PermissionChecker(
    [Permission(type=Type.create, resource="role_assignment", context=Context.all)])
delete_role_assignment_all = PermissionChecker(
    [Permission(type=Type.delete, resource="role_assignment", context=Context.all)])


@role_assignment_router.get("", status_code=status.HTTP_200_OK, response_model=ListRoleAssignmentResponse)
async def get_role_assignments(
        user_id: str | None = Query(
            None, description="Filter by user ID"),
        role_id: Optional[int] = Query(None, description="Filter by role ID"),
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
        current_user: UserModel = Depends(get_current_user)):
    """Get all role assignments with optional filtering <br />

    Returns: <br />
        ListRoleAssignmentResponse: List of role assignments with optional user/role details and pagination metadata <br />
    """
    # Check permissions based on whether user is requesting their own data or all data
    if user_id is not None:
        # User is filtering by a specific user_id, check if it's their own
        check_ownership_permissions(
            current_user=current_user,
            target_id=user_id,
            own_data_permissions=[Permission(
                type=Type.read, resource="role_assignment", context=Context.me)],
            other_data_permissions=[Permission(
                type=Type.read, resource="role_assignment", context=Context.all)]
        )
    else:
        # User is requesting all role assignments, requires "all" permission
        checker = PermissionChecker(
            [Permission(type=Type.read, resource="role_assignment", context=Context.all)])
        checker(current_user)

    assignments = await service.get_role_assignments(
        session=session,
        user_id=user_id,
        role_id=role_id,
        order_by_field=order_by_field,
        order_by_direction=order_by_direction,
        limit=limit,
        offset=offset
    )

    return assignments


@role_assignment_router.post("", status_code=status.HTTP_201_CREATED, response_model=RoleAssignmentCreateResponse)
async def create_role_assignment(assignment_data: RoleAssignmentCreateRequest,
                                 session: AsyncSession = Depends(get_session),
                                 _: bool = Depends(create_role_assignment_all)):
    """Create a new role assignment between a user and role <br />

    Args: <br />
        assignment_data (RoleAssignmentCreateRequest): The user ID and role ID to assign <br />

    Returns: <br />
        RoleAssignmentCreateResponse: The created assignment details and success status <br />
    """
    new_assignment = await service.create_role_assignment(assignment_data=assignment_data, session=session)
    return RoleAssignmentCreateResponse(
        user_id=new_assignment.user_id,
        role_id=new_assignment.role_id,
        success=True,
        message="Role assigned successfully"
    )


@role_assignment_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_assignment(assignment_data: RoleAssignmentDeleteRequest,
                                 session: AsyncSession = Depends(get_session),
                                 _: bool = Depends(delete_role_assignment_all)):
    """Delete a role assignment between a user and role <br />

    Args: <br />
        assignment_data (RoleAssignmentDeleteRequest): The user ID and role ID to unassign <br />

    Returns: <br />
        204 No Content: Role assignment successfully removed <br />
    """
    assignment_deleted = await service.delete_role_assignment(assignment_data=assignment_data, session=session)

    if not assignment_deleted:
        raise RoleAssignmentNotFound()
