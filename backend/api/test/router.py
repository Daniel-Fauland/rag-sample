from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.test.request import TestRequest
from models.test.response import TestResponse
from core.test.service import TestService
from errors import XValueError
from auth.auth import RoleChecker

test_router = APIRouter()
service = TestService()
role_user = RoleChecker(['user'])
role_admin = RoleChecker([])


@test_router.post("/string-conversion", status_code=201, response_model=TestResponse)
async def test_route(request: TestRequest):
    try:
        message = await service.convert_string(**request.model_dump())
    except ValueError:
        raise XValueError
    return TestResponse(message=message, conversion_type=request.conversion_type)


@test_router.get("/test-user-role", status_code=200)
async def test_user_role(_: bool = Depends(role_user)) -> JSONResponse:
    return JSONResponse(content={"message": "you should only see this if you have the 'user' or 'admin' role."}, status_code=200)


@test_router.get("/test-admin-role", status_code=200)
async def test_admin_role(_: bool = Depends(role_admin)) -> JSONResponse:
    return JSONResponse(content={"message": "you should only see this if you have the 'admin' role."}, status_code=200)
