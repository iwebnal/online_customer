#!/bin/bash

# Скрипт развертывания бота через Docker

set -e

echo "🐳 Развертывание Telegram бота через Docker..."

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

# Переходим в папку с Docker конфигурацией
cd docker

# Останавливаем и удаляем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Собираем и запускаем контейнеры
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up --build -d

# Ждем запуска базы данных
echo "⏳ Ожидание запуска базы данных..."
sleep 10

# Запускаем миграции
echo "🗄️ Запуск миграций базы данных..."
docker-compose exec bot alembic upgrade head

echo "✅ Telegram бот развернут и запущен"
echo "📊 База данных доступна на localhost:5432"
