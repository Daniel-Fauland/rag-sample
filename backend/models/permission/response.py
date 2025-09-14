from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from models.auth import Type, Context


class PermissionModelBase(BaseModel):
    id: int = Field(..., description="The permission id", examples=[3])
    type: Type = Field(..., description="The type of operation",
                       examples=[Type.update])
    resource: str = Field(..., description="The referenced resource", examples=[
                          "user"])
    context: Context = Field(..., description="The context of the action", examples=[
                             Context.me])
    description: Optional[str] = Field(None, description="The description of the permission",
                                       examples=["Update own user"])
    is_active: bool = Field(..., description="Whether the permission can be currently used in the application",
                            examples=[True])
    created_at: datetime = Field(...,
                                 description="When the permission was initially created")


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


class PermissionModel(PermissionModelBase):
    roles: Optional[list["RoleModelBase"]] = None


class PermissionCreateResponse(BaseModel):
    id: int = Field(..., description="The id of the newly created permission", examples=[
                    4])
    type: Type = Field(..., description="The type of the newly created permission", examples=[
                       Type.create])
    resource: str = Field(..., description="The resource of the newly created permission", examples=[
                          "permission"])
    context: Context = Field(..., description="The context of the newly created permission", examples=[
                             Context.all])
    success: bool = Field(..., description="Whether the permission was successfully created", examples=[
                          True])


class PermissionUpdateResponse(BaseModel):
    message: str = Field(..., description="A status message about the permission update",
                         examples=["Permission updated successfully"])
