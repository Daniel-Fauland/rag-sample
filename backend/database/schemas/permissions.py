import sqlalchemy.dialects.postgresql as pg
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Relationship
from .role_permissions import RolePermission

if TYPE_CHECKING:  # This is needed to prevent circular imports
    from .roles import Role


class Permission(SQLModel, table=True):
    __tablename__ = 'permissions'

    id: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False,
                         primary_key=True, autoincrement=True)
    )
    type: str = Field()
    resource: str = Field(index=True)
    context: str = Field(default="all")
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    ))

    # Many-to-many relationship with users
    roles: List["Role"] = Relationship(
        back_populates="permissions", link_model=RolePermission)

    def __repr__(self):
        return f"<Permission {self.type}:{self.resource}:{self.context}>"
