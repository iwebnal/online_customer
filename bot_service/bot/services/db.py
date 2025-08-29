from sqlalchemy import select
from sqlalchemy.orm import selectinload
from shared.models import Product, Category, Restaurant, Discount, User, Order, OrderItem
from shared.database import get_db_session

async def get_products_by_category_name(category_name: str):
    async with get_db_session() as session:
        result = await session.execute(
            select(Product)
            .join(Category)
            .where(Category.name == category_name)
            .where(Product.is_available == True)
        )
        products = result.scalars().all()
        print(f"products -------- {products}")
        return products 


async def get_all_categories():
    async with get_db_session() as session:
        result = await session.execute(select(Category))
        return result.scalars().all() 

async def get_all_restaurants():
    async with get_db_session() as session:
        result = await session.execute(select(Restaurant))
        return result.scalars().all()

async def get_products_by_restaurant(restaurant_id: int):
    async with get_db_session() as session:
        result = await session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.restaurant_id == restaurant_id)
            .where(Product.is_available == True)
        )
        return result.scalars().all()

async def get_discounts_by_restaurant(restaurant_id: int):
    async with get_db_session() as session:
        result = await session.execute(
            select(Discount)
            .where(Discount.restaurant_id == restaurant_id)
            .where(Discount.is_active == True)
        )
        return result.scalars().all() 

async def get_user_by_telegram_id(telegram_id: str):
    async with get_db_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

async def create_user(telegram_id: str, name: str = None, phone: str = None):
    async with get_db_session() as session:
        user = User(telegram_id=telegram_id, name=name, phone=phone)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def create_order(user_id: int, restaurant_id: int, total: float, items: list):
    async with get_db_session() as session:
        order = Order(user_id=user_id, restaurant_id=restaurant_id, total=total, status='new')
        session.add(order)
        await session.flush()  # Получить order.id до коммита
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price'],
                discount_price=item.get('discount_price')
            )
            session.add(order_item)
        await session.commit()
        await session.refresh(order)
        return order 