"""make_restaurant_id_nullable

Revision ID: c36089f5ffa6
Revises: 23a116cd8d5e
Create Date: 2025-09-14 13:59:20.892241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c36089f5ffa6'
down_revision: Union[str, None] = '23a116cd8d5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Делаем restaurant_id nullable для всех связанных таблиц
    with op.batch_alter_table('categories') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=True)
    
    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=True)
    
    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=True)
    
    with op.batch_alter_table('discounts') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=True)


def downgrade() -> None:
    # Возвращаем restaurant_id к nullable=False
    # Сначала обновляем все NULL значения на существующий ресторан
    conn = op.get_bind()
    
    # Находим первый доступный ресторан для замены NULL значений
    result = conn.execute(sa.text("SELECT id FROM restaurants LIMIT 1"))
    first_restaurant_id = result.scalar()
    
    if first_restaurant_id:
        # Обновляем все NULL значения
        conn.execute(sa.text(f"UPDATE categories SET restaurant_id = {first_restaurant_id} WHERE restaurant_id IS NULL"))
        conn.execute(sa.text(f"UPDATE products SET restaurant_id = {first_restaurant_id} WHERE restaurant_id IS NULL"))
        conn.execute(sa.text(f"UPDATE orders SET restaurant_id = {first_restaurant_id} WHERE restaurant_id IS NULL"))
        conn.execute(sa.text(f"UPDATE discounts SET restaurant_id = {first_restaurant_id} WHERE restaurant_id IS NULL"))
    
    # Теперь делаем поля NOT NULL
    with op.batch_alter_table('categories') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=False)
    
    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=False)
    
    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=False)
    
    with op.batch_alter_table('discounts') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=False)
