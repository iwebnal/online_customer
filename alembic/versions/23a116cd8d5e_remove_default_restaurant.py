"""remove_default_restaurant

Revision ID: 23a116cd8d5e
Revises: 6b1d08246904
Create Date: 2025-09-14 13:39:07.503061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23a116cd8d5e'
down_revision: Union[str, None] = '6b1d08246904'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Находим Default Restaurant
    result = conn.execute(sa.text("SELECT id FROM restaurants WHERE name = 'Default Restaurant' AND address = 'Default Address'"))
    default_restaurant = result.fetchone()
    
    if default_restaurant:
        default_id = default_restaurant[0]
        
        # Создаем новый ресторан для замены Default Restaurant
        result = conn.execute(sa.text("""
            INSERT INTO restaurants (name, address) 
            VALUES ('You Coffee (Nalchik)', 'г. Нальчик, ул. Кабардинская, 25') 
            RETURNING id
        """))
        new_restaurant_id = result.scalar()
        
        # Переназначаем все связанные записи на новый ресторан
        conn.execute(sa.text(f"UPDATE categories SET restaurant_id = {new_restaurant_id} WHERE restaurant_id = {default_id}"))
        conn.execute(sa.text(f"UPDATE discounts SET restaurant_id = {new_restaurant_id} WHERE restaurant_id = {default_id}"))
        conn.execute(sa.text(f"UPDATE orders SET restaurant_id = {new_restaurant_id} WHERE restaurant_id = {default_id}"))
        conn.execute(sa.text(f"UPDATE products SET restaurant_id = {new_restaurant_id} WHERE restaurant_id = {default_id}"))
        
        # Теперь удаляем Default Restaurant
        conn.execute(sa.text(f"DELETE FROM restaurants WHERE id = {default_id}"))


def downgrade() -> None:
    # Восстанавливаем Default Restaurant (если нужно)
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        INSERT INTO restaurants (name, address) VALUES ('Default Restaurant', 'Default Address') RETURNING id
    """))
    default_restaurant_id = result.scalar()
    
    # Обновляем все записи без restaurant_id на новый Default Restaurant
    conn.execute(sa.text(f"UPDATE categories SET restaurant_id = {default_restaurant_id} WHERE restaurant_id IS NULL"))
    conn.execute(sa.text(f"UPDATE discounts SET restaurant_id = {default_restaurant_id} WHERE restaurant_id IS NULL"))
    conn.execute(sa.text(f"UPDATE orders SET restaurant_id = {default_restaurant_id} WHERE restaurant_id IS NULL"))
    conn.execute(sa.text(f"UPDATE products SET restaurant_id = {default_restaurant_id} WHERE restaurant_id IS NULL"))
