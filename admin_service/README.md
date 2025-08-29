# Админ панель Online Customer

Веб-интерфейс для управления ресторанами, продуктами, заказами и скидками.

## Возможности

- 🔐 Аутентификация администратора
- 🏪 Управление ресторанами
- 🍕 Управление продуктами и категориями
- 📦 Управление заказами
- 🎯 Управление скидками
- 📊 Статистика и аналитика

## Быстрый старт

### Локальное развертывание

1. Установите зависимости:
```bash
pip install -r requirements/requirements.txt
```

2. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл
```

3. Запустите миграции:
```bash
cd shared
alembic upgrade head
cd ..
```

4. Запустите сервер:
```bash
python -m uvicorn admin.main:app --host 0.0.0.0 --port 8000
```

### Docker развертывание

```bash
./scripts/docker-deploy.sh
```

## API Endpoints

- `GET /` - Главная страница админ панели
- `GET /admin/login` - Страница входа
- `POST /admin/login` - Аутентификация
- `GET /admin/logout` - Выход из системы

### Управление продуктами
- `GET /admin/products` - Список продуктов
- `POST /admin/products` - Создание продукта
- `PUT /admin/products/{id}` - Обновление продукта
- `DELETE /admin/products/{id}` - Удаление продукта

### Управление заказами
- `GET /admin/orders` - Список заказов
- `GET /admin/orders/{id}` - Детали заказа
- `PUT /admin/orders/{id}/status` - Изменение статуса заказа

## Структура проекта

```
admin_service/
├── admin/                 # Основной код приложения
│   ├── main.py           # Точка входа FastAPI
│   ├── auth.py           # Аутентификация
│   ├── database.py       # Подключение к БД (deprecated)
│   └── routes/           # API маршруты
│       ├── products.py   # Управление продуктами
│       ├── orders.py     # Управление заказами
│       ├── discounts.py  # Управление скидками
│       └── restaurants.py # Управление ресторанами
├── shared/               # Общие компоненты
│   ├── models/          # Модели базы данных
│   ├── database/        # Подключение к БД
│   └── config/          # Конфигурация
├── requirements/         # Зависимости Python
├── scripts/             # Скрипты развертывания
└── docker/              # Docker конфигурация
```

## Переменные окружения

```env
# База данных
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/online_customer

# Аутентификация
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=your-super-secret-key-change-this-in-production

# Сервер
HOST=0.0.0.0
ADMIN_PORT=8000
```

## Разработка

### Добавление новых маршрутов

1. Создайте новый файл в `admin/routes/`
2. Импортируйте роутер в `admin/main.py`
3. Добавьте роутер в приложение

### Добавление новых моделей

1. Добавьте модель в `shared/models/models.py`
2. Создайте миграцию:
```bash
cd shared
alembic revision --autogenerate -m "Add new model"
alembic upgrade head
```

## Мониторинг

### Логи
```bash
# Docker
docker-compose logs -f admin

# Локально
tail -f logs/admin.log
```

### Метрики
- Доступность: `GET /health`
- Статистика: `GET /admin/stats`
