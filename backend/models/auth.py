from enum import Enum
from pydantic import BaseModel


class Type(str, Enum):
    # The type / action to take
    read = "read"
    write = "write"
    update = "update"
    delete = "delete"


class Resource(str, Enum):
    # The affected resource
    admin = "admin"
    user = "user"
    roles = "role"
    permissions = "permission"
    # add more as needed


class Context(str, Enum):
    # The context / scope
    me = "me"
    all = "all"


class Permission(BaseModel):
    type: Type
    resource: Resource
    context: Context = Context.all
