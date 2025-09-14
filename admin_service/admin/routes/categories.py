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
from shared.models import Category, Restaurant
from typing import Optional
from pathlib import Path

router = APIRouter()

# Определяем абсолютный путь к шаблонам
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# HTML роуты
@router.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница управления категориями"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    stmt = select(Category).options(joinedload(Category.restaurant))
    result = await db.execute(stmt)
    categories = result.scalars().unique().all()
    
    flash_message = request.session.pop("flash", None)
    
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "categories": categories,
        "flash_message": flash_message
    })


@router.get("/categories/new", response_class=HTMLResponse)
async def new_category_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница создания новой категории"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    selected_restaurant_id = restaurants[0].id if restaurants else None
    return templates.TemplateResponse("category_form.html", {
        "request": request,
        "category": None,
        "restaurants": restaurants,
        "selected_restaurant_id": selected_restaurant_id
    })


@router.get("/categories/{category_id}/edit", response_class=HTMLResponse)
async def edit_category_page(request: Request, category_id: int, db: AsyncSession = Depends(get_db)):
    """Страница редактирования категории"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    return templates.TemplateResponse("category_form.html", {
        "request": request,
        "category": category,
        "restaurants": restaurants,
        "selected_restaurant_id": category.restaurant_id if category else None
    })


# API роуты
@router.get("/api/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Получить список всех категорий"""
    stmt = select(Category).options(joinedload(Category.restaurant))
    result = await db.execute(stmt)
    categories = result.scalars().unique().all()
    return {"categories": [{"id": c.id, "name": c.name, "restaurant": c.restaurant.name} for c in categories]}


@router.get("/categories/{category_id}")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Получить категорию по ID"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/categories")
async def create_category(
        request: Request,
        name: str = Form(...),
        restaurant_id: int = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """Создать новую категорию"""
    category = Category(
        name=name,
        restaurant_id=restaurant_id
    )
    db.add(category)
    await db.commit()
    
    request.session["flash"] = "Категория создана успешно!"
    
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.post("/categories/{category_id}")
async def update_category(
        request: Request,
        category_id: int,
        name: str = Form(...),
        restaurant_id: int = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """Обновить категорию"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = name
    category.restaurant_id = restaurant_id

    await db.commit()

    request.session["flash"] = "Категория успешно обновлена!"

    return RedirectResponse(url="/admin/categories", status_code=303)


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить категорию"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await db.execute(delete(Category).where(Category.id == category_id))
    await db.commit()
    return {"message": "Категория удалена"}
