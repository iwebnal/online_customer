#!/bin/bash

# Скрипт для развертывания исправлений Telegram Bot на сервере
# Использование: ./deploy_telegram_fix.sh

set -e  # Останавливаем выполнение при ошибке

echo "🚀 Развертывание исправлений Telegram Bot на сервере"
echo "=================================================="

# Проверяем, что мы на сервере
if [ ! -f "/etc/hostname" ]; then
    echo "❌ Этот скрипт должен запускаться на сервере"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с переменными:"
    echo "TELEGRAM_BOT_TOKEN=your-bot-token-here"
    echo "TELEGRAM_CHAT_ID=-1003068821769"
    exit 1
fi

echo "✅ Файл .env найден"

# Проверяем переменные окружения
if ! grep -q "TELEGRAM_BOT_TOKEN" .env; then
    echo "❌ TELEGRAM_BOT_TOKEN не найден в .env"
    exit 1
fi

if ! grep -q "TELEGRAM_CHAT_ID" .env; then
    echo "❌ TELEGRAM_CHAT_ID не найден в .env"
    exit 1
fi

echo "✅ Переменные окружения найдены в .env"

# Останавливаем контейнеры если они запущены
echo "🛑 Останавливаем контейнеры..."
if command -v docker-compose &> /dev/null; then
    docker-compose down || true
    docker-compose -f docker-compose.prod.yml down || true
    docker-compose -f docker-compose.ip.yml down || true
fi

# Проверяем, установлена ли библиотека python-telegram-bot
echo "🔍 Проверяем установку python-telegram-bot..."
if python3 -c "import telegram; print(f'✅ python-telegram-bot {telegram.__version__} установлена')" 2>/dev/null; then
    echo "✅ Библиотека установлена"
else
    echo "📦 Устанавливаем python-telegram-bot..."
    pip3 install python-telegram-bot>=20.0
fi

# Запускаем диагностику
echo "🔍 Запускаем диагностику..."
if [ -f "telegram_server_diagnostic.py" ]; then
    python3 telegram_server_diagnostic.py
else
    echo "⚠️ Файл telegram_server_diagnostic.py не найден, пропускаем диагностику"
fi

# Пересобираем Docker образ если используется Docker
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.prod.yml" ]; then
    echo "🔨 Пересобираем Docker образ..."
    
    # Определяем какой docker-compose файл использовать
    COMPOSE_FILE=""
    if [ -f "docker-compose.prod.yml" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
    elif [ -f "docker-compose.ip.yml" ]; then
        COMPOSE_FILE="docker-compose.ip.yml"
    elif [ -f "docker-compose.yml" ]; then
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    if [ -n "$COMPOSE_FILE" ]; then
        echo "Используем файл: $COMPOSE_FILE"
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        echo "🚀 Запускаем контейнеры..."
        docker-compose -f "$COMPOSE_FILE" up -d
    fi
else
    echo "ℹ️ Docker не используется, перезапускаем приложение напрямую"
    
    # Останавливаем существующие процессы
    pkill -f "python.*admin.*main" || true
    
    # Запускаем приложение
    echo "🚀 Запускаем приложение..."
    nohup python3 admin_service/admin/main.py > app.log 2>&1 &
    echo "✅ Приложение запущено в фоне"
fi

# Ждем запуска
echo "⏳ Ждем запуска приложения..."
sleep 10

# Проверяем статус
echo "🔍 Проверяем статус приложения..."

if command -v docker-compose &> /dev/null && [ -n "$COMPOSE_FILE" ]; then
    echo "Проверяем логи Docker контейнера..."
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 admin
else
    echo "Проверяем логи приложения..."
    tail -20 app.log 2>/dev/null || echo "Логи не найдены"
fi

# Финальная проверка Telegram
echo "🧪 Выполняем финальную проверку Telegram..."
python3 -c "
import asyncio
import sys
import os
sys.path.append('.')

async def test():
    try:
        from shared.telegram.sender import get_telegram_sender
        sender = get_telegram_sender()
        
        if sender.is_initialized():
            print('✅ Telegram Bot инициализирован успешно')
            result = await sender.send_test_message()
            if result:
                print('✅ Тестовое сообщение отправлено успешно')
                print('🎉 Telegram Bot работает корректно!')
            else:
                print('❌ Не удалось отправить тестовое сообщение')
        else:
            error = sender.get_initialization_error()
            print(f'❌ Telegram Bot не инициализирован: {error}')
    except Exception as e:
        print(f'❌ Ошибка проверки: {e}')

asyncio.run(test())
"

echo ""
echo "=================================================="
echo "✅ Развертывание завершено!"
echo ""
echo "📋 Что было сделано:"
echo "   • Проверены переменные окружения"
echo "   • Установлена/проверена библиотека python-telegram-bot"
echo "   • Выполнена диагностика системы"
echo "   • Пересобран Docker образ (если используется)"
echo "   • Перезапущено приложение"
echo "   • Выполнена финальная проверка Telegram"
echo ""
echo "📝 Для мониторинга используйте:"
if command -v docker-compose &> /dev/null && [ -n "$COMPOSE_FILE" ]; then
    echo "   docker-compose -f $COMPOSE_FILE logs -f admin"
else
    echo "   tail -f app.log"
fi
echo ""
echo "🔧 Для диагностики проблем используйте:"
echo "   python3 telegram_server_diagnostic.py"
echo ""
