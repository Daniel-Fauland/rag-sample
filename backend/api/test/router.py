from fastapi import APIRouter
from models.test.request import TestRequest
from models.test.response import TestResponse
from core.test.service import TestService
from errors import XValueError

test_router = APIRouter()
service = TestService()


@test_router.post("/test", status_code=201, response_model=TestResponse)
async def test_route(request: TestRequest):
    try:
        message = await service.convert_string(**request.model_dump())
    except ValueError:
        raise XValueError
    return TestResponse(message=message, conversion_type=request.conversion_type)
