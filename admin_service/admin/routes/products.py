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
from shared.models import Product, Category, Restaurant
from typing import Optional
from pathlib import Path

router = APIRouter()

# Определяем абсолютный путь к шаблонам
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# HTML роуты
@router.get("/products", response_class=HTMLResponse)
async def products_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница управления товарами"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    stmt = select(Product).options(joinedload(Product.category))
    result = await db.execute(stmt)
    products = result.scalars().unique().all()
    
    flash_message = request.session.pop("flash", None)
    
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
        "flash_message": flash_message
    })


@router.get("/products/new", response_class=HTMLResponse)
async def new_product_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница создания нового товара"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    selected_restaurant_id = restaurants[0].id if restaurants else None
    return templates.TemplateResponse("product_form.html", {
        "request": request,
        "categories": categories,
        "restaurants": restaurants,
        "product": None,
        "selected_restaurant_id": selected_restaurant_id
    })


@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
async def edit_product_page(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    """Страница редактирования товара"""
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    return templates.TemplateResponse("product_form.html", {
        "request": request,
        "product": product,
        "categories": categories,
        "restaurants": restaurants,
        "selected_restaurant_id": product.restaurant_id if product else None
    })


# API роуты
@router.get("/api/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    """Получить список всех товаров"""
    stmt = select(Product).options(joinedload(Product.category))
    result = await db.execute(stmt)
    products = result.scalars().unique().all()
    return {"products": [{"id": p.id, "name": p.name, "price": p.price, "category": p.category.name} for p in products]}


@router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Получить товар по ID"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products")
async def create_product(
        request: Request,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        restaurant_id: int = Form(...),
        size: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db)
):
    """Создать новый товар"""
    product = Product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        restaurant_id=restaurant_id,
        size=size,
        is_available=True,
        stock=0
    )
    db.add(product)
    await db.commit()
    
    request.session["flash"] = "Товар создан успешно!"
    
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/products/{product_id}")
async def update_product(
        request: Request,
        product_id: int,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        category_id: int = Form(...),
        restaurant_id: int = Form(...),
        size: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db)
):
    """Обновить товар"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = name
    product.description = description
    product.price = price
    product.category_id = category_id
    product.restaurant_id = restaurant_id
    product.size = size

    await db.commit()

    request.session["flash"] = "Товар успешно обновлен!"

    return RedirectResponse(url="/admin/products", status_code=303)


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить товар"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()
    return {"message": "Товар удален"}
