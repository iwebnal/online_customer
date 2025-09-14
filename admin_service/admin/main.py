from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
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

from admin_service.admin.routes import products, orders, discounts, restaurants, categories
from admin_service.admin.auth import login_user, logout_user, is_authenticated, require_auth
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.database import get_db
from shared.models import Order, User, Restaurant, Product, Discount
from shared.config import settings

load_dotenv()

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


@app.get("/", response_class=HTMLResponse)
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
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/admin/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if login_user(request, username, password):
        return RedirectResponse(url="/", status_code=302)
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


@app.post("/api/orders")
async def create_order_api(order_data: dict, db: AsyncSession = Depends(get_db)):
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

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.ADMIN_PORT)