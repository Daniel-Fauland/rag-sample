import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserModelBase(BaseModel):
    id: uuid.UUID = Field(..., description="The user id")
    email: str = Field(..., description="The email of the newly created user", examples=[
                       "john.doe@example.com"])
    password_hash: str = Field(exclude=True)
    first_name: str = Field(..., description="The users first name", examples=[
                            "John"])
    last_name: str = Field(..., description="The users last name", examples=[
                           "Doe"])
    is_verified: bool = Field(..., description="Whether the user is verified", examples=[
                              True])
    account_type: str = Field(..., description="Wheter the user account was created locally on the database or via SSO (e.g. Google Auth)", examples=[
                              "local"])
    created_at: datetime = Field(...,
                                 description="A timestamp when the user was created")
    modified_at: datetime = Field(...,
                                  description="A timestamp when the user was last modified")


class PermissionModelBase(BaseModel):
    id: int = Field(..., description="The permission id", examples=[3])
    type: str = Field(..., description="The type of operation. Can either be read, write, update or delete",
                      examples=["update"])
    resource: str = Field(..., description="The referenced resource", examples=[
                          "user"])
    context: str = Field(..., description="The context of the action", examples=[
                         "me"])
    is_active: bool = Field(
        ..., description="Whether the permission can be currently used in the application", examples=[True])


class PermissionModel(PermissionModelBase):
    description: str = Field(..., description="The description of the permission", examples=[
                             "Update own user"])
    created_at: datetime = Field(...,
                                 description="When the permission was initally created")


class RoleModelBase(BaseModel):
    id: int = Field(..., description="The role id", examples=[2])
    name: str = Field(..., description="The name of the role",
                      examples=["user"])
    is_active: bool = Field(
        ..., description="Whether the role can be currently used in the application", examples=[True])


class RoleModelPermissionBase(RoleModelBase):
    permissions: list["PermissionModelBase"]


class RoleModel(RoleModelBase):
    description: str = Field(..., description="The description of the role", examples=[
                             "Default role with limited permissions"])
    created_at: datetime = Field(...,
                                 description="When the role was initally created")


class UserModel(UserModelBase):
    roles: Optional[list["RoleModelPermissionBase"]] = None


class SignupResponse(BaseModel):
    email: str = Field(..., description="The email of the newly created user", examples=[
                       "john.doe@example.com"])
    success: bool = Field(..., description="Wheter the user was successfully created", examples=[
        True])


class BatchSignupResponseBase(SignupResponse):
    reason: Optional[str] = Field(..., description="The reason why a signup failed", examples=[
                                  "User does already exist in the database"])


class BatchSignupResponse(BaseModel):
    result: list[BatchSignupResponseBase]


class SigninRefreshModelBase(BaseModel):
    access_token: str = Field(..., description="The access JWT", examples=[
        "eyJhbG..."])
    refresh_token: str = Field(..., description="The refresh JWT", examples=[
        "eyJhbG..."])


class SigninResponse(SigninRefreshModelBase):
    message: str = Field(..., description="A status message about the login", examples=[
                         "Login successful"])


class RefreshResponse(SigninRefreshModelBase):
    message: str = Field(..., description="A status message about the login", examples=[
                         "Refresh successful"])


class PasswordUpdateResponse(BaseModel):
    message: str = Field(..., description="A status message about the password change", examples=[
                         "Password changed successfully"])
