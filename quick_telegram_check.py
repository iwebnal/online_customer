#!/usr/bin/env python3
"""
Быстрая проверка Telegram Bot на сервере
"""
import os
import sys

def quick_check():
    print("🔍 Быстрая проверка Telegram Bot...")
    
    # 1. Проверяем импорт
    try:
        from telegram import Bot
        print("✅ Библиотека telegram импортируется")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Решение: pip install python-telegram-bot>=20.0")
        return False
    
    # 2. Проверяем переменные окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не установлен")
        print("Решение: добавьте TELEGRAM_BOT_TOKEN=your-token в .env")
        return False
    else:
        print(f"✅ TELEGRAM_BOT_TOKEN установлен: {bot_token[:10]}...")
    
    # 3. Проверяем инициализацию
    try:
        from shared.telegram.sender import TelegramSender
        sender = TelegramSender()
        
        if sender.bot:
            print("✅ Telegram Bot инициализирован успешно")
            return True
        else:
            print("❌ Telegram Bot не инициализирован")
            return False
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

if __name__ == "__main__":
    success = quick_check()
    if success:
        print("\n🎉 Telegram Bot работает!")
    else:
        print("\n💥 Проблемы с Telegram Bot!")
        print("Запустите полную диагностику: python telegram_debug.py")
