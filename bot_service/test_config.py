#!/usr/bin/env python3
"""
Тестовый скрипт для проверки конфигурации бота
"""

import os
import sys
from dotenv import load_dotenv

def test_config():
    print("🔍 Проверка конфигурации бота...")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем BOT_TOKEN
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не найден в переменных окружения")
        return False
    
    if bot_token == "your-bot-token-here":
        print("❌ BOT_TOKEN не настроен. Замените 'your-bot-token-here' на реальный токен.")
        print("📖 Инструкции: см. BOT_SETUP.md")
        return False
    
    print(f"✅ BOT_TOKEN настроен: {bot_token[:10]}...")
    
    # Проверяем DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return False
    
    print(f"✅ DATABASE_URL настроен: {database_url}")
    
    # Проверяем импорт настроек
    try:
        from shared.config import settings
        print(f"✅ Настройки загружены успешно")
        print(f"   - BOT_TOKEN из settings: {settings.BOT_TOKEN[:10] if settings.BOT_TOKEN else 'None'}...")
        print(f"   - DATABASE_URL из settings: {settings.DATABASE_URL}")
    except ImportError as e:
        print(f"❌ Ошибка импорта настроек: {e}")
        return False
    
    print("\n🎉 Конфигурация бота настроена правильно!")
    print("🚀 Можно запускать бота командой: python bot/main.py")
    
    return True

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
