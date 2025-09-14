from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from shared.database import get_db
from admin_service.admin.auth import is_authenticated
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.models import Restaurant, Category, Product, Order, Discount
from pathlib import Path

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/restaurants", response_class=HTMLResponse)
async def list_restaurants(request: Request, db: AsyncSession = Depends(get_db)):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    result = await db.execute(select(Restaurant).order_by(Restaurant.name))
    restaurants = result.scalars().all()
    return templates.TemplateResponse("restaurants.html", {"request": request, "restaurants": restaurants})

@router.get("/restaurants/new", response_class=HTMLResponse)
async def new_restaurant_page(request: Request):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    return templates.TemplateResponse("restaurant_form.html", {"request": request, "restaurant": None})

@router.post("/restaurants")
async def create_restaurant(request: Request, name: str = Form(...), address: str = Form(...), db: AsyncSession = Depends(get_db)):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    restaurant = Restaurant(name=name, address=address)
    db.add(restaurant)
    await db.commit()
    request.session["flash"] = "Ресторан успешно создан!"
    return RedirectResponse(url="/admin/restaurants", status_code=303)

@router.get("/restaurants/{restaurant_id}/edit", response_class=HTMLResponse)
async def edit_restaurant_page(request: Request, restaurant_id: int, db: AsyncSession = Depends(get_db)):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return templates.TemplateResponse("restaurant_form.html", {"request": request, "restaurant": restaurant})

@router.post("/restaurants/{restaurant_id}/edit")
async def update_restaurant(request: Request, restaurant_id: int, name: str = Form(...), address: str = Form(...), db: AsyncSession = Depends(get_db)):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant.name = name
    restaurant.address = address
    await db.commit()
    request.session["flash"] = "Ресторан успешно обновлен!"
    return RedirectResponse(url="/admin/restaurants", status_code=303)

@router.post("/restaurants/{restaurant_id}/delete")
async def delete_restaurant(request: Request, restaurant_id: int, db: AsyncSession = Depends(get_db)):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    try:
        # Обнуляем restaurant_id во всех связанных записях
        # Обнуляем restaurant_id в заказах
        await db.execute(update(Order).where(Order.restaurant_id == restaurant_id).values(restaurant_id=None))
        
        # Обнуляем restaurant_id в продуктах
        await db.execute(update(Product).where(Product.restaurant_id == restaurant_id).values(restaurant_id=None))
        
        # Обнуляем restaurant_id в категориях
        await db.execute(update(Category).where(Category.restaurant_id == restaurant_id).values(restaurant_id=None))
        
        # Обнуляем restaurant_id в скидках
        await db.execute(update(Discount).where(Discount.restaurant_id == restaurant_id).values(restaurant_id=None))
        
        # Теперь удаляем сам ресторан
        await db.execute(delete(Restaurant).where(Restaurant.id == restaurant_id))
        
        await db.commit()
        request.session["flash"] = "Ресторан успешно удален! Связанные записи сохранены с пустым полем ресторана."
        
    except Exception as e:
        await db.rollback()
        request.session["flash"] = f"Ошибка при удалении ресторана: {str(e)}"
    
    return RedirectResponse(url="/admin/restaurants", status_code=303) 