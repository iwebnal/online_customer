# Telegram Mini App

Этот Telegram Mini App получает данные о товарах и ресторанах из базы данных админ-панели.

## Запуск

### 1. Запуск админ-панели

```bash
cd /Users/ahatuhov/Documents/python-projects/temp_project_all_scripts/online_customer/admin_service
python -m admin.main
```

Админ-панель будет доступна по адресу: http://localhost:8000

### 2. Запуск Mini App сервера

```bash
cd /Users/ahatuhov/Documents/python-projects/temp_project_all_scripts/online_customer/public
python server.py
```

Mini App будет доступен по адресу: http://localhost:3000

## API эндпоинты

Mini App использует следующие API эндпоинты админ-панели:

- `GET /api/restaurants` - Получить список ресторанов
- `GET /api/products` - Получить список товаров
- `GET /api/categories` - Получить список категорий
- `POST /api/orders` - Создать новый заказ

## Функции

- ✅ Загрузка данных о ресторанах из базы данных
- ✅ Загрузка меню товаров из базы данных
- ✅ Отображение фотографий товаров
- ✅ Фильтрация по категориям
- ✅ Корзина заказов
- ✅ Создание заказов через API
- ✅ Поддержка Telegram WebApp API
- ✅ Адаптивный дизайн

## Настройка

Для изменения URL админ-панели отредактируйте переменные в файле `app.js`:

```javascript
var apiUrl = 'http://localhost:8000/api/products';
var apiUrl = 'http://localhost:8000/api/restaurants';
var apiUrl = 'http://localhost:8000/api/orders';
```

## Структура файлов

- `index.html` - Основная HTML страница
- `app.js` - JavaScript логика приложения
- `styles.css` - Стили приложения
- `server.py` - Простой веб-сервер для разработки
- `menu.json` - Fallback данные для меню
