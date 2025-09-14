from typing import Optional
from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    """Request model for creating a new role."""
    name: str = Field(..., description="The role name", examples=["test"])
    description: Optional[str] = Field(None, description="The role description",
                                       examples=["Test role description"])


class RoleUpdateRequest(BaseModel):
    """Request model for updating role information. All fields are optional to support PATCH-like behavior."""
    name: Optional[str] = Field(
        None, description="The role name", examples=["user"])
    description: Optional[str] = Field(None, description="The role description",
                                       examples=["Default role with limited permissions"])
    is_active: Optional[bool] = Field(
        None, description="Whether the role is active", examples=[True])
