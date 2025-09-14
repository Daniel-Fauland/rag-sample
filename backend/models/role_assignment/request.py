import uuid
from pydantic import BaseModel, Field


class RoleAssignmentCreateRequest(BaseModel):
    """Request model for creating a new role assignment."""
    user_id: uuid.UUID = Field(..., description="The user ID to assign the role to",
                               examples=["0198c7ff-7032-7649-88f0-438321150e2c"])
    role_id: int = Field(..., description="The role ID to assign to the user", examples=[
                         2])


class RoleAssignmentDeleteRequest(BaseModel):
    """Request model for deleting a role assignment."""
    user_id: uuid.UUID = Field(..., description="The user ID to remove the role from",
                               examples=["0198c7ff-7032-7649-88f0-438321150e2c"])
    role_id: int = Field(..., description="The role ID to remove from the user", examples=[
                         2])
