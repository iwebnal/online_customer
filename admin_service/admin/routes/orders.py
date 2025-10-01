from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from shared.database import get_db
from admin_service.admin.auth import is_authenticated
from shared.models import Order, User, OrderItem, Product, Restaurant
from datetime import datetime
from typing import List
from pathlib import Path

router = APIRouter()

# Определяем абсолютный путь к шаблонам
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# API роуты
# @router.get("/api/orders")
# async def get_orders(db: AsyncSession = Depends(get_db)):
#     """Получить список всех заказов"""
#     stmt = select(Order).options(
#         joinedload(Order.user),
#         joinedload(Order.restaurant)
#     ).order_by(Order.created_at.desc())
#     result = await db.execute(stmt)
#     orders = result.scalars().unique().all()
#     return orders


@router.get("/api/recent-orders")
async def get_recent_orders(db: AsyncSession = Depends(get_db)):
    """Получить последние 3 заказа"""
    stmt = select(Order).options(
        joinedload(Order.user),
        joinedload(Order.restaurant)
    ).order_by(Order.created_at.desc()).limit(3)
    result = await db.execute(stmt)
    orders = result.scalars().unique().all()
    return orders


# HTML роуты
@router.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request, db: AsyncSession = Depends(get_db), restaurant_id: int = None):
    """Страница управления заказами"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    query = select(Order).options(
        joinedload(Order.user),
        joinedload(Order.restaurant)
    )
    if restaurant_id:
        query = query.where(Order.restaurant_id == restaurant_id)
    result = await db.execute(query)
    orders = result.scalars().unique().all()
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    flash_message = request.session.pop("flash", None)
    return templates.TemplateResponse("orders.html", {
        "request": request,
        "orders": orders,
        "flash_message": flash_message,
        "restaurants": restaurants,
        "selected_restaurant_id": restaurant_id
    })


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_details_page(request: Request, order_id: int, db: AsyncSession = Depends(get_db)):
    """Страница с деталями заказа"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    stmt = select(Order).options(
        joinedload(Order.user),
        joinedload(Order.restaurant),
        joinedload(Order.items).joinedload(OrderItem.product)
    ).where(Order.id == order_id)
    
    result = await db.execute(stmt)
    order = result.scalars().unique().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
        
    return templates.TemplateResponse("order_detail.html", {
        "request": request,
        "order": order
    })


@router.put("/orders/{order_id}/status")
async def update_order_status(
        order_id: int,
        status: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """Обновить статус заказа"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    if status == "paid":
        order.paid_at = datetime.now()

    await db.commit()
    return {"message": f"Статус заказа {order_id} обновлен"}


# API роуты
@router.get("/api/orders/{order_id}")
async def get_order_details(order_id: int, db: AsyncSession = Depends(get_db)):
    """Получить заказ по ID (API)"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
