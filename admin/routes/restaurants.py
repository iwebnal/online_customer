from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from admin.database import get_db
from db.models import Restaurant
from pathlib import Path

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/restaurants", response_class=HTMLResponse)
async def list_restaurants(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant))
    restaurants = result.scalars().all()
    return templates.TemplateResponse("restaurants.html", {"request": request, "restaurants": restaurants})

@router.get("/restaurants/new", response_class=HTMLResponse)
async def new_restaurant_page(request: Request):
    return templates.TemplateResponse("restaurant_form.html", {"request": request, "restaurant": None})

@router.post("/restaurants")
async def create_restaurant(request: Request, name: str = Form(...), address: str = Form(...), db: AsyncSession = Depends(get_db)):
    restaurant = Restaurant(name=name, address=address)
    db.add(restaurant)
    await db.commit()
    request.session["flash"] = "Ресторан успешно создан!"
    return RedirectResponse(url="/admin/restaurants", status_code=303)

@router.get("/restaurants/{restaurant_id}/edit", response_class=HTMLResponse)
async def edit_restaurant_page(request: Request, restaurant_id: int, db: AsyncSession = Depends(get_db)):
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return templates.TemplateResponse("restaurant_form.html", {"request": request, "restaurant": restaurant})

@router.post("/restaurants/{restaurant_id}/edit")
async def update_restaurant(request: Request, restaurant_id: int, name: str = Form(...), address: str = Form(...), db: AsyncSession = Depends(get_db)):
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
    restaurant = await db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    await db.delete(restaurant)
    await db.commit()
    request.session["flash"] = "Ресторан успешно удален!"
    return RedirectResponse(url="/admin/restaurants", status_code=303) 