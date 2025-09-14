from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class RoleModelBase(BaseModel):
    id: int = Field(..., description="The role id", examples=[2])
    name: str = Field(..., description="The name of the role",
                      examples=["user"])
    description: Optional[str] = Field(None, description="The description of the role",
                                       examples=["Default role with limited permissions"])
    is_active: bool = Field(..., description="Whether the role can be currently used in the application",
                            examples=[True])
    created_at: datetime = Field(...,
                                 description="When the role was initially created")


class PermissionModelBase(BaseModel):
    id: int = Field(..., description="The permission id", examples=[3])
    type: str = Field(..., description="The type of operation. Can either be read, write, update or delete",
                      examples=["update"])
    resource: str = Field(..., description="The referenced resource", examples=[
                          "user"])
    context: str = Field(..., description="The context of the action", examples=[
                         "me"])
    description: Optional[str] = Field(None, description="The description of the permission",
                                       examples=["Update own user"])
    is_active: bool = Field(..., description="Whether the permission can be currently used in the application",
                            examples=[True])
    created_at: datetime = Field(...,
                                 description="When the permission was initially created")


class RoleModel(RoleModelBase):
    permissions: Optional[list["PermissionModelBase"]] = None


class RoleCreateResponse(BaseModel):
    id: int = Field(..., description="The id of the newly created role", examples=[
                    3])
    name: str = Field(..., description="The name of the newly created role", examples=[
                      "admin"])
    success: bool = Field(..., description="Whether the role was successfully created", examples=[
                          True])


class RoleUpdateResponse(BaseModel):
    message: str = Field(..., description="A status message about the role update",
                         examples=["Role updated successfully"])
