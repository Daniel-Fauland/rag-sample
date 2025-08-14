from pydantic import BaseModel


class TestResponse(BaseModel):
    conversion_type: str
    message: str
