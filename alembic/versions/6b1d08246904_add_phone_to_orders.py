"""add_phone_to_orders

Revision ID: 6b1d08246904
Revises: 7854e42178cc
Create Date: 2025-09-03 21:39:10.386674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b1d08246904'
down_revision: Union[str, None] = '7854e42178cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле phone в таблицу orders
    op.add_column('orders', sa.Column('phone', sa.String(32), nullable=True))


def downgrade() -> None:
    # Удаляем поле phone из таблицы orders
    op.drop_column('orders', 'phone')
