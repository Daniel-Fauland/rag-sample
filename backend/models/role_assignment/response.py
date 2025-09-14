import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class RoleAssignmentModel(BaseModel):
    user_id: uuid.UUID = Field(..., description="The user ID")
    role_id: int = Field(..., description="The role ID")
    assigned_at: datetime = Field(...,
                                  description="When the role was assigned to the user")


class RoleAssignmentCreateResponse(BaseModel):
    user_id: uuid.UUID = Field(...,
                               description="The user ID that was assigned the role")
    role_id: int = Field(...,
                         description="The role ID that was assigned to the user")
    success: bool = Field(..., description="Whether the assignment was successful", examples=[
                          True])
    message: str = Field(..., description="Status message",
                         examples=["Role assigned successfully"])


class RoleAssignmentDeleteResponse(BaseModel):
    success: bool = Field(..., description="Whether the removal was successful", examples=[
                          True])
    message: str = Field(..., description="Status message", examples=[
                         "Role assignment removed successfully"])
