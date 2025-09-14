from typing import Optional
from pydantic import BaseModel, Field
from models.auth import Type, Context


class PermissionCreateRequest(BaseModel):
    """Request model for creating a new permission."""
    type: Type = Field(..., description="The permission type/action",
                       examples=[Type.read])
    resource: str = Field(..., description="The resource the permission applies to", examples=[
                          "user"])
    context: Context = Field(
        Context.all, description="The context/scope of the permission", examples=[Context.all])
    description: Optional[str] = Field(None, description="The permission description",
                                       examples=["Allows reading user data"])


class PermissionUpdateRequest(BaseModel):
    """Request model for updating permission information. All fields are optional to support PATCH-like behavior."""
    type: Optional[Type] = Field(
        None, description="The permission type/action", examples=[Type.update])
    resource: Optional[str] = Field(
        None, description="The resource the permission applies to", examples=["role"])
    context: Optional[Context] = Field(
        None, description="The context/scope of the permission", examples=[Context.me])
    description: Optional[str] = Field(None, description="The permission description",
                                       examples=["Allows updating role data"])
    is_active: Optional[bool] = Field(
        None, description="Whether the permission is active", examples=[True])
