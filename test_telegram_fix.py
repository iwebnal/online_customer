#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Telegram интеграции
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

from shared.telegram.sender import get_telegram_sender


async def test_telegram_integration():
    """Тестирует интеграцию с Telegram"""
    print("🤖 Тестирование Telegram интеграции...")
    
    # Проверяем переменные окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '-1003068821769')
    
    print(f"📱 Chat ID: {chat_id}")
    print(f"🔑 Bot Token: {'установлен' if bot_token else 'НЕ установлен'}")
    
    if not bot_token:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
        return False
    
    # Получаем отправителя
    sender = get_telegram_sender()
    
    if not sender.is_initialized():
        error = sender.get_initialization_error()
        print(f"❌ Telegram Bot не инициализирован: {error}")
        return False
    
    print("✅ Telegram Bot инициализирован успешно")
    
    # Тестируем отправку тестового сообщения
    print("📤 Отправляем тестовое сообщение...")
    success = await sender.send_test_message()
    
    if success:
        print("✅ Тестовое сообщение отправлено успешно!")
        
        # Тестируем отправку уведомления о заказе
        print("📤 Отправляем тестовое уведомление о заказе...")
        
        test_order_data = {
            "order_id": 999,
            "user": {
                "id": 123456789,
                "first_name": "Тест",
                "last_name": "Пользователь",
                "username": "test_user"
            },
            "address": "Тестовый адрес, д. 1",
            "order": [
                {
                    "id": 1,
                    "name": "Тестовый товар 1",
                    "qty": 2,
                    "price": 100
                },
                {
                    "id": 2,
                    "name": "Тестовый товар 2", 
                    "qty": 1,
                    "price": 200
                }
            ],
            "totalSum": 400,
            "timestamp": "2024-01-01T12:00:00Z",
            "restaurant_id": 1
        }
        
        order_success = await sender.send_order_notification(test_order_data)
        
        if order_success:
            print("✅ Уведомление о заказе отправлено успешно!")
            return True
        else:
            print("❌ Ошибка отправки уведомления о заказе")
            return False
    else:
        print("❌ Ошибка отправки тестового сообщения")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_telegram_integration())
        if result:
            print("\n🎉 Все тесты прошли успешно!")
            sys.exit(0)
        else:
            print("\n💥 Тесты не прошли!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)