#!/bin/bash

# Скрипт для диагностики Telegram Bot на сервере
# Использование: ./server_telegram_check.sh

echo "=========================================="
echo "🔧 ДИАГНОСТИКА TELEGRAM BOT НА СЕРВЕРЕ"
echo "=========================================="

# Проверяем, что мы в правильной директории
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден"
    echo "   Убедитесь, что вы находитесь в директории проекта"
    exit 1
fi

echo "📁 Текущая директория: $(pwd)"
echo ""

# 1. Проверяем Python
echo "🐍 Проверка Python..."
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python3 доступен"
else
    echo "❌ Python3 недоступен"
    exit 1
fi
echo ""

# 2. Проверяем pip
echo "📦 Проверка pip..."
pip3 --version
if [ $? -eq 0 ]; then
    echo "✅ pip3 доступен"
else
    echo "❌ pip3 недоступен"
    exit 1
fi
echo ""

# 3. Проверяем установленные пакеты
echo "📋 Проверка установленных пакетов..."
echo "Пакеты, связанные с telegram:"
pip3 list | grep -i telegram
echo ""

# 4. Проверяем файл .env
echo "🔐 Проверка файла .env..."
if [ -f ".env" ]; then
    echo "✅ Файл .env найден"
    echo "Переменные Telegram:"
    grep -i telegram .env || echo "   Переменные Telegram не найдены"
else
    echo "❌ Файл .env не найден"
    echo "   Создайте файл .env с переменными TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID"
fi
echo ""

# 5. Проверяем переменные окружения
echo "🌍 Проверка переменных окружения..."
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo "✅ TELEGRAM_BOT_TOKEN установлен: ${TELEGRAM_BOT_TOKEN:0:10}..."
else
    echo "❌ TELEGRAM_BOT_TOKEN не установлен"
fi

if [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "✅ TELEGRAM_CHAT_ID установлен: $TELEGRAM_CHAT_ID"
else
    echo "⚠️  TELEGRAM_CHAT_ID не установлен (будет использован по умолчанию)"
fi
echo ""

# 6. Проверяем импорт библиотеки
echo "📚 Проверка импорта библиотеки telegram..."
python3 -c "
try:
    import telegram
    print('✅ Библиотека telegram импортируется успешно')
    print(f'   Версия: {telegram.__version__}')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
    print('   Установите: pip install python-telegram-bot>=20.0')
except Exception as e:
    print(f'❌ Другая ошибка: {e}')
"
echo ""

# 7. Проверяем инициализацию Telegram Bot
echo "🤖 Проверка инициализации Telegram Bot..."
python3 -c "
import os
import sys
sys.path.append('.')

try:
    from shared.telegram.sender import TelegramSender
    sender = TelegramSender()
    
    if sender.bot:
        print('✅ Telegram Bot инициализирован успешно')
    else:
        print('❌ Telegram Bot НЕ инициализирован')
        print('   Причина: отсутствует токен или библиотека')
        
        # Дополнительная диагностика
        if not sender.bot_token:
            print('   - Токен бота отсутствует')
        if not sender.bot:
            print('   - Объект Bot не создан')
            
except ImportError as e:
    print(f'❌ Ошибка импорта модуля: {e}')
except Exception as e:
    print(f'❌ Ошибка инициализации: {e}')
"
echo ""

# 8. Предложения по исправлению
echo "💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:"
echo "=========================================="

# Проверяем, установлена ли библиотека
if ! pip3 list | grep -q "python-telegram-bot"; then
    echo "1. Установите библиотеку python-telegram-bot:"
    echo "   pip install python-telegram-bot>=20.0"
    echo ""
fi

# Проверяем наличие токена
if [ ! -f ".env" ] || ! grep -q "TELEGRAM_BOT_TOKEN" .env; then
    echo "2. Настройте переменные окружения в файле .env:"
    echo "   echo 'TELEGRAM_BOT_TOKEN=your-bot-token-here' >> .env"
    echo "   echo 'TELEGRAM_CHAT_ID=-1003068821769' >> .env"
    echo ""
fi

echo "3. Получите токен бота от @BotFather в Telegram"
echo "4. Получите ID чата от @userinfobot"
echo "5. Перезапустите приложение после настройки"
echo ""

# 9. Запуск полного теста (если возможно)
echo "🧪 Запуск полного теста Telegram..."
if [ -f "test_telegram.py" ]; then
    echo "Запускаем test_telegram.py..."
    python3 test_telegram.py
else
    echo "⚠️  Файл test_telegram.py не найден"
fi

echo ""
echo "=========================================="
echo "🏁 ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "=========================================="
