"""add users.full_name

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-03 18:00:00.000000

The ``users`` table is empty at this point, so the NOT NULL column is added
without a backfill.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('full_name', sa.String(length=120), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('users', 'full_name')
