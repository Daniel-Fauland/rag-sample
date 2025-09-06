import uuid
import uuid_utils as uid
import sqlalchemy.dialects.postgresql as pg
from typing import List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Relationship
from .user_roles import UserRole

if TYPE_CHECKING:  # This is needed to prevent circular imports
    from .roles import Role


class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uid.uuid7)
    )
    email: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    is_verified: bool = Field(default=True)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    ))
    modified_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    ))
    roles: List["Role"] = Relationship(
        back_populates="users", link_model=UserRole)

    def __repr__(self):
        return f"<User {self.email}>"
