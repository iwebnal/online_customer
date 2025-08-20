#!/usr/bin/env python3
"""
Скрипт для тестирования авторизации админ-панели
"""

import os
from dotenv import load_dotenv
from admin.auth import login_user, is_authenticated, logout_user

# Загружаем переменные окружения
load_dotenv()

def test_auth():
    """Тестируем функции авторизации"""
    print("=== Тест авторизации админ-панели ===")
    
    # Получаем учетные данные из переменных окружения
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    print(f"Логин: {admin_username}")
    print(f"Пароль: {admin_password}")
    
    # Создаем mock request объект
    class MockRequest:
        def __init__(self):
            self.session = {}
    
    request = MockRequest()
    
    # Тест 1: Проверяем, что пользователь не авторизован изначально
    print("\n1. Проверка начального состояния:")
    print(f"Авторизован: {is_authenticated(request)}")
    
    # Тест 2: Пытаемся войти с правильными данными
    print("\n2. Попытка входа с правильными данными:")
    success = login_user(request, admin_username, admin_password)
    print(f"Успешный вход: {success}")
    print(f"Авторизован: {is_authenticated(request)}")
    
    # Тест 3: Пытаемся войти с неправильными данными
    print("\n3. Попытка входа с неправильными данными:")
    success = login_user(request, "wrong_user", "wrong_pass")
    print(f"Успешный вход: {success}")
    
    # Тест 4: Выход из системы
    print("\n4. Выход из системы:")
    logout_user(request)
    print(f"Авторизован: {is_authenticated(request)}")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_auth()
