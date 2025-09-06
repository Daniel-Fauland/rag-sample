"""Insert inital user data

Revision ID: 8340e034cd24
Revises: 55475cd1c3f0
Create Date: 2025-08-20 16:44:31.695158

"""
from typing import Sequence, Union

# fmt: off
from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import sqlmodel  # EDITED  # noqa
from datetime import datetime
# fmt: on

# revision identifiers, used by Alembic.
revision: str = '8340e034cd24'
down_revision: Union[str, Sequence[str], None] = '55475cd1c3f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get current timestamp
    current_timestamp = datetime.now()

    # Insert User 1 if email does not exist
    op.execute(f"""
        INSERT INTO users (id, email, first_name, last_name, role, is_verified, password_hash, created_at, modified_at)
        SELECT '0198c7ff-09a9-7b8c-9c6f-65996832605c', 'admin@example.com', 'Max', 'Mustermann', 'admin', TRUE,
               '$argon2id$v=19$m=8192,t=2,p=10$cAWQyBLCG58aViCV4yQuqw$B038tldLPEZtVwlN47ONMlS3MXGCFZl/LR3VRY+QR14',
               '{current_timestamp}', '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@example.com')
    """)

    # Insert User 2 if email does not exist
    op.execute(f"""
        INSERT INTO users (id, email, first_name, last_name, role, is_verified, password_hash, created_at, modified_at)
        SELECT '0198c7ff-7032-7649-88f0-438321150e2c', 'user@example.com', 'Marcus', 'Müller', 'user', TRUE,
               '$argon2id$v=19$m=8192,t=2,p=10$1CgqUuMOLDVscJsRi2+vAw$YdMavMSpgy17KmeRtcDvtQ2kPdTPqMUqyhR8E2DfkBQ',
               '{current_timestamp}', '{current_timestamp}'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'user@example.com')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the inserted rows if downgrading
    op.execute("DELETE FROM users WHERE email = 'admin@example.com'")
    op.execute("DELETE FROM users WHERE email = 'user@example.com'")
