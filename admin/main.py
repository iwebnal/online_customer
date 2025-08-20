from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import uvicorn
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
import os

from admin.routes import products, orders, discounts, restaurants
from admin.auth import login_user, logout_user, is_authenticated, require_auth

load_dotenv()

app = FastAPI(title="Online Customer Admin", version="1.0.0")

# Добавляем middleware для сессий
# Нужен для flash-сообщений и авторизации
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key"))

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
async def admin_panel(request: Request):
    # Проверяем авторизацию
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    return templates.TemplateResponse("index.html", {"request": request})


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
    uvicorn.run(app, host="0.0.0.0", port=8000)