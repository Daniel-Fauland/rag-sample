import sqlalchemy.dialects.postgresql as pg
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Relationship
from .user_roles import UserRole

if TYPE_CHECKING:  # This is needed to prevent circular imports
    from .users import User


class Role(SQLModel, table=True):
    __tablename__ = 'roles'

    id: int = Field(
        sa_column=Column(pg.INTEGER, nullable=False,
                         primary_key=True, autoincrement=True)
    )
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    ))

    # Many-to-many relationship with users
    users: List["User"] = Relationship(
        back_populates="roles", link_model=UserRole)

    def __repr__(self):
        return f"<Role {self.name}>"
