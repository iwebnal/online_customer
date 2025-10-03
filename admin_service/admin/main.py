from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

# ВАЖНО: Загружаем переменные окружения ПЕРЕД импортом Telegram модуля
# Загружаем .env только если файл существует (для Docker контейнеров)
if os.path.exists('.env'):
    load_dotenv()

from admin_service.admin.routes import products, orders, discounts, restaurants, categories
from admin_service.admin.auth import login_user, logout_user, is_authenticated, require_auth
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.database import get_db
from shared.models import Order, User, Restaurant, Product, Discount
from shared.config import settings

from shared.telegram.sender import send_order_to_telegram, get_telegram_sender

import asyncio

app = FastAPI(title="Online Customer Admin", version="1.0.0")

# Добавляем middleware для сессий
# Нужен для flash-сообщений и авторизации
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY.encode())

# Добавляем CORS middleware для API эндпоинтов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Определяем абсолютные пути
ADMIN_DIR = Path(__file__).resolve().parent

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory=ADMIN_DIR / "static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory=ADMIN_DIR / "templates")

# Подключаем роуты
app.include_router(products.router, prefix="/admin", tags=["products"])
app.include_router(orders.router, prefix="/admin", tags=["orders"])
app.include_router(discounts.router, prefix="/admin", tags=["discounts"])
app.include_router(restaurants.router, prefix="/admin", tags=["restaurants"])
app.include_router(categories.router, prefix="/admin", tags=["categories"])


@app.get("/home", response_class=HTMLResponse)
async def admin_panel(request: Request, db: AsyncSession = Depends(get_db)):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    # Получаем последние 3 заказа
    stmt = select(Order).options(
        joinedload(Order.user),
        joinedload(Order.restaurant)
    ).order_by(Order.created_at.desc()).limit(3)
    result = await db.execute(stmt)
    recent_orders = result.scalars().unique().all()

    # Получаем статистику
    restaurants_result = await db.execute(select(func.count(Restaurant.id)))
    restaurants_count = restaurants_result.scalar()

    products_result = await db.execute(select(func.count(Product.id)))
    products_count = products_result.scalar()

    orders_result = await db.execute(select(func.count(Order.id)))
    orders_count = orders_result.scalar()

    discounts_result = await db.execute(select(func.count(Discount.id)))
    discounts_count = discounts_result.scalar()

    users_result = await db.execute(select(func.count(User.id)))
    users_count = users_result.scalar()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "recent_orders": recent_orders,
        "stats": {
            "restaurants": restaurants_count,
            "products": products_count,
            "orders": orders_count,
            "discounts": discounts_count,
            "users": users_count
        }
    })


@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Если уже авторизован, перенаправляем на главную
    if is_authenticated(request):
        return RedirectResponse(url="/home", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/admin/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if login_user(request, username, password):
        return RedirectResponse(url="/home", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверное имя пользователя или пароль"
        })


@app.get("/admin/logout")
async def logout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/admin/login", status_code=302)


# API эндпоинты для Mini App
@app.get("/api/restaurants")
async def get_restaurants_api(db: AsyncSession = Depends(get_db)):
    """Получить список всех ресторанов для Mini App"""
    stmt = select(Restaurant).order_by(Restaurant.name)
    result = await db.execute(stmt)
    restaurants = result.scalars().all()

    return {
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address
            } for r in restaurants
        ]
    }


@app.get("/api/products")
async def get_products_api(db: AsyncSession = Depends(get_db)):
    """Получить список всех товаров для Mini App"""
    stmt = select(Product).options(
        joinedload(Product.category),
        joinedload(Product.restaurant)
    )
    result = await db.execute(stmt)
    products = result.scalars().unique().all()

    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description or "",
                "price": p.price,
                "discount_price": p.discount_price,
                "size": p.size or "",
                "photo": p.photo or "",
                "is_available": p.is_available,
                "stock": p.stock,
                "category": {
                    "id": p.category.id if p.category else None,
                    "name": p.category.name if p.category else "Без категории"
                } if p.category else {"id": None, "name": "Без категории"},
                "restaurant_id": p.restaurant_id
            } for p in products if p.is_available
        ]
    }


@app.get("/api/categories")
async def get_categories_api(db: AsyncSession = Depends(get_db)):
    """Получить список всех категорий для Mini App"""
    from shared.models import Category
    stmt = select(Category)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    return {
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "restaurant_id": c.restaurant_id
            } for c in categories
        ]
    }


def send_telegram_notification_sync(telegram_data: dict):
    """Синхронная обертка для отправки уведомления в Telegram"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"🚀 Начинаем отправку уведомления в Telegram для заказа {telegram_data.get('order_id', 'unknown')}")

    try:
        # Создаем новый event loop для фоновой задачи
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(send_order_to_telegram(telegram_data))
            if result:
                logger.info(
                    f"✅ Уведомление в Telegram отправлено успешно для заказа {telegram_data.get('order_id', 'unknown')}")
            else:
                logger.warning(
                    f"⚠️ Не удалось отправить уведомление в Telegram для заказа {telegram_data.get('order_id', 'unknown')}")
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"💥 Критическая ошибка отправки уведомления в Telegram: {e}")
        return False




@app.post("/api/orders")
async def create_order_api(order_data: dict, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Создать новый заказ из Mini App"""
    try:
        # Создаем пользователя если его нет
        user = None
        if order_data.get("user"):
            user_data = order_data["user"]
            stmt = select(User).where(User.telegram_id == str(user_data.get("id")))
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    telegram_id=str(user_data.get("id")),
                    name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                    phone=order_data.get("phone", "")
                )
                db.add(user)
                await db.flush()

        # Получаем ресторан по переданному ID или первый доступный
        restaurant = None
        if order_data.get("restaurant_id"):
            stmt = select(Restaurant).where(Restaurant.id == order_data["restaurant_id"])
            result = await db.execute(stmt)
            restaurant = result.scalar_one_or_none()

        # Если ресторан не найден по ID, берем первый доступный
        if not restaurant:
            stmt = select(Restaurant).order_by(Restaurant.id)
            result = await db.execute(stmt)
            restaurant = result.scalars().first()

        if not restaurant:
            return {
                "status": "error",
                "message": "Нет доступных ресторанов в системе"
            }

        # Создаем заказ
        order = Order(
            user_id=user.id if user else None,
            restaurant_id=restaurant.id,  # Используем выбранный или первый доступный ресторан
            status="new",
            total=order_data.get("totalSum", 0),
            phone=order_data.get("phone", "")
        )
        db.add(order)
        await db.flush()

        # Создаем элементы заказа
        for item in order_data.get("order", []):
            from shared.models import OrderItem
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.get("id"),
                quantity=item.get("qty", 1),
                price=item.get("price", 0)
            )
            db.add(order_item)

        await db.commit()

        # Отправляем уведомление в Telegram
        try:
            # Получаем полную информацию о товарах из базы данных
            order_items_with_products = []
            for item in order_data.get("order", []):
                # Получаем информацию о товаре из базы данных
                product_stmt = select(Product).where(Product.id == item.get("id"))
                product_result = await db.execute(product_stmt)
                product = product_result.scalar_one_or_none()
                
                if product:
                    order_items_with_products.append({
                        "id": product.id,
                        "name": product.name,
                        "qty": item.get("qty", 1),
                        "price": item.get("price", 0)
                    })
                else:
                    # Если товар не найден, используем данные из заказа
                    order_items_with_products.append({
                        "id": item.get("id"),
                        "name": item.get("name", "Неизвестный товар"),
                        "qty": item.get("qty", 1),
                        "price": item.get("price", 0)
                    })

            # Подготавливаем данные для отправки в Telegram
            telegram_data = {
                "order_id": order.id,
                "user": order_data.get("user"),
                "address": order_data.get("address", "Не указан"),
                "order": order_items_with_products,
                "totalSum": order_data.get("totalSum", 0),
                "timestamp": order_data.get("timestamp"),
                "restaurant_id": restaurant.id
            }

            # Отправляем уведомление в фоновом режиме (не блокируем ответ)
            background_tasks.add_task(send_telegram_notification_sync, telegram_data)

        except Exception as telegram_error:
            # Логируем ошибку, но не прерываем создание заказа
            print(f"Ошибка отправки в Telegram: {telegram_error}")

        return {
            "status": "success",
            "message": "Заказ успешно создан",
            "order_id": order.id
        }

    except Exception as e:
        await db.rollback()
        return {
            "status": "error",
            "message": f"Ошибка создания заказа: {str(e)}"
        }


@app.post("/api/telegram/test")
async def test_telegram():
    """Тестирование отправки сообщения в Telegram"""
    try:
        sender = get_telegram_sender()
        success = await sender.send_test_message()

        if success:
            return {
                "status": "success",
                "message": "Тестовое сообщение отправлено в Telegram"
            }
        else:
            return {
                "status": "error",
                "message": "Не удалось отправить тестовое сообщение"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка тестирования Telegram: {str(e)}"
        }


@app.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Получить товар по ID"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/orders")
async def get_orders(db: AsyncSession = Depends(get_db)):
    """Получить список всех заказов"""
    stmt = select(Order).options(
        joinedload(Order.user),
        joinedload(Order.restaurant)
    ).order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    orders = result.scalars().unique().all()
    return orders


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.ADMIN_PORT)
