from fastapi import APIRouter, Depends, status, Query, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from core.role.service import RoleService
from models.auth import Permission, Type, Context
from auth.auth import PermissionChecker
from models.role.request import RoleCreateRequest, RoleUpdateRequest
from models.role.response import RoleModelBase, RoleModel, RoleCreateResponse
from database.session import get_session
from errors import RoleNotFound, RoleAlreadyExists, XValueError


role_router = APIRouter()
service = RoleService()

# Permissions
read_role_all = PermissionChecker(
    [Permission(type=Type.read, resource="role", context=Context.all)])
create_role_all = PermissionChecker(
    [Permission(type=Type.create, resource="role", context=Context.all)])
update_role_all = PermissionChecker(
    [Permission(type=Type.update, resource="role", context=Context.all)])
delete_role_all = PermissionChecker(
    [Permission(type=Type.delete, resource="role", context=Context.all)])


@role_router.post("", status_code=status.HTTP_201_CREATED, response_model=RoleCreateResponse)
async def create_role(role_data: RoleCreateRequest,
                      session: AsyncSession = Depends(get_session),
                      _: bool = Depends(create_role_all)):
    """Create a new role in the database <br />

    Args: <br />
        role_data (RoleCreateRequest): The data for the new role to create <br />

    Returns: <br />
        RoleCreateResponse: The created role's id, name and success flag <br />
    """
    # Check if role with this name already exists
    role_exists = await service.role_exists(name=role_data.name, session=session)
    if role_exists:
        raise RoleAlreadyExists()

    # Create the new role
    new_role = await service.create_role(role_data=role_data, session=session)
    return RoleCreateResponse(id=new_role.id, name=new_role.name, success=True)


@role_router.get("", status_code=status.HTTP_200_OK, response_model=list[RoleModelBase])
async def get_all_roles(order_by_field: str = Query(
        None, description="The field to order the records by", example="id"),
        order_by_direction: str = Query(
        None, description="Whether to sort the field asc or desc", example="desc"),
        limit: int = Query(None,
                           description="The maximum number of records to return"),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_role_all)):
    """Get all roles in the database <br />

    Returns: <br />
        list[RoleModelBase]: The role data without the associated permissions <br />
    """
    roles = await service.get_roles(session=session,
                                    include_permissions=False,
                                    order_by_field=order_by_field,
                                    order_by_direction=order_by_direction,
                                    limit=limit)

    return roles


@role_router.get("-with-permissions", status_code=status.HTTP_200_OK, response_model=list[RoleModel])
async def get_all_roles_with_permissions(order_by_field: str = Query(
        None, description="The field to order the records by", example="id"),
        order_by_direction: str = Query(
        None, description="Whether to sort the field asc or desc", example="desc"),
        limit: int = Query(None,
                           description="The maximum number of records to return"),
        session: AsyncSession = Depends(get_session),
        _: bool = Depends(read_role_all)):
    """Get all roles in the database <br />

    Returns: <br />
        list[RoleModel]: The role data including the associated permissions <br />
    """
    roles = await service.get_roles(session=session,
                                    include_permissions=True,
                                    order_by_field=order_by_field,
                                    order_by_direction=order_by_direction,
                                    limit=limit)

    return roles


@role_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=RoleModel)
async def get_specific_role(id: int = Path(..., description="The role ID", example=1),
                            session: AsyncSession = Depends(get_session),
                            _: bool = Depends(read_role_all)):
    """Get a specific role in the database by ID <br />

    Returns: <br />
        RoleModel: The role data including the associated permissions <br />
    """
    role = await service.get_role_by_id(id=id, session=session, include_permissions=True)

    if not role:
        raise RoleNotFound
    return role


@role_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=RoleModelBase)
async def update_role(id: int = Path(..., description="The role ID to update", example=1),
                      update_data: RoleUpdateRequest = None,
                      session: AsyncSession = Depends(get_session),
                      _: bool = Depends(update_role_all)):
    """Update a specific role in the database by ID <br />

    Args: <br />
        id: The role ID to update <br />
        update_data: The role data to update (all fields optional for PATCH-like behavior) <br />

    Returns: <br />
        RoleModel: The updated role data including the associated permissions <br />
    """
    # Convert Pydantic model to dict, excluding None values
    update_dict = update_data.model_dump(
        exclude_none=True) if update_data else {}

    if not update_dict:
        raise XValueError("No fields provided for update")

    # Update the role
    updated_role = await service.update_role(id=id, update_data=update_dict, session=session)

    if not updated_role:
        raise RoleNotFound

    # Return the updated role with permissions
    return await service.get_role_by_id(id=updated_role.id, session=session, include_permissions=True)


@role_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(id: int = Path(..., description="The role ID to delete", example=2),
                      session: AsyncSession = Depends(get_session),
                      _: bool = Depends(delete_role_all)):
    """Delete a specific role from the database by ID <br />

    Returns: <br />
        204 No Content: Role successfully deleted <br />
    """
    role_deleted = await service.delete_role(id=id, session=session)

    if not role_deleted:
        raise RoleNotFound
