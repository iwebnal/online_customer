# Telegram Mini App с интеграцией админ-панели

Этот проект представляет собой Telegram Mini App, который получает данные о товарах и ресторанах из базы данных админ-панели.

## 🏗️ Архитектура

```
┌─────────────────┐    API     ┌──────────────────┐
│   Telegram      │ ────────── │   Админ-панель   │
│   Mini App      │            │   (FastAPI)      │
│   (Frontend)    │            │   Port: 8000     │
└─────────────────┘            └──────────────────┘
        │                                │
        │ HTTP Requests                  │ Database
        │ - GET /api/products            │ Connection
        │ - GET /api/restaurants         │
        │ - POST /api/orders             │
        │                                │
        │                       ┌──────────────────┐
        │                       │   PostgreSQL     │
        │                       │   Database       │
        │                       └──────────────────┘
```

## 🚀 Быстрый запуск

### 1. Установка зависимостей

```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Или только для админ-панели
pip install -r admin_service/requirements.txt

# Для разработки (включает тестирование, линтинг)
pip install -r requirements-dev.txt
```

### 2. Запуск всей системы одной командой

```bash
python start_all.py
```

### 3. Или запуск по отдельности

**Админ-панель:**
```bash
cd admin_service
python -m admin.main
```

**Mini App сервер:**
```bash
cd public
python server.py
```

## 📱 Доступ к приложению

- **Админ-панель**: http://localhost:8000
- **Mini App**: http://localhost:3000

## 🧪 Тестирование

```bash
python test_api.py
```

## 📋 Функции

### ✅ Реализовано

- **Интеграция с базой данных**: Mini App получает данные из PostgreSQL через API админ-панели
- **Управление ресторанами**: Отображение списка ресторанов с адресами
- **Управление товарами**: Получение меню товаров с фотографиями, ценами и описаниями
- **Категории товаров**: Фильтрация по категориям
- **Корзина заказов**: Добавление/удаление товаров
- **Создание заказов**: Отправка заказов в базу данных через API
- **Telegram WebApp API**: Поддержка нативных функций Telegram
- **Адаптивный дизайн**: Работает на мобильных устройствах
- **CORS поддержка**: Настроена для работы с внешними доменами

### 🔧 API эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/restaurants` | Получить список ресторанов |
| GET | `/api/products` | Получить список товаров |
| GET | `/api/categories` | Получить список категорий |
| POST | `/api/orders` | Создать новый заказ |

## 📁 Структура проекта

```
online_customer/
├── admin_service/           # Админ-панель
│   ├── admin/
│   │   ├── main.py         # Главный файл FastAPI
│   │   ├── routes/         # Роуты для управления
│   │   ├── templates/      # HTML шаблоны
│   │   └── static/         # CSS/JS для админки
│   └── shared/             # Общие модели и настройки
├── public/                 # Telegram Mini App
│   ├── index.html         # Основная страница
│   ├── app.js            # JavaScript логика
│   ├── styles.css        # Стили приложения
│   ├── server.py         # Веб-сервер для разработки
│   └── menu.json         # Fallback данные
├── shared/                # Общие компоненты
│   ├── models.py         # Модели базы данных
│   ├── database.py       # Подключение к БД
│   └── config.py         # Настройки
├── alembic/              # Миграции базы данных
├── start_all.py          # Скрипт запуска всей системы
├── test_api.py           # Тестирование API
└── README.md             # Документация
```

## 🔧 Настройка

### Изменение URL админ-панели

В файле `public/app.js` найдите и измените:

```javascript
var apiUrl = 'http://localhost:8000/api/products';
var apiUrl = 'http://localhost:8000/api/restaurants';
var apiUrl = 'http://localhost:8000/api/orders';
```

### Настройка базы данных

1. Создайте файл `.env` на основе `env.example`
2. Настройте подключение к PostgreSQL
3. Запустите миграции:

```bash
alembic upgrade head
```

### Добавление тестовых данных

```bash
python shared/seed.py
```

## 🌐 Развертывание

### Для продакшена

1. Измените URL в `app.js` на продакшн адрес
2. Настройте CORS в админ-панели для конкретных доменов
3. Используйте nginx или другой веб-сервер для статических файлов
4. Настройте SSL сертификаты

### Docker

```bash
# Админ-панель
cd admin_service/docker
docker-compose up -d

# Mini App (nginx)
docker run -d -p 80:80 -v $(pwd)/public:/usr/share/nginx/html nginx
```

## 🤝 Разработка

### Добавление новых API эндпоинтов

1. Добавьте роут в `admin_service/admin/main.py`
2. Обновите frontend в `public/app.js`
3. Протестируйте с помощью `test_api.py`

### Добавление новых полей в модели

1. Обновите модели в `shared/models.py`
2. Создайте миграцию: `alembic revision --autogenerate -m "description"`
3. Примените миграцию: `alembic upgrade head`
4. Обновите API эндпоинты и frontend

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи админ-панели
2. Убедитесь, что база данных доступна
3. Проверьте настройки CORS
4. Используйте `test_api.py` для диагностики API

## 📄 Лицензия

MIT License
