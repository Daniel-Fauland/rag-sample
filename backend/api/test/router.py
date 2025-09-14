from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from models.test.request import TestRequest
from models.test.response import TestResponse
from models.auth import Permission, Type, Context
from auth.auth import PermissionChecker, RoleChecker
from core.test.service import TestService
from errors import XValueError

test_router = APIRouter()
service = TestService()

# Permissions
read_user_all = PermissionChecker(
    [Permission(type=Type.read, resource="user", context=Context.all)])
create_user_me_create_role_all = PermissionChecker(
    [Permission(type=Type.create, resource="user", context=Context.me),
     Permission(type=Type.create, resource="role", context=Context.all)])
role_admin = RoleChecker([])


@test_router.post("/string-conversion", status_code=status.HTTP_201_CREATED, response_model=TestResponse)
async def test_route(request: TestRequest):
    try:
        message = await service.convert_string(**request.model_dump())
    except ValueError:
        raise XValueError(
            f"Unsupported conversion_type: {request.conversion_type}")
    return TestResponse(message=message, conversion_type=request.conversion_type)


@test_router.get("/test-read-user-all-permission", status_code=status.HTTP_200_OK)
async def test_user_role(_: bool = Depends(read_user_all)) -> JSONResponse:
    return JSONResponse(content={"message": "you will only see this if you have the 'read:user:all' permission."}, status_code=200)


@test_router.get("/test-create-user-me-create-role-all-permission", status_code=200)
async def test_user_role2(_: bool = Depends(create_user_me_create_role_all)) -> JSONResponse:
    return JSONResponse(content={"message": "you will only see this if you have the 'create:user:me' & 'create:role:all' permission."}, status_code=200)


@test_router.get("/test-admin-role", status_code=status.HTTP_200_OK)
async def test_admin_role(_: bool = Depends(role_admin)) -> JSONResponse:
    return JSONResponse(content={"message": "you will only see this if you have the 'admin' role."}, status_code=200)
