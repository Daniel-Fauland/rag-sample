from datetime import datetime
from pydantic import BaseModel, Field
from typing import Sequence
from database.schemas.role_permissions import RolePermission


class PermissionAssignmentModel(BaseModel):
    """Model representing a permission assignment (role-permission relationship)."""
    role_id: int = Field(..., description="The role ID")
    permission_id: int = Field(..., description="The permission ID")
    assigned_at: datetime = Field(...,
                                  description="When the permission was assigned to the role")


class PermissionAssignmentCreateResponse(BaseModel):
    """Response model for creating a permission assignment."""
    role_id: int = Field(..., description="The role ID that was assigned the permission", examples=[
                         2])
    permission_id: int = Field(..., description="The permission ID that was assigned", examples=[
                               1])
    success: bool = Field(..., description="Whether the assignment was successful", examples=[
                          True])
    message: str = Field(..., description="Success message", examples=[
                         "Permission assigned successfully"])


class ListPermissionAssignmentModel(BaseModel):
    limit: int = Field(..., description="The maximum number of permission assignments to be retrieved", examples=[
                       25])
    offset: int = Field(...,
                        description="How many permission assignments to skip", examples=[75])
    total_assignments: int = Field(..., description="The total number of permission assignments in the db", examples=[
        123])
    current_assignments: int = Field(..., description="The number of permission assignments retrieved right now", examples=[
        25])
    assignments: Sequence[RolePermission] = Field(..., description="The actual permission assignment data")


class ListPermissionAssignmentResponse(ListPermissionAssignmentModel):
    assignments: list[PermissionAssignmentModel] = Field(..., description="The actual permission assignment data")
