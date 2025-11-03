import uuid
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ForeignKey


class UserRole(SQLModel, table=True):
    """Junction table for many-to-many relationship between users and roles"""
    __tablename__ = 'user_roles'

    user_id: uuid.UUID = Field(
        default=None,
        sa_column=Column(
            pg.UUID,
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    role_id: int = Field(
        default=None,
        sa_column=Column(
            pg.INTEGER,
            ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    assigned_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    ))
