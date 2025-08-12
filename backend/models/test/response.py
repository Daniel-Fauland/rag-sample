from pydantic import BaseModel


class TestResponse(BaseModel):
    message: str
