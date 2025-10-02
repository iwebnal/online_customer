#!/usr/bin/env python3
"""
Скрипт для исправления проблемы с загрузкой переменных окружения Telegram
"""
import os
import sys
from dotenv import load_dotenv

def fix_telegram_env():
    """Исправляет проблему с загрузкой переменных окружения"""
    print("🔧 Исправление проблемы с Telegram Bot...")
    
    # 1. Загружаем переменные из .env
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Переменные загружены из .env файла")
    else:
        print("❌ Файл .env не найден")
        return False
    
    # 2. Проверяем токен
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '-1003068821769')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле")
        return False
    
    print(f"✅ Токен найден: {bot_token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    # 3. Тестируем инициализацию
    try:
        from shared.telegram.sender import TelegramSender
        sender = TelegramSender()
        
        if sender.bot:
            print("✅ Telegram Bot инициализирован успешно!")
            return True
        else:
            print("❌ Telegram Bot не инициализирован")
            print(f"   Токен: {sender.bot_token}")
            print(f"   Bot объект: {sender.bot}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

def test_telegram_sending():
    """Тестирует отправку сообщений"""
    print("\n🧪 Тестирование отправки сообщений...")
    
    try:
        from shared.telegram.sender import get_telegram_sender
        sender = get_telegram_sender()
        
        if not sender.bot:
            print("❌ Bot не инициализирован")
            return False
        
        # Тестируем отправку
        import asyncio
        success = asyncio.run(sender.send_test_message())
        
        if success:
            print("✅ Тестовое сообщение отправлено успешно!")
            return True
        else:
            print("❌ Ошибка отправки тестового сообщения")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("🔧 ИСПРАВЛЕНИЕ TELEGRAM BOT")
    print("=" * 60)
    
    # Исправляем проблему
    if fix_telegram_env():
        print("\n✅ Проблема исправлена!")
        
        # Тестируем отправку
        if test_telegram_sending():
            print("\n🎉 ВСЕ РАБОТАЕТ КОРРЕКТНО!")
            print("   Telegram Bot полностью функционален")
        else:
            print("\n⚠️  Bot инициализирован, но есть проблемы с отправкой")
    else:
        print("\n❌ ПРОБЛЕМА НЕ ИСПРАВЛЕНА")
        print("   Проверьте настройки в файле .env")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
