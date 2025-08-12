from fastapi import APIRouter, Query
from utils.helper import Utils
from errors import FilePathNotFoundError
from models.test.response import TestResponse

test_router = APIRouter()


@test_router.get("/test/", status_code=200, response_model=TestResponse)
async def test_utils(request: str = Query(..., description="The path to the file to read", example="./Readme.md")):
    try:
        file_content = await Utils.file_to_str(request)
    except FileNotFoundError:
        raise FilePathNotFoundError()
    except Exception as e:
        raise e
    return TestResponse(message=file_content)
