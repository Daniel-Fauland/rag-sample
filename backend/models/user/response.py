import uuid
from datetime import datetime
from pydantic import BaseModel, Field


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
    created_at: datetime = Field(...,
                                 description="A timestamp when the user was created")
    modified_at: datetime = Field(...,
                                  description="A timestamp when the user was last modified")


class RoleModelBase(BaseModel):
    id: int = Field(..., description="The role id", examples=[2])
    name: str = Field(..., description="The name of the role",
                      examples=["user"])
    is_active: bool = Field(
        ..., description="Whether the role can be currently used in the application", examples=[True])


class RoleModel(RoleModelBase):
    description: str = Field(..., description="The description of the role", examples=[
                             "Default role with limited permissions"])
    created_at: datetime = Field(...,
                                 description="When the role was initally created")


class UserModel(UserModelBase):
    roles: list["RoleModelBase"]


class SignupResponse(BaseModel):
    email: str = Field(..., description="The email of the newly created user", examples=[
                       "john.doe@example.com"])
    sucess: bool = Field(..., description="Wheter the user was successfully created", examples=[
        True])


class SigninResponse(BaseModel):
    message: str = Field(..., description="A status message about the login", examples=[
                         "Login successful"])
    access_token: str = Field(..., description="The access JWT", examples=[
        "eyJhbG..."])
    refresh_token: str = Field(..., description="The refresh JWT", examples=[
        "eyJhbG..."])
