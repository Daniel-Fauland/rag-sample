"""add_user_roles_relationship_data

Revision ID: 9914df272fc1
Revises: 3cb8a3670bf3
Create Date: 2025-09-06 16:39:42.560121

"""
from typing import Sequence, Union
# fmt: off
from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import sqlmodel  # EDITED  # noqa
from datetime import datetime
# fmt: off

# revision identifiers, used by Alembic.
revision: str = '9914df272fc1'
down_revision: Union[str, Sequence[str], None] = '3cb8a3670bf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get current timestamp
    current_timestamp = datetime.now()

    # Add admin role for User 1 (admin user gets both admin and user roles)
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id, assigned_at)
        SELECT '0198c7ff-09a9-7b8c-9c6f-65996832605c', r.id, '{current_timestamp}'
        FROM roles r
        WHERE r.name = 'admin'
        AND NOT EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c'
            AND ur.role_id = r.id
        )
    """)

    # Add user role for User 1 (admin user also gets user role)
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id, assigned_at)
        SELECT '0198c7ff-09a9-7b8c-9c6f-65996832605c', r.id, '{current_timestamp}'
        FROM roles r
        WHERE r.name = 'user'
        AND NOT EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c'
            AND ur.role_id = r.id
        )
    """)

    # Add user role for User 2 (regular user)
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id, assigned_at)
        SELECT '0198c7ff-7032-7649-88f0-438321150e2c', r.id, '{current_timestamp}'
        FROM roles r
        WHERE r.name = 'user'
        AND NOT EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id = '0198c7ff-7032-7649-88f0-438321150e2c'
            AND ur.role_id = r.id
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove admin role for User 1
    op.execute("""
        DELETE FROM user_roles
        WHERE user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c'
        AND role_id IN (SELECT id FROM roles WHERE name = 'admin')
    """)

    # Remove user role for User 1
    op.execute("""
        DELETE FROM user_roles
        WHERE user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c'
        AND role_id IN (SELECT id FROM roles WHERE name = 'user')
    """)

    # Remove user role for User 2
    op.execute("""
        DELETE FROM user_roles
        WHERE user_id = '0198c7ff-7032-7649-88f0-438321150e2c'
        AND role_id IN (SELECT id FROM roles WHERE name = 'user')
    """)
