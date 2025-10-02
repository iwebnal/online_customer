#!/usr/bin/env python3
"""
Тестирование исправления проблемы с Telegram Bot
"""
import os
import sys
from dotenv import load_dotenv

def test_environment_loading():
    """Тестирует загрузку переменных окружения"""
    print("🔍 Тестирование загрузки переменных окружения...")
    
    # Загружаем переменные
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"   TELEGRAM_BOT_TOKEN: {'✅' if bot_token else '❌'}")
    print(f"   TELEGRAM_CHAT_ID: {'✅' if chat_id else '❌'}")
    
    return bool(bot_token)

def test_telegram_sender_after_fix():
    """Тестирует TelegramSender после исправления"""
    print("\n🔍 Тестирование TelegramSender после исправления...")
    
    try:
        from shared.telegram.sender import TelegramSender
        
        # Создаем экземпляр
        sender = TelegramSender()
        
        print(f"   bot_token: {'✅' if sender.bot_token else '❌'}")
        print(f"   chat_id: {'✅' if sender.chat_id else '❌'}")
        print(f"   bot: {'✅' if sender.bot else '❌'}")
        
        if sender.bot:
            print("   🎉 Telegram Bot инициализирован успешно!")
            return True
        else:
            print("   ❌ Telegram Bot НЕ инициализирован")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_global_sender():
    """Тестирует глобальный отправитель"""
    print("\n🔍 Тестирование глобального отправителя...")
    
    try:
        from shared.telegram.sender import get_telegram_sender
        
        sender = get_telegram_sender()
        
        print(f"   bot_token: {'✅' if sender.bot_token else '❌'}")
        print(f"   bot: {'✅' if sender.bot else '❌'}")
        
        if sender.bot:
            print("   🎉 Глобальный отправитель работает!")
            return True
        else:
            print("   ❌ Глобальный отправитель НЕ работает")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_telegram_sending():
    """Тестирует отправку сообщений"""
    print("\n🔍 Тестирование отправки сообщений...")
    
    try:
        from shared.telegram.sender import get_telegram_sender
        import asyncio
        
        sender = get_telegram_sender()
        
        if not sender.bot:
            print("   ❌ Bot не инициализирован, пропускаем тест отправки")
            return False
        
        # Тестируем отправку
        success = asyncio.run(sender.send_test_message())
        
        if success:
            print("   🎉 Тестовое сообщение отправлено успешно!")
            return True
        else:
            print("   ❌ Ошибка отправки тестового сообщения")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка тестирования отправки: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ TELEGRAM BOT")
    print("=" * 60)
    
    # Тестируем все компоненты
    env_ok = test_environment_loading()
    sender_ok = test_telegram_sender_after_fix()
    global_ok = test_global_sender()
    sending_ok = test_telegram_sending()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    print(f"Переменные окружения: {'✅' if env_ok else '❌'}")
    print(f"TelegramSender: {'✅' if sender_ok else '❌'}")
    print(f"Глобальный отправитель: {'✅' if global_ok else '❌'}")
    print(f"Отправка сообщений: {'✅' if sending_ok else '❌'}")
    
    if all([env_ok, sender_ok, global_ok, sending_ok]):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("   Проблема с Telegram Bot полностью исправлена!")
        print("   Ошибка 'Telegram Bot не инициализирован' больше не должна появляться")
    else:
        print("\n💥 НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        print("   Проблема может быть не полностью исправлена")
        
        if not env_ok:
            print("   - Проблема с переменными окружения")
        if not sender_ok:
            print("   - Проблема с инициализацией TelegramSender")
        if not global_ok:
            print("   - Проблема с глобальным отправителем")
        if not sending_ok:
            print("   - Проблема с отправкой сообщений")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
