"""add_initial_permission_data

Revision ID: db135d0d75dd
Revises: 2a3c5c4c0a33
Create Date: 2025-09-11 21:53:11.317301

"""
from typing import Sequence, Union
# fmt: off
from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import sqlmodel  # EDITED  # noqa
from datetime import datetime
# fmt: off

# revision identifiers, used by Alembic.
revision: str = 'db135d0d75dd'
down_revision: Union[str, Sequence[str], None] = '2a3c5c4c0a33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get current timestamp
    current_timestamp = datetime.now()

    # Define permissions table reference
    permissions_table = sa.table(
        'permissions',
        sa.column('id', sa.Integer),
        sa.column('type', sa.String),
        sa.column('resource', sa.String),
        sa.column('context', sa.String),
        sa.column('description', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime)
    )

    # Define all permissions to insert
    permissions_data = [
        # User permissions (both me and all contexts make sense)
        {
            'type': 'read',
            'resource': 'user',
            'context': 'me',
            'description': 'Read own user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'write',
            'resource': 'user',
            'context': 'me',
            'description': 'Create own user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'update',
            'resource': 'user',
            'context': 'me',
            'description': 'Update own user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'delete',
            'resource': 'user',
            'context': 'me',
            'description': 'Delete own user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'read',
            'resource': 'user',
            'context': 'all',
            'description': 'Read all users data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'write',
            'resource': 'user',
            'context': 'all',
            'description': 'Create any user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'update',
            'resource': 'user',
            'context': 'all',
            'description': 'Update any user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'delete',
            'resource': 'user',
            'context': 'all',
            'description': 'Delete any user data',
            'is_active': True,
            'created_at': current_timestamp
        },
        # Role permissions (only all context makes sense)
        {
            'type': 'read',
            'resource': 'role',
            'context': 'all',
            'description': 'Read all roles data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'write',
            'resource': 'role',
            'context': 'all',
            'description': 'Create any role data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'update',
            'resource': 'role',
            'context': 'all',
            'description': 'Update any role data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'delete',
            'resource': 'role',
            'context': 'all',
            'description': 'Delete any role data',
            'is_active': True,
            'created_at': current_timestamp
        },
        # Permission permissions (only all context makes sense)
        {
            'type': 'read',
            'resource': 'permission',
            'context': 'all',
            'description': 'Read all permissions data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'write',
            'resource': 'permission',
            'context': 'all',
            'description': 'Create any permission data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'update',
            'resource': 'permission',
            'context': 'all',
            'description': 'Update any permission data',
            'is_active': True,
            'created_at': current_timestamp
        },
        {
            'type': 'delete',
            'resource': 'permission',
            'context': 'all',
            'description': 'Delete any permission data',
            'is_active': True,
            'created_at': current_timestamp
        }
    ]

    # Insert permissions only if they don't already exist
    for permission in permissions_data:
        # Check if permission already exists based on type, resource, and context
        result = op.get_bind().execute(
            sa.select(permissions_table.c.id).where(
                sa.and_(
                    permissions_table.c.type == permission['type'],
                    permissions_table.c.resource == permission['resource'],
                    permissions_table.c.context == permission['context']
                )
            )
        ).fetchone()

        # Only insert if permission doesn't exist
        if not result:
            op.execute(
                permissions_table.insert().values(**permission)
            )


def downgrade() -> None:
    """Downgrade schema."""
    # Define permissions table reference
    permissions_table = sa.table(
        'permissions',
        sa.column('id', sa.Integer),
        sa.column('type', sa.String),
        sa.column('resource', sa.String),
        sa.column('context', sa.String),
        sa.column('description', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime)
    )

    # List of all permissions that were inserted (type, resource, context combinations)
    permissions_to_delete = [
        # User permissions
        {'type': 'read', 'resource': 'user', 'context': 'me'},
        {'type': 'write', 'resource': 'user', 'context': 'me'},
        {'type': 'update', 'resource': 'user', 'context': 'me'},
        {'type': 'delete', 'resource': 'user', 'context': 'me'},
        {'type': 'read', 'resource': 'user', 'context': 'all'},
        {'type': 'write', 'resource': 'user', 'context': 'all'},
        {'type': 'update', 'resource': 'user', 'context': 'all'},
        {'type': 'delete', 'resource': 'user', 'context': 'all'},
        # Role permissions
        {'type': 'read', 'resource': 'role', 'context': 'all'},
        {'type': 'write', 'resource': 'role', 'context': 'all'},
        {'type': 'update', 'resource': 'role', 'context': 'all'},
        {'type': 'delete', 'resource': 'role', 'context': 'all'},
        # Permission permissions
        {'type': 'read', 'resource': 'permission', 'context': 'all'},
        {'type': 'write', 'resource': 'permission', 'context': 'all'},
        {'type': 'update', 'resource': 'permission', 'context': 'all'},
        {'type': 'delete', 'resource': 'permission', 'context': 'all'}
    ]

    # Delete all permissions that were inserted
    for permission in permissions_to_delete:
        op.execute(
            permissions_table.delete().where(
                sa.and_(
                    permissions_table.c.type == permission['type'],
                    permissions_table.c.resource == permission['resource'],
                    permissions_table.c.context == permission['context']
                )
            )
        )
