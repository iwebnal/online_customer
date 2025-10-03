#!/usr/bin/env python3
"""
Диагностический скрипт для проверки Telegram Bot на сервере
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Проверяет переменные окружения"""
    print("🔍 Проверка переменных окружения...")
    
    # Проверяем наличие .env файла
    env_file = Path('.env')
    if env_file.exists():
        print(f"✅ Файл .env найден: {env_file.absolute()}")
        
        # Читаем содержимое .env
        try:
            with open('.env', 'r') as f:
                content = f.read()
                if 'TELEGRAM_BOT_TOKEN' in content:
                    print("✅ TELEGRAM_BOT_TOKEN найден в .env")
                else:
                    print("❌ TELEGRAM_BOT_TOKEN НЕ найден в .env")
                    
                if 'TELEGRAM_CHAT_ID' in content:
                    print("✅ TELEGRAM_CHAT_ID найден в .env")
                else:
                    print("❌ TELEGRAM_CHAT_ID НЕ найден в .env")
        except Exception as e:
            print(f"❌ Ошибка чтения .env: {e}")
    else:
        print("❌ Файл .env не найден")
    
    # Загружаем переменные окружения
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Переменные окружения загружены из .env")
    except ImportError:
        print("⚠️  python-dotenv не установлен, используем системные переменные")
    except Exception as e:
        print(f"❌ Ошибка загрузки .env: {e}")
    
    # Проверяем переменные
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token:
        print(f"✅ TELEGRAM_BOT_TOKEN: {bot_token[:10]}...{bot_token[-4:]}")
    else:
        print("❌ TELEGRAM_BOT_TOKEN не установлен")
        
    if chat_id:
        print(f"✅ TELEGRAM_CHAT_ID: {chat_id}")
    else:
        print("❌ TELEGRAM_CHAT_ID не установлен")
    
    return bool(bot_token and chat_id)

def check_telegram_library():
    """Проверяет установку библиотеки Telegram"""
    print("\n🔍 Проверка библиотеки python-telegram-bot...")
    
    try:
        import telegram
        print(f"✅ python-telegram-bot установлена, версия: {telegram.__version__}")
        return True
    except ImportError as e:
        print(f"❌ python-telegram-bot не установлена: {e}")
        return False

def check_network_connectivity():
    """Проверяет сетевое подключение к Telegram API"""
    print("\n🔍 Проверка сетевого подключения...")
    
    try:
        import urllib.request
        import urllib.error
        
        # Проверяем доступность Telegram API
        try:
            response = urllib.request.urlopen('https://api.telegram.org', timeout=10)
            print("✅ Подключение к api.telegram.org успешно")
            return True
        except urllib.error.URLError as e:
            print(f"❌ Ошибка подключения к api.telegram.org: {e}")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки сети: {e}")
        return False

async def test_telegram_bot():
    """Тестирует инициализацию и отправку сообщения в Telegram"""
    print("\n🔍 Тестирование Telegram Bot...")
    
    try:
        from telegram import Bot
        from telegram.error import TelegramError
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ Отсутствуют необходимые переменные окружения")
            return False
        
        # Инициализируем бота
        bot = Bot(token=bot_token)
        print("✅ Telegram Bot инициализирован")
        
        # Проверяем информацию о боте
        try:
            bot_info = await bot.get_me()
            print(f"✅ Информация о боте: @{bot_info.username} ({bot_info.first_name})")
        except TelegramError as e:
            print(f"❌ Ошибка получения информации о боте: {e}")
            return False
        
        # Отправляем тестовое сообщение
        try:
            message = "🤖 Тестовое сообщение от диагностического скрипта"
            await bot.send_message(chat_id=chat_id, text=message)
            print("✅ Тестовое сообщение отправлено успешно")
            return True
        except TelegramError as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def check_docker_environment():
    """Проверяет, запущен ли скрипт в Docker контейнере"""
    print("\n🔍 Проверка Docker окружения...")
    
    # Проверяем наличие Docker файлов
    if Path('/.dockerenv').exists():
        print("✅ Скрипт запущен в Docker контейнере")
        return True
    else:
        print("ℹ️  Скрипт запущен не в Docker контейнере")
        return False

def check_application_integration():
    """Проверяет интеграцию с основным приложением"""
    print("\n🔍 Проверка интеграции с приложением...")
    
    try:
        # Добавляем путь к shared модулю
        sys.path.append(str(Path(__file__).parent))
        
        from shared.telegram.sender import get_telegram_sender
        
        sender = get_telegram_sender()
        
        if sender.bot:
            print("✅ TelegramSender инициализирован успешно")
            return True
        else:
            print("❌ TelegramSender не инициализирован")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки интеграции: {e}")
        return False

async def main():
    """Основная функция диагностики"""
    print("🚀 Диагностика Telegram Bot на сервере")
    print("=" * 50)
    
    results = []
    
    # Выполняем все проверки
    results.append(("Переменные окружения", check_environment()))
    results.append(("Библиотека Telegram", check_telegram_library()))
    results.append(("Сетевое подключение", check_network_connectivity()))
    results.append(("Docker окружение", check_docker_environment()))
    results.append(("Интеграция с приложением", check_application_integration()))
    
    # Тестируем Telegram Bot
    if all(result for _, result in results[:3]):  # Если базовые проверки прошли
        telegram_result = await test_telegram_bot()
        results.append(("Тест Telegram Bot", telegram_result))
    
    # Выводим итоги
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ОШИБКА"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("   Telegram Bot должен работать корректно.")
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("   См. детали выше для исправления.")
    
    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Диагностика прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)
