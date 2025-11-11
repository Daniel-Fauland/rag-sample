from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AccountType(str, Enum):
    local = "local",
    sso_google = "sso_google",
    sso_microsoft = "sso_microsoft"
    # add more as needed


class UserCommonModel(BaseModel):
    email: str = Field(..., description="The users email", examples=[
        "john.doe@example.com"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError(
                "Invalid email. A valid email must include '@' and '.'")
        return v


class SignupRequest(UserCommonModel):
    password: str = Field(..., examples=["Mysecretpassword99"])
    first_name: str = Field(..., description="The users first name", examples=[
                            "John"])
    last_name: str = Field(..., description="The users last name", examples=[
                           "Doe"])
    account_type: AccountType = AccountType.local

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.islower() for c in v):
            raise ValueError(
                "Password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in v):
            raise ValueError(
                "Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        return v


class BatchSignupRequest(BaseModel):
    users: list[SignupRequest]


class BatchDeleteRequest(BaseModel):
    identifiers: list[str] = Field(..., description="List of user emails or UUIDs to delete", examples=[
        ["john.doe@example.com", "0198c7ff-7032-7649-88f0-438321150e2c"]])


class LoginRequest(UserCommonModel):
    password: str = Field(..., examples=["Mysecretpassword99"])


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(
        None, description="The refresh token to invalidate", examples=["eyJhb..."])


class UserUpdateRequest(BaseModel):
    """Request model for updating user information. All fields are optional to support PATCH-like behavior."""
    email: Optional[str] = Field(None, description="The user's email", examples=[
                                 "john.doe@example.com"])
    first_name: Optional[str] = Field(
        None, description="The user's first name", examples=["John"])
    last_name: Optional[str] = Field(
        None, description="The user's last name", examples=["Doe"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if "@" not in v or "." not in v:
                raise ValueError(
                    "Invalid email. A valid email must include '@' and '.'")
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Name fields cannot be empty strings")
        return v.strip() if v is not None else v


class BatchUserUpdateItem(BaseModel):
    """Single user update item for batch operations"""
    identifier: str = Field(..., description="User email or UUID to update", examples=[
        "john.doe@example.com", "0198c7ff-7032-7649-88f0-438321150e2c"])
    updates: UserUpdateRequest = Field(...,
                                       description="Fields to update for this user")


class BatchUserUpdateRequest(BaseModel):
    """Request model for batch user updates"""
    users: list[BatchUserUpdateItem] = Field(
        ..., description="List of users to update with their respective changes")


class PasswordUpdateRequest(BaseModel):
    """Request model for updating user password."""
    old_password: str = Field(..., description="The user's current password", examples=[
                              "OldPassword123"])
    new_password: str = Field(..., description="The user's new password", examples=[
                              "NewPassword456"])

    @field_validator('old_password', 'new_password')
    @classmethod
    def validate_passwords(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Password cannot be empty")
        return v.strip()

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(
                "New password must be at least 8 characters long.")
        if not any(c.islower() for c in v):
            raise ValueError(
                "New password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in v):
            raise ValueError(
                "New password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("New password must contain at least one number.")
        return v
