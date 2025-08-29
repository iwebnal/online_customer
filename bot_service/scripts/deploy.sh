#!/bin/bash

# Скрипт развертывания бота

set -e

echo "🤖 Развертывание Telegram бота..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Скопируйте .env.example в .env и настройте переменные."
    exit 1
fi

# Загружаем переменные из .env файла
export $(cat .env | grep -v '^#' | xargs)

# Проверяем наличие BOT_TOKEN
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your-bot-token-here" ]; then
    echo "❌ BOT_TOKEN не установлен в .env файле. Замените 'your-bot-token-here' на реальный токен."
    exit 1
fi

# Создаем виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Установка зависимостей..."
pip install -r requirements/requirements.txt

# Запускаем миграции базы данных
echo "🗄️ Запуск миграций базы данных..."
cd shared
alembic upgrade head
cd ..

# Запускаем бота
echo "🎯 Запуск Telegram бота..."
python bot/main.py

echo "✅ Telegram бот запущен"
