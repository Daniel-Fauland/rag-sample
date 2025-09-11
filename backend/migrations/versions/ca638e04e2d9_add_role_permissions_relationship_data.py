"""add_role_permissions_relationship_data

Revision ID: ca638e04e2d9
Revises: db135d0d75dd
Create Date: 2025-09-11 22:34:46.919049

"""
from typing import Sequence, Union
# fmt: off
from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import sqlmodel  # EDITED  # noqa
from datetime import datetime
# fmt: off

# revision identifiers, used by Alembic.
revision: str = 'ca638e04e2d9'
down_revision: Union[str, Sequence[str], None] = 'db135d0d75dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get current timestamp
    current_timestamp = datetime.now()

    # Define role_permissions table reference
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
        sa.column('assigned_at', sa.DateTime)
    )

    # Define permissions table reference
    permissions_table = sa.table(
        'permissions',
        sa.column('id', sa.Integer),
        sa.column('type', sa.String),
        sa.column('resource', sa.String),
        sa.column('context', sa.String)
    )

    # Define roles table reference
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String)
    )

    # Add permissions to user role
    # User role gets:
    # 1. All read permissions (read:user:me, read:user:all, read:role:all, read:permission:all)
    # 2. User-specific permissions (update:user:me, delete:user:me)

    # Get user role ID
    user_role_result = op.get_bind().execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == 'user')
    ).fetchone()

    if user_role_result:
        user_role_id = user_role_result[0]

        # Get all read permissions
        read_permissions = op.get_bind().execute(
            sa.select(permissions_table.c.id).where(
                permissions_table.c.type == 'read'
            )
        ).fetchall()

        # Get user-specific permissions (update:user:me, delete:user:me)
        user_me_permissions = op.get_bind().execute(
            sa.select(permissions_table.c.id).where(
                sa.and_(
                    permissions_table.c.resource == 'user',
                    permissions_table.c.context == 'me',
                    permissions_table.c.type.in_(['write', 'update', 'delete'])
                )
            )
        ).fetchall()

        # Combine all permissions for user role
        all_user_permissions = read_permissions + user_me_permissions

        # Insert role-permission relationships
        for permission in all_user_permissions:
            permission_id = permission[0]

            # Check if relationship already exists
            existing = op.get_bind().execute(
                sa.select(role_permissions_table.c.role_id).where(
                    sa.and_(
                        role_permissions_table.c.role_id == user_role_id,
                        role_permissions_table.c.permission_id == permission_id
                    )
                )
            ).fetchone()

            # Only insert if relationship doesn't exist
            if not existing:
                op.execute(
                    role_permissions_table.insert().values(
                        role_id=user_role_id,
                        permission_id=permission_id,
                        assigned_at=current_timestamp
                    )
                )

    # Note: Admin role gets all permissions, but this is handled in the backend
    # No need to add explicit role-permission relationships for admin role


def downgrade() -> None:
    """Downgrade schema."""
    # Define role_permissions table reference
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer)
    )

    # Define roles table reference
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String)
    )

    # Remove all role-permission relationships for user role
    # (Admin role has no explicit relationships, so nothing to remove)
    op.execute(
        role_permissions_table.delete().where(
            role_permissions_table.c.role_id.in_(
                sa.select(roles_table.c.id).where(roles_table.c.name == 'user')
            )
        )
    )
