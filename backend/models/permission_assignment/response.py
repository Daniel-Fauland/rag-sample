from datetime import datetime
from pydantic import BaseModel, Field


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
