#!/bin/bash

# Скрипт развертывания всего проекта

set -e

echo "🚀 Развертывание всего проекта Online Customer..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Скопируйте env.example в .env и настройте переменные."
    exit 1
fi

# Загружаем переменные из .env файла
export $(cat .env | grep -v '^#' | xargs)

# Проверяем наличие BOT_TOKEN
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your-bot-token-here" ]; then
    echo "❌ BOT_TOKEN не установлен в .env файле. Замените 'your-bot-token-here' на реальный токен."
    exit 1
fi

# Останавливаем существующие контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Собираем и запускаем все сервисы
echo "🔨 Сборка и запуск всех сервисов..."
docker-compose up --build -d

# Ждем запуска базы данных
echo "⏳ Ожидание запуска базы данных..."
sleep 15

# Запускаем миграции
echo "🗄️ Запуск миграций базы данных..."
docker-compose exec admin alembic upgrade head

echo "✅ Проект успешно развернут!"
echo ""
echo "🌐 Админ панель: http://localhost:8000"
echo "🤖 Telegram бот: запущен"
echo "📊 База данных: localhost:5432"
echo ""
echo "📋 Полезные команды:"
echo "  docker-compose logs -f admin    # Логи админ панели"
echo "  docker-compose logs -f bot      # Логи бота"
echo "  docker-compose logs -f db       # Логи базы данных"
echo "  docker-compose down             # Остановить все сервисы"
