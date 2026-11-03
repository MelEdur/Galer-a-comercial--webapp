"""limit merchant uniqueness to active accounts

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-03 18:10:00.000000

A deactivated merchant keeps ``store_id`` as historical data while its store
becomes free for a replacement, so the unique index must only consider active
merchant accounts.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OLD_PREDICATE = sa.text("role = 'merchant'")
_NEW_PREDICATE = sa.text("role = 'merchant' AND is_active")


def upgrade() -> None:
    op.drop_index(
        'uq_users_store_merchant',
        table_name='users',
        postgresql_where=_OLD_PREDICATE,
    )
    op.create_index(
        'uq_users_store_merchant',
        'users',
        ['store_id'],
        unique=True,
        postgresql_where=_NEW_PREDICATE,
    )


def downgrade() -> None:
    op.drop_index(
        'uq_users_store_merchant',
        table_name='users',
        postgresql_where=_NEW_PREDICATE,
    )
    op.create_index(
        'uq_users_store_merchant',
        'users',
        ['store_id'],
        unique=True,
        postgresql_where=_OLD_PREDICATE,
    )
