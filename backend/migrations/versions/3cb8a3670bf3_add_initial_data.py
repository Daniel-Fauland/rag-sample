"""add_initial_data

Revision ID: 3cb8a3670bf3
Revises: 9350a45866c5
Create Date: 2025-09-06 16:24:42.583188

"""
from typing import Sequence, Union
# fmt: off
from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import sqlmodel  # EDITED  # noqa
from datetime import datetime
# fmt: off

# revision identifiers, used by Alembic.
revision: str = '3cb8a3670bf3'
down_revision: Union[str, Sequence[str], None] = '9350a45866c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get current timestamp
    current_timestamp = datetime.now()

    # Insert User 1 if email does not exist
    op.execute(f"""
        INSERT INTO users (id, email, first_name, last_name, is_verified, password_hash, created_at, modified_at)
        SELECT '0198c7ff-09a9-7b8c-9c6f-65996832605c', 'admin@example.com', 'Max', 'Mustermann', TRUE,
               '$argon2id$v=19$m=8192,t=2,p=10$cAWQyBLCG58aViCV4yQuqw$B038tldLPEZtVwlN47ONMlS3MXGCFZl/LR3VRY+QR14',
               '{current_timestamp}', '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@example.com')
    """)

    # Insert User 2 if email does not exist
    op.execute(f"""
        INSERT INTO users (id, email, first_name, last_name, is_verified, password_hash, created_at, modified_at)
        SELECT '0198c7ff-7032-7649-88f0-438321150e2c', 'user@example.com', 'Marcus', 'Müller', TRUE,
               '$argon2id$v=19$m=8192,t=2,p=10$1CgqUuMOLDVscJsRi2+vAw$YdMavMSpgy17KmeRtcDvtQ2kPdTPqMUqyhR8E2DfkBQ',
               '{current_timestamp}', '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'user@example.com')
    """)

    # Insert Role "admin" if it does not exist
    op.execute(f"""
        INSERT INTO roles (name, description, is_active, created_at)
        SELECT 'admin', 'Administrator with full system access', TRUE, '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'admin')
    """)

    # Insert Role "user" if it does not exist
    op.execute(f"""
        INSERT INTO roles (name, description, is_active, created_at)
        SELECT 'user', 'Default role with limited permissions', TRUE, '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'user')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # First, clean up ALL user_roles relationships that reference the roles we're about to delete
    # This handles any user_roles records that might reference these roles
    op.execute("""
        DELETE FROM user_roles
        WHERE role_id IN (
            SELECT id FROM roles WHERE name IN ('admin', 'user')
        )
    """)

    # Then remove the users
    op.execute("DELETE FROM users WHERE email = 'admin@example.com'")
    op.execute("DELETE FROM users WHERE email = 'user@example.com'")

    # Finally remove the roles (now safe since no foreign key references exist)
    op.execute("DELETE FROM roles WHERE name = 'admin'")
    op.execute("DELETE FROM roles WHERE name = 'user'")
