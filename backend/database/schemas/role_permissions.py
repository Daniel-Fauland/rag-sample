import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column


class RolePermission(SQLModel, table=True):
    """Junction table for many-to-many relationship between roles and permissions"""
    __tablename__ = 'role_permissions'

    role_id: int = Field(
        default=None, foreign_key="roles.id", primary_key=True)
    permission_id: int = Field(
        default=None, foreign_key="permissions.id", primary_key=True)
    assigned_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    ))
