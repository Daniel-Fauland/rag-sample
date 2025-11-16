from fastapi import APIRouter, Depends, status, Query, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from core.permission.service import PermissionService
from models.auth import Permission, Type, Context
from auth.auth import PermissionChecker
from models.permission.request import PermissionCreateRequest, PermissionUpdateRequest
from models.permission.response import PermissionModelBase, PermissionModel, PermissionCreateResponse, ListPermissionResponse, ListPermissionWithRolesResponse
from database.session import get_session
from errors import PermissionNotFound, PermissionAlreadyExists, XValueError
from config import config


permission_router = APIRouter()
service = PermissionService()

# Permissions
read_permission_all = PermissionChecker(
    [Permission(type=Type.read, resource="permission", context=Context.all)])
create_permission_all = PermissionChecker(
    [Permission(type=Type.create, resource="permission", context=Context.all)])
update_permission_all = PermissionChecker(
    [Permission(type=Type.update, resource="permission", context=Context.all)])
delete_permission_all = PermissionChecker(
    [Permission(type=Type.delete, resource="permission", context=Context.all)])


@permission_router.post("", status_code=status.HTTP_201_CREATED, response_model=PermissionCreateResponse)
async def create_permission(permission_data: PermissionCreateRequest,
                            session: AsyncSession = Depends(get_session),
                            _: bool = Depends(create_permission_all)):
    """Create a new permission in the database <br />

    Args: <br />
        permission_data (PermissionCreateRequest): The data for the new permission to create <br />

    Returns: <br />
        PermissionCreateResponse: The created permission's id, type, resource, context and success flag <br />
    """
    # Check if permission with this combination already exists
    permission_exists = await service.permission_exists(
        type_value=permission_data.type.value,
        resource=permission_data.resource,
        context=permission_data.context.value,
        session=session
    )
    if permission_exists:
        raise PermissionAlreadyExists()

    # Create the new permission
    new_permission = await service.create_permission(permission_data=permission_data, session=session)
    return PermissionCreateResponse(
        id=new_permission.id,
        type=Type(new_permission.type),
        resource=new_permission.resource,
        context=Context(new_permission.context),
        success=True
    )


@permission_router.get("", status_code=status.HTTP_200_OK, response_model=ListPermissionResponse)
async def get_all_permissions(order_by_field: str = Query(
        None, description="The field to order the records by", example="id"),
        order_by_direction: str = Query(
        None, description="Whether to sort the field asc or desc", example="desc"),
        limit: int = Query(100,
                           description="The maximum number of records to return",
                           ge=1,
                           le=config.default_api_pagination_limit),
        offset: int = Query(0,
                            description="How many records to skip",
                            ge=0),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_permission_all)):
    """Get all permissions in the database <br />

    Returns: <br />
        ListPermissionResponse: The permission data without the associated roles with pagination metadata <br />
    """
    permissions = await service.get_permissions(session=session,
                                                include_roles=False,
                                                order_by_field=order_by_field,
                                                order_by_direction=order_by_direction,
                                                limit=limit,
                                                offset=offset)

    return permissions


@permission_router.get("-with-roles", status_code=status.HTTP_200_OK, response_model=ListPermissionWithRolesResponse)
async def get_all_permissions_with_roles(order_by_field: str = Query(
        None, description="The field to order the records by", example="id"),
        order_by_direction: str = Query(
        None, description="Whether to sort the field asc or desc", example="desc"),
        limit: int = Query(100,
                           description="The maximum number of records to return",
                           ge=1,
                           le=config.default_api_pagination_limit),
        offset: int = Query(0,
                            description="How many records to skip",
                            ge=0),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_permission_all)):
    """Get all permissions in the database <br />

    Returns: <br />
        ListPermissionWithRolesResponse: The permission data including the associated roles with pagination metadata <br />
    """
    permissions = await service.get_permissions(session=session,
                                                include_roles=True,
                                                order_by_field=order_by_field,
                                                order_by_direction=order_by_direction,
                                                limit=limit,
                                                offset=offset)

    return permissions


@permission_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=PermissionModel)
async def get_specific_permission(id: int = Path(..., description="The permission ID", example=1),
                                  session: AsyncSession = Depends(get_session),
                                  _: bool = Depends(read_permission_all)):
    """Get a specific permission in the database by ID <br />

    Returns: <br />
        PermissionModel: The permission data including the associated roles <br />
    """
    permission = await service.get_permission_by_id(id=id, session=session, include_roles=True)

    if not permission:
        raise PermissionNotFound
    return permission


@permission_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=PermissionModelBase)
async def update_permission(id: int = Path(..., description="The permission ID to update", example=1),
                            update_data: PermissionUpdateRequest = None,
                            session: AsyncSession = Depends(get_session),
                            _: bool = Depends(update_permission_all)):
    """Update a specific permission in the database by ID <br />

    Args: <br />
        id: The permission ID to update <br />
        update_data: The permission data to update (all fields optional for PATCH-like behavior) <br />

    Returns: <br />
        PermissionModelBase: The updated permission data <br />
    """
    # Convert Pydantic model to dict, excluding None values
    update_dict = update_data.model_dump(
        exclude_none=True) if update_data else {}

    if not update_dict:
        raise XValueError("No fields provided for update")

    # Update the permission
    updated_permission = await service.update_permission(id=id, update_data=update_dict, session=session)

    if not updated_permission:
        raise PermissionNotFound

    # Return the updated permission without roles for simplicity
    return updated_permission


@permission_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(id: int = Path(..., description="The permission ID to delete", example=1),
                            session: AsyncSession = Depends(get_session),
                            _: bool = Depends(delete_permission_all)):
    """Delete a specific permission from the database by ID <br />

    Returns: <br />
        204 No Content: Permission successfully deleted <br />
    """
    permission_deleted = await service.delete_permission(id=id, session=session)

    if not permission_deleted:
        raise PermissionNotFound
