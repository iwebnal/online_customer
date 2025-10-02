#!/usr/bin/env python3
"""
Продвинутая диагностика проблем с Telegram Bot
"""
import os
import sys
import traceback
from dotenv import load_dotenv

def debug_environment():
    """Детальная диагностика переменных окружения"""
    print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 60)
    
    # 1. Проверяем файл .env
    print("1. Проверка файла .env:")
    if os.path.exists('.env'):
        print("   ✅ Файл .env найден")
        with open('.env', 'r') as f:
            content = f.read()
            if 'TELEGRAM_BOT_TOKEN' in content:
                print("   ✅ TELEGRAM_BOT_TOKEN найден в файле")
            else:
                print("   ❌ TELEGRAM_BOT_TOKEN НЕ найден в файле")
            if 'TELEGRAM_CHAT_ID' in content:
                print("   ✅ TELEGRAM_CHAT_ID найден в файле")
            else:
                print("   ⚠️  TELEGRAM_CHAT_ID не найден в файле")
    else:
        print("   ❌ Файл .env НЕ найден")
        return False
    
    # 2. Загружаем переменные
    print("\n2. Загрузка переменных из .env:")
    try:
        load_dotenv()
        print("   ✅ load_dotenv() выполнен успешно")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки .env: {e}")
        return False
    
    # 3. Проверяем переменные после загрузки
    print("\n3. Проверка переменных после загрузки:")
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"   TELEGRAM_BOT_TOKEN: {'✅ Установлен' if bot_token else '❌ НЕ установлен'}")
    if bot_token:
        print(f"   Длина токена: {len(bot_token)} символов")
        print(f"   Начало токена: {bot_token[:10]}...")
    
    print(f"   TELEGRAM_CHAT_ID: {'✅ Установлен' if chat_id else '❌ НЕ установлен'}")
    if chat_id:
        print(f"   Chat ID: {chat_id}")
    
    return bool(bot_token)

def debug_telegram_import():
    """Диагностика импорта библиотеки telegram"""
    print("\n🔍 ДИАГНОСТИКА ИМПОРТА TELEGRAM")
    print("=" * 60)
    
    # 1. Проверяем импорт telegram
    print("1. Импорт telegram:")
    try:
        import telegram
        print(f"   ✅ telegram импортирован, версия: {telegram.__version__}")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта telegram: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Другая ошибка: {e}")
        return False
    
    # 2. Проверяем импорт Bot
    print("\n2. Импорт Bot:")
    try:
        from telegram import Bot
        print("   ✅ Bot импортирован успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта Bot: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Другая ошибка: {e}")
        return False
    
    # 3. Проверяем импорт TelegramError
    print("\n3. Импорт TelegramError:")
    try:
        from telegram.error import TelegramError
        print("   ✅ TelegramError импортирован успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта TelegramError: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Другая ошибка: {e}")
        return False
    
    return True

def debug_telegram_sender_import():
    """Диагностика импорта TelegramSender"""
    print("\n🔍 ДИАГНОСТИКА ИМПОРТА TELEGRAM SENDER")
    print("=" * 60)
    
    # 1. Проверяем импорт TelegramSender
    print("1. Импорт TelegramSender:")
    try:
        from shared.telegram.sender import TelegramSender
        print("   ✅ TelegramSender импортирован успешно")
    except ImportError as e:
        print(f"   ❌ Ошибка импорта TelegramSender: {e}")
        print(f"   Полная ошибка: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"   ❌ Другая ошибка: {e}")
        print(f"   Полная ошибка: {traceback.format_exc()}")
        return False
    
    return True

def debug_telegram_sender_initialization():
    """Диагностика инициализации TelegramSender"""
    print("\n🔍 ДИАГНОСТИКА ИНИЦИАЛИЗАЦИИ TELEGRAM SENDER")
    print("=" * 60)
    
    try:
        from shared.telegram.sender import TelegramSender
        
        print("1. Создание экземпляра TelegramSender:")
        sender = TelegramSender()
        print("   ✅ Экземпляр создан успешно")
        
        print(f"\n2. Проверка атрибутов:")
        print(f"   bot_token: {'✅ Установлен' if sender.bot_token else '❌ НЕ установлен'}")
        if sender.bot_token:
            print(f"   Длина токена: {len(sender.bot_token)}")
            print(f"   Начало токена: {sender.bot_token[:10]}...")
        
        print(f"   chat_id: {'✅ Установлен' if sender.chat_id else '❌ НЕ установлен'}")
        if sender.chat_id:
            print(f"   Chat ID: {sender.chat_id}")
        
        print(f"   bot: {'✅ Инициализирован' if sender.bot else '❌ НЕ инициализирован'}")
        
        if not sender.bot:
            print("\n3. Анализ причин неудачи инициализации:")
            if not sender.bot_token:
                print("   ❌ Причина: bot_token отсутствует")
            else:
                print("   ✅ bot_token присутствует")
                
            # Проверяем импорт Bot
            try:
                from telegram import Bot
                print("   ✅ Bot импортируется")
                
                # Пробуем создать Bot вручную
                print("   🧪 Тестирование создания Bot вручную:")
                test_bot = Bot(token=sender.bot_token)
                print("   ✅ Bot создается успешно")
                
            except Exception as e:
                print(f"   ❌ Ошибка создания Bot: {e}")
                print(f"   Полная ошибка: {traceback.format_exc()}")
        
        return sender.bot is not None
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        print(f"Полная ошибка: {traceback.format_exc()}")
        return False

def debug_global_sender():
    """Диагностика глобального отправителя"""
    print("\n🔍 ДИАГНОСТИКА ГЛОБАЛЬНОГО ОТПРАВИТЕЛЯ")
    print("=" * 60)
    
    try:
        from shared.telegram.sender import get_telegram_sender
        
        print("1. Получение глобального отправителя:")
        sender = get_telegram_sender()
        print("   ✅ Глобальный отправитель получен")
        
        print(f"2. Проверка состояния:")
        print(f"   bot_token: {'✅ Установлен' if sender.bot_token else '❌ НЕ установлен'}")
        print(f"   bot: {'✅ Инициализирован' if sender.bot else '❌ НЕ инициализирован'}")
        
        return sender.bot is not None
        
    except Exception as e:
        print(f"❌ Ошибка получения глобального отправителя: {e}")
        print(f"Полная ошибка: {traceback.format_exc()}")
        return False

def suggest_solutions():
    """Предлагает решения на основе диагностики"""
    print("\n💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ")
    print("=" * 60)
    
    print("1. Если проблема с переменными окружения:")
    print("   - Убедитесь, что файл .env находится в корне проекта")
    print("   - Проверьте права доступа к файлу .env")
    print("   - Убедитесь, что в .env нет лишних пробелов")
    
    print("\n2. Если проблема с импортом:")
    print("   - Переустановите библиотеку: pip install python-telegram-bot>=20.0")
    print("   - Проверьте версию Python: python3 --version")
    print("   - Очистите кэш Python: find . -name '*.pyc' -delete")
    
    print("\n3. Если проблема с инициализацией:")
    print("   - Проверьте токен бота в @BotFather")
    print("   - Убедитесь, что бот не заблокирован")
    print("   - Проверьте интернет-соединение сервера")
    
    print("\n4. Принудительная загрузка переменных:")
    print("   - Добавьте load_dotenv() в начало основного приложения")
    print("   - Или установите переменные окружения системно")

def main():
    """Основная функция диагностики"""
    print("🔧 ПРОДВИНУТАЯ ДИАГНОСТИКА TELEGRAM BOT")
    print("=" * 60)
    
    # Проверяем все компоненты
    env_ok = debug_environment()
    import_ok = debug_telegram_import()
    sender_import_ok = debug_telegram_sender_import()
    init_ok = debug_telegram_sender_initialization()
    global_ok = debug_global_sender()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
    print("=" * 60)
    
    print(f"Переменные окружения: {'✅' if env_ok else '❌'}")
    print(f"Импорт telegram: {'✅' if import_ok else '❌'}")
    print(f"Импорт TelegramSender: {'✅' if sender_import_ok else '❌'}")
    print(f"Инициализация TelegramSender: {'✅' if init_ok else '❌'}")
    print(f"Глобальный отправитель: {'✅' if global_ok else '❌'}")
    
    if all([env_ok, import_ok, sender_import_ok, init_ok, global_ok]):
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("   Telegram Bot должен работать корректно")
    else:
        print("\n💥 ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        suggest_solutions()
    
    print("=" * 60)

if __name__ == "__main__":
    main()
