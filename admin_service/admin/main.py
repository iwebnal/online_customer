from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import uvicorn
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from admin.routes import products, orders, discounts, restaurants
from admin.auth import login_user, logout_user, is_authenticated, require_auth
from shared.database import get_db
from shared.models import Order, User, Restaurant, Product, Discount
from shared.config import settings

load_dotenv()

app = FastAPI(title="Online Customer Admin", version="1.0.0")

# Добавляем middleware для сессий
# Нужен для flash-сообщений и авторизации
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

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

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.ADMIN_PORT)