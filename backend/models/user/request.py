from pydantic import BaseModel, Field, field_validator


class UserCommonModel(BaseModel):
    email: str = Field(..., description="The users email", examples=[
        "john.doe@example.com"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError(
                "email is not valid. It must include '@' and '.'")
        return v


class SignupRequest(UserCommonModel):
    password: str = Field(..., examples=["Mysecretpassword99"])
    first_name: str = Field(..., description="The users first name", examples=[
                            "John"])
    last_name: str = Field(..., description="The users last name", examples=[
                           "Doe"])

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


class LoginRequest(UserCommonModel):
    password: str = Field(..., examples=["Mysecretpassword99"])
