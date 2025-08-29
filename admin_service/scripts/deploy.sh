#!/bin/bash

# Скрипт развертывания админ панели

set -e

echo "🚀 Развертывание админ панели..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Скопируйте .env.example в .env и настройте переменные."
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

# Запускаем приложение
echo "🎯 Запуск админ панели..."
python -m uvicorn admin.main:app --host 0.0.0.0 --port 8000

echo "✅ Админ панель запущена на http://localhost:8000"
