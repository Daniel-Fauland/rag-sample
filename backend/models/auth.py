from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Type(str, Enum):
    # The type/action to take
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"


class Context(str, Enum):
    # The context/scope
    me = "me"
    all = "all"


class Permission(BaseModel):
    type: Type
    resource: str = Field(...,
                          description="The resource the permission is for")
    context: Context = Context.all

    @field_validator('resource')
    @classmethod
    def resource_lower_case(cls, v: str) -> str:
        return v.lower()
