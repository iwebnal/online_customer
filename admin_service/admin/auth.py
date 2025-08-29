from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем учетные данные из переменных окружения
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def get_current_user(request: Request) -> Optional[str]:
    """Получить текущего пользователя из сессии"""
    return request.session.get("user")

def require_auth(request: Request) -> str:
    """Проверить авторизацию пользователя"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

def login_user(request: Request, username: str, password: str) -> bool:
    """Авторизовать пользователя"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["user"] = username
        return True
    return False

def logout_user(request: Request):
    """Выйти из системы"""
    request.session.pop("user", None)

def is_authenticated(request: Request) -> bool:
    """Проверить, авторизован ли пользователь"""
    return get_current_user(request) is not None
