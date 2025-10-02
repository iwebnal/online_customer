#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с Telegram Bot на сервере
"""
import os
import sys
from dotenv import load_dotenv

def check_telegram_library():
    """Проверяет установку библиотеки python-telegram-bot"""
    print("🔍 Проверка библиотеки python-telegram-bot...")
    
    try:
        import telegram
        print(f"✅ python-telegram-bot установлен, версия: {telegram.__version__}")
        return True
    except ImportError as e:
        print(f"❌ python-telegram-bot НЕ установлен: {e}")
        print("   Установите библиотеку: pip install python-telegram-bot>=20.0")
        return False
    except Exception as e:
        print(f"❌ Ошибка при импорте telegram: {e}")
        return False

def check_environment_variables():
    """Проверяет переменные окружения"""
    print("\n🔍 Проверка переменных окружения...")
    
    # Загружаем .env файл если есть
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Файл .env найден и загружен")
    else:
        print("⚠️  Файл .env не найден")
    
    # Проверяем токен
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        print(f"✅ TELEGRAM_BOT_TOKEN установлен: {bot_token[:10]}...")
    else:
        print("❌ TELEGRAM_BOT_TOKEN НЕ установлен")
        print("   Добавьте TELEGRAM_BOT_TOKEN=your-bot-token в файл .env")
    
    # Проверяем chat_id
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if chat_id:
        print(f"✅ TELEGRAM_CHAT_ID установлен: {chat_id}")
    else:
        print("⚠️  TELEGRAM_CHAT_ID не установлен, будет использован по умолчанию: -1003068821769")
    
    return bool(bot_token)

def check_telegram_bot_initialization():
    """Проверяет инициализацию Telegram Bot"""
    print("\n🔍 Проверка инициализации Telegram Bot...")
    
    try:
        from telegram import Bot
        from shared.telegram.sender import TelegramSender
        
        # Создаем экземпляр отправителя
        sender = TelegramSender()
        
        if sender.bot:
            print("✅ Telegram Bot инициализирован успешно")
            return True
        else:
            print("❌ Telegram Bot НЕ инициализирован")
            print("   Причина: отсутствует токен или библиотека")
            return False
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

def check_requirements():
    """Проверяет файл requirements.txt"""
    print("\n🔍 Проверка файла requirements.txt...")
    
    if os.path.exists('requirements.txt'):
        print("✅ Файл requirements.txt найден")
        
        with open('requirements.txt', 'r') as f:
            content = f.read()
            if 'python-telegram-bot' in content:
                print("✅ python-telegram-bot указан в requirements.txt")
            else:
                print("❌ python-telegram-bot НЕ указан в requirements.txt")
    else:
        print("❌ Файл requirements.txt не найден")

def suggest_solutions():
    """Предлагает решения проблем"""
    print("\n💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
    print("=" * 50)
    
    print("1. Установите библиотеку python-telegram-bot:")
    print("   pip install python-telegram-bot>=20.0")
    print("   или")
    print("   pip install -r requirements.txt")
    
    print("\n2. Настройте переменные окружения в файле .env:")
    print("   TELEGRAM_BOT_TOKEN=your-bot-token-here")
    print("   TELEGRAM_CHAT_ID=-1003068821769")
    
    print("\n3. Получите токен бота от @BotFather в Telegram")
    print("   и ID чата от @userinfobot")
    
    print("\n4. Перезапустите приложение после настройки")

def main():
    """Основная функция диагностики"""
    print("=" * 60)
    print("🔧 ДИАГНОСТИКА TELEGRAM BOT")
    print("=" * 60)
    
    # Проверяем текущую директорию
    print(f"📁 Текущая директория: {os.getcwd()}")
    
    # Проверяем все компоненты
    lib_ok = check_telegram_library()
    env_ok = check_environment_variables()
    init_ok = check_telegram_bot_initialization()
    check_requirements()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
    print("=" * 60)
    
    if lib_ok and env_ok and init_ok:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("   Telegram Bot должен работать корректно")
    else:
        print("💥 ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        suggest_solutions()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
