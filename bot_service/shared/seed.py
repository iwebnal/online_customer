import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models import Base, Category, Product
# from db.models import Base, Category, Product

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/online_customer"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed():
    async with engine.begin() as conn:
        # Создаём таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Добавляем категории
        categories = [
            Category(name="Напитки"),
            Category(name="Завтраки"),
            Category(name="Десерты"),
        ]
        session.add_all(categories)
        await session.commit()

        # Получаем id категорий
        await session.refresh(categories[0])
        await session.refresh(categories[1])
        await session.refresh(categories[2])

        # Добавляем товары
        products = [
            Product(name="Капучино", description="Кофе с молоком", category_id=categories[0].id, price=150, size="250 мл", is_available=True, stock=10),
            Product(name="Американо", description="Классический черный кофе", category_id=categories[0].id, price=120, size="250 мл", is_available=True, stock=10),
            Product(name="Омлет с сыром", description="Вкусный омлет", category_id=categories[1].id, price=250, size="200 г", is_available=True, stock=5),
            Product(name="Каша овсяная", description="Полезная каша", category_id=categories[1].id, price=180, size="300 г", is_available=True, stock=5),
            Product(name="Чизкейк", description="Нежный десерт", category_id=categories[2].id, price=220, size="120 г", is_available=True, stock=7),
            Product(name="Эклер", description="Французский десерт", category_id=categories[2].id, price=90, size="80 г", is_available=True, stock=7),
        ]
        session.add_all(products)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())