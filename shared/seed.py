import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from models import Base, Category, Product, Restaurant

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/online_customer"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed():
    async with engine.begin() as conn:
        # Создаём таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже рестораны
        result = await session.execute(select(Restaurant))
        restaurants = result.scalars().all()
        
        if not restaurants:
            # Добавляем ресторан
            restaurant = Restaurant(
                name="You Coffee (Nalchik)",
                address="г. Нальчик, ул. Кабардинская, 25"
            )
            session.add(restaurant)
            await session.commit()
            await session.refresh(restaurant)
            restaurant_id = restaurant.id
        else:
            restaurant_id = restaurants[0].id

        # Проверяем, есть ли уже категории
        result = await session.execute(select(Category))
        existing_categories = result.scalars().all()
        
        if not existing_categories:
            # Добавляем категории
            categories = [
                Category(name="Напитки", restaurant_id=restaurant_id),
                Category(name="Выпечка", restaurant_id=restaurant_id),
                Category(name="Десерты", restaurant_id=restaurant_id),
                Category(name="Завтраки", restaurant_id=restaurant_id),
            ]
            session.add_all(categories)
            await session.commit()

            # Получаем id категорий
            for category in categories:
                await session.refresh(category)

            # Добавляем товары
            products = [
                Product(name="Американо", description="Классический черный кофе 250 мл", category_id=categories[0].id, restaurant_id=restaurant_id, price=150, size="250 мл", is_available=True, stock=100),
                Product(name="Капучино", description="Кофе с молоком и пенкой 300 мл", category_id=categories[0].id, restaurant_id=restaurant_id, price=210, discount_price=190, size="300 мл", is_available=True, stock=80),
                Product(name="Латте", description="Нежный латте с молоком 300 мл", category_id=categories[0].id, restaurant_id=restaurant_id, price=230, size="300 мл", is_available=True, stock=60),
                Product(name="Круассан", description="Сливочный круассан, свежая выпечка", category_id=categories[1].id, restaurant_id=restaurant_id, price=180, size="1 шт", is_available=True, stock=40),
                Product(name="Чизкейк", description="Классический Нью-Йорк чизкейк", category_id=categories[2].id, restaurant_id=restaurant_id, price=260, discount_price=240, size="1 порция", is_available=True, stock=20),
                Product(name="Омлет с сыром", description="Вкусный омлет с сыром", category_id=categories[3].id, restaurant_id=restaurant_id, price=250, size="200 г", is_available=True, stock=15),
            ]
            session.add_all(products)
            await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())