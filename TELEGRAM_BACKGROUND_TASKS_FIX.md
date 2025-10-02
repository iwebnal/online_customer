# Исправление отправки сообщений в Telegram через BackgroundTasks

## Проблема
После нажатия на кнопку "Отправить" сообщения в группу не приходили, хотя все тестовые скрипты работали корректно.

## Причина проблемы
В коде использовался `asyncio.create_task()` для отправки уведомлений в Telegram, но это не работает корректно в контексте FastAPI, особенно когда задача создается после отправки ответа клиенту.

## Решение
Заменили `asyncio.create_task()` на правильное использование FastAPI BackgroundTasks.

### Изменения в коде

#### 1. Добавлен импорт BackgroundTasks
```python
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, BackgroundTasks
```

#### 2. Изменена сигнатура функции создания заказа
```python
@app.post("/api/orders")
async def create_order_api(order_data: dict, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
```

#### 3. Добавлена синхронная функция-обертка
```python
def send_telegram_notification_sync(telegram_data: dict):
    """Синхронная обертка для отправки уведомления в Telegram"""
    try:
        # Создаем новый event loop для фоновой задачи
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(send_order_to_telegram(telegram_data))
        finally:
            loop.close()
    except Exception as e:
        print(f"Ошибка отправки уведомления в Telegram: {e}")
```

#### 4. Заменен вызов функции
**Было:**
```python
import asyncio
asyncio.create_task(send_order_to_telegram(telegram_data))
```

**Стало:**
```python
background_tasks.add_task(send_telegram_notification_sync, telegram_data)
```

## Преимущества нового подхода

1. **Правильная интеграция с FastAPI**: BackgroundTasks - это стандартный способ FastAPI для выполнения фоновых задач
2. **Надежность**: Задачи выполняются после отправки ответа клиенту
3. **Обработка ошибок**: Лучшая обработка ошибок в фоновых задачах
4. **Производительность**: Не блокирует основной поток выполнения

## Тестирование

Создан тестовый скрипт `test_order_creation.py` для проверки работы исправления:

```bash
python test_order_creation.py
```

## Результат
✅ Отправка сообщений в Telegram группу теперь работает корректно
✅ Тестовые скрипты продолжают работать
✅ Улучшена надежность системы уведомлений

## Применение на сервере

Для применения исправления на сервере:

1. Обновите файл `admin_service/admin/main.py` с новым кодом
2. Перезапустите приложение:
   ```bash
   # Если используется systemd
   systemctl restart your-app-service
   
   # Если используется docker
   docker-compose restart
   ```

3. Проверьте работу:
   ```bash
   python test_order_creation.py
   ```
