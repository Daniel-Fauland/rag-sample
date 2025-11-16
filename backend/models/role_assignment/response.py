import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Sequence
from database.schemas.user_roles import UserRole


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


class ListRoleAssignmentModel(BaseModel):
    limit: int = Field(..., description="The maximum number of role assignments to be retrieved", examples=[
                       25])
    offset: int = Field(...,
                        description="How many role assignments to skip", examples=[75])
    total_assignments: int = Field(..., description="The total number of role assignments in the db", examples=[
        123])
    current_assignments: int = Field(..., description="The number of role assignments retrieved right now", examples=[
        25])
    assignments: Sequence[UserRole] = Field(...,
                                            description="The actual role assignment data")


class ListRoleAssignmentResponse(ListRoleAssignmentModel):
    assignments: list[RoleAssignmentModel] = Field(
        ..., description="The actual role assignment data")
