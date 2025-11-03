"""Add on delete cascade to junction tables

Revision ID: f1d92ec1c0cf
Revises: ca638e04e2d9
Create Date: 2025-11-03 19:11:52.518307

"""
from typing import Sequence, Union
# fmt: off
from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import sqlmodel  # EDITED  # noqa

# fmt: off

# revision identifiers, used by Alembic.
revision: str = 'f1d92ec1c0cf'
down_revision: Union[str, Sequence[str], None] = 'ca638e04e2d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add CASCADE to foreign key constraints."""
    # Drop existing foreign key constraints on role_permissions table
    op.drop_constraint('role_permissions_permission_id_fkey', 'role_permissions', type_='foreignkey')
    op.drop_constraint('role_permissions_role_id_fkey', 'role_permissions', type_='foreignkey')

    # Recreate with CASCADE
    op.create_foreign_key('role_permissions_role_id_fkey', 'role_permissions', 'roles', ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('role_permissions_permission_id_fkey', 'role_permissions', 'permissions', ['permission_id'], ['id'], ondelete='CASCADE')

    # Drop existing foreign key constraints on user_roles table
    op.drop_constraint('user_roles_role_id_fkey', 'user_roles', type_='foreignkey')
    op.drop_constraint('user_roles_user_id_fkey', 'user_roles', type_='foreignkey')

    # Recreate with CASCADE
    op.create_foreign_key('user_roles_role_id_fkey', 'user_roles', 'roles', ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_roles_user_id_fkey', 'user_roles', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema - Remove CASCADE from foreign key constraints."""
    # Drop CASCADE foreign key constraints on user_roles table
    op.drop_constraint('user_roles_user_id_fkey', 'user_roles', type_='foreignkey')
    op.drop_constraint('user_roles_role_id_fkey', 'user_roles', type_='foreignkey')

    # Recreate without CASCADE
    op.create_foreign_key('user_roles_user_id_fkey', 'user_roles', 'users', ['user_id'], ['id'])
    op.create_foreign_key('user_roles_role_id_fkey', 'user_roles', 'roles', ['role_id'], ['id'])

    # Drop CASCADE foreign key constraints on role_permissions table
    op.drop_constraint('role_permissions_permission_id_fkey', 'role_permissions', type_='foreignkey')
    op.drop_constraint('role_permissions_role_id_fkey', 'role_permissions', type_='foreignkey')

    # Recreate without CASCADE
    op.create_foreign_key('role_permissions_role_id_fkey', 'role_permissions', 'roles', ['role_id'], ['id'])
    op.create_foreign_key('role_permissions_permission_id_fkey', 'role_permissions', 'permissions', ['permission_id'], ['id'])
