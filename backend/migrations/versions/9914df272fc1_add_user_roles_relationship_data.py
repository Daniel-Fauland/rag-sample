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

    # Add Roles for User 1 (admin)
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id, assigned_at)
        SELECT '0198c7ff-09a9-7b8c-9c6f-65996832605c', 1, '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM user_roles WHERE user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c' AND role_id = 1)
    """)

    # Add Roles for User 1 (user)
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id, assigned_at)
        SELECT '0198c7ff-09a9-7b8c-9c6f-65996832605c', 2, '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM user_roles WHERE user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c' AND role_id = 2)
    """)

    # Add Roles for User 2 (user)
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id, assigned_at)
        SELECT '0198c7ff-7032-7649-88f0-438321150e2c', 2, '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM user_roles WHERE user_id = '0198c7ff-7032-7649-88f0-438321150e2c' AND role_id = 2)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM user_roles WHERE user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c' AND role_id = 1")
    op.execute("DELETE FROM user_roles WHERE user_id = '0198c7ff-09a9-7b8c-9c6f-65996832605c' AND role_id = 2")
    op.execute("DELETE FROM user_roles WHERE user_id = '0198c7ff-7032-7649-88f0-438321150e2c' AND role_id = 2")
