from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload

from shared.database import get_db
from admin_service.admin.auth import is_authenticated
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.models import Discount, Category, Product, Restaurant
from typing import Optional
from datetime import datetime
from pathlib import Path

router = APIRouter()

# Определяем абсолютный путь к шаблонам
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# API роуты
@router.get("/api/discounts")
async def get_discounts(db: AsyncSession = Depends(get_db)):
    """Получить список всех скидок"""
    stmt = select(Discount).options(
        joinedload(Discount.category),
        joinedload(Discount.product)
    )
    result = await db.execute(stmt)
    discounts = result.scalars().unique().all()
    return discounts


# HTML роуты
@router.get("/discounts", response_class=HTMLResponse)
async def discounts_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница управления скидками"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    stmt = select(Discount).options(
        joinedload(Discount.category),
        joinedload(Discount.product)
    )
    result = await db.execute(stmt)
    discounts = result.scalars().unique().all()

    flash_message = request.session.pop("flash", None)

    return templates.TemplateResponse("discounts.html", {
        "request": request,
        "discounts": discounts,
        "flash_message": flash_message
    })


@router.get("/discounts/new", response_class=HTMLResponse)
async def new_discount_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница создания новой скидки"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    result = await db.execute(select(Product))
    products = result.scalars().all()
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    selected_restaurant_id = restaurants[0].id if restaurants else None
    return templates.TemplateResponse("discount_form.html", {
        "request": request,
        "discount": None,
        "categories": categories,
        "products": products,
        "restaurants": restaurants,
        "selected_restaurant_id": selected_restaurant_id
    })


@router.post("/discounts")
async def create_discount(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        date_start: Optional[datetime] = Form(None),
        date_end: Optional[datetime] = Form(None),
        category_id: Optional[int] = Form(None),
        product_id: Optional[int] = Form(None),
        restaurant_id: int = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """Создать новую скидку"""
    discount = Discount(
        title=title,
        description=description,
        date_start=date_start,
        date_end=date_end,
        category_id=category_id,
        product_id=product_id,
        restaurant_id=restaurant_id,
        is_active=True
    )
    db.add(discount)
    await db.commit()

    request.session["flash"] = "Скидка создана успешно!"
    return RedirectResponse(url="/admin/discounts", status_code=303)


@router.get("/discounts/{discount_id}")
async def get_discount(discount_id: int, db: AsyncSession = Depends(get_db)):
    """Получить скидку по ID"""
    result = await db.execute(select(Discount).where(Discount.id == discount_id))
    discount = result.scalar_one_or_none()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount


@router.put("/discounts/{discount_id}")
async def update_discount(
        request: Request,
        discount_id: int,
        title: str = Form(...),
        description: str = Form(...),
        date_start: Optional[datetime] = Form(None),
        date_end: Optional[datetime] = Form(None),
        category_id: Optional[int] = Form(None),
        product_id: Optional[int] = Form(None),
        db: AsyncSession = Depends(get_db)
):
    """Обновить скидку"""
    result = await db.execute(select(Discount).where(Discount.id == discount_id))
    discount = result.scalar_one_or_none()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    discount.title = title
    discount.description = description
    discount.date_start = date_start
    discount.date_end = date_end
    discount.category_id = category_id
    discount.product_id = product_id

    await db.commit()
    
    request.session["flash"] = "Скидка успешно обновлена!"
    return RedirectResponse(url="/admin/discounts", status_code=303)


@router.post("/discounts/{discount_id}/edit")
async def update_discount_form(
        request: Request,
        discount_id: int,
        title: str = Form(...),
        description: str = Form(...),
        date_start: Optional[datetime] = Form(None),
        date_end: Optional[datetime] = Form(None),
        category_id: Optional[int] = Form(None),
        product_id: Optional[int] = Form(None),
        restaurant_id: int = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """Обновить скидку через HTML-форму (POST)"""
    result = await db.execute(select(Discount).where(Discount.id == discount_id))
    discount = result.scalar_one_or_none()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    discount.title = title
    discount.description = description
    discount.date_start = date_start if date_start else None
    discount.date_end = date_end if date_end else None
    discount.category_id = int(category_id) if category_id not in (None, "") else None
    discount.product_id = int(product_id) if product_id not in (None, "") else None
    discount.restaurant_id = restaurant_id
    await db.commit()
    request.session["flash"] = "Скидка успешно обновлена!"
    return RedirectResponse(url="/admin/discounts", status_code=303)


@router.post("/discounts/{discount_id}/toggle")
async def toggle_active_status(request: Request, discount_id: int, db: AsyncSession = Depends(get_db)):
    """Активировать/деактивировать скидку"""
    result = await db.execute(select(Discount).where(Discount.id == discount_id))
    discount = result.scalar_one_or_none()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    discount.__dict__['is_active'] = not bool(discount.is_active)
    await db.commit()
    
    status = "активирована" if discount.is_active else "деактивирована"
    request.session["flash"] = f"Скидка '{discount.title}' была успешно {status}."
    return RedirectResponse(url="/admin/discounts", status_code=303)


@router.post("/discounts/{discount_id}/delete")
async def delete_discount(request: Request, discount_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить скидку"""
    await db.execute(delete(Discount).where(Discount.id == discount_id))
    await db.commit()
    
    request.session["flash"] = "Скидка была успешно удалена."
    return RedirectResponse(url="/admin/discounts", status_code=303)


@router.get("/discounts/{discount_id}/edit", response_class=HTMLResponse)
async def edit_discount_page(request: Request, discount_id: int, db: AsyncSession = Depends(get_db)):
    """Страница редактирования скидки"""
    stmt = select(Discount).where(Discount.id == discount_id)
    result = await db.execute(stmt)
    discount = result.scalar_one_or_none()
    
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    result = await db.execute(select(Category))
    categories = result.scalars().all()
    
    result = await db.execute(select(Product))
    products = result.scalars().all()
    
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    
    return templates.TemplateResponse("discount_form.html", {
        "request": request,
        "discount": discount,
        "categories": categories,
        "products": products,
        "restaurants": restaurants,
        "selected_restaurant_id": discount.restaurant_id if discount else None
    })
