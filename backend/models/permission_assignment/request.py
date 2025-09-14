from pydantic import BaseModel, Field


class PermissionAssignmentCreateRequest(BaseModel):
    """Request model for creating a new permission assignment."""
    role_id: int = Field(..., description="The role ID to assign the permission to", examples=[
                         2])
    permission_id: int = Field(..., description="The permission ID to assign", examples=[
                               1])


class PermissionAssignmentDeleteRequest(BaseModel):
    """Request model for deleting a permission assignment."""
    role_id: int = Field(..., description="The role ID to remove the permission from", examples=[
                         2])
    permission_id: int = Field(..., description="The permission ID to remove", examples=[
                               1])
