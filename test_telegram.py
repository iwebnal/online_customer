#!/usr/bin/env python3
"""
Скрипт для тестирования отправки сообщений в Telegram
"""
import asyncio
import os
from dotenv import load_dotenv
from shared.telegram.sender import get_telegram_sender

# Загружаем переменные окружения
load_dotenv()

async def test_telegram():
    """Тестирует отправку сообщений в Telegram"""
    print("🤖 Тестирование Telegram интеграции...")
    
    # Проверяем наличие токена
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '-1003068821769')
    
    if not bot_token:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
        print("   Добавьте TELEGRAM_BOT_TOKEN=your-bot-token в файл .env")
        return False
    
    print(f"📱 Chat ID: {chat_id}")
    print(f"🔑 Bot Token: {bot_token[:10]}...")
    
    # Получаем отправителя
    sender = get_telegram_sender()
    
    if not sender.bot:
        print("❌ Ошибка: Telegram Bot не инициализирован")
        return False
    
    # Тестируем отправку тестового сообщения
    print("📤 Отправляем тестовое сообщение...")
    success = await sender.send_test_message()
    
    if success:
        print("✅ Тестовое сообщение отправлено успешно!")
        
        # Тестируем отправку уведомления о заказе
        print("📤 Отправляем тестовое уведомление о заказе...")
        
        test_order = {
            "order_id": 999,
            "user": {
                "id": 123456789,
                "first_name": "Тест",
                "last_name": "Пользователь",
                "username": "test_user"
            },
            "address": "г. Тестовый, ул. Тестовая, 1",
            "order": [
                {"name": "Американо", "qty": 2, "price": 150},
                {"name": "Круассан", "qty": 1, "price": 180}
            ],
            "totalSum": 480,
            "timestamp": "2024-01-15T12:00:00Z",
            "restaurant_id": 1
        }
        
        order_success = await sender.send_order_notification(test_order)
        
        if order_success:
            print("✅ Уведомление о заказе отправлено успешно!")
            return True
        else:
            print("❌ Ошибка отправки уведомления о заказе")
            return False
    else:
        print("❌ Ошибка отправки тестового сообщения")
        return False

async def main():
    """Основная функция"""
    print("=" * 50)
    print("🧪 ТЕСТИРОВАНИЕ TELEGRAM ИНТЕГРАЦИИ")
    print("=" * 50)
    
    success = await test_telegram()
    
    print("=" * 50)
    if success:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("   Telegram интеграция работает корректно")
    else:
        print("💥 ТЕСТЫ НЕ ПРОШЛИ!")
        print("   Проверьте настройки Telegram Bot")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
