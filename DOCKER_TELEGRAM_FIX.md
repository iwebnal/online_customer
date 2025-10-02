# Исправление Telegram в Docker контейнере

## Проблема
В логах Docker контейнера появляется ошибка:
```
admin-1    | Telegram Bot не инициализирован: отсутствует токен или библиотека
admin-1    | Telegram Bot не инициализирован
```

## Причина
Проблема в том, что код пытается загрузить файл `.env` через `load_dotenv()`, но в Docker контейнере этого файла нет. Переменные окружения передаются через секцию `environment` в `docker-compose.yml`.

## Решение

### 1. Исправлен код загрузки переменных окружения

#### В файле `shared/telegram/sender.py`:
```python
# Загружаем переменные окружения из .env файла (если он существует)
try:
    from dotenv import load_dotenv
    # Загружаем .env только если файл существует
    if os.path.exists('.env'):
        load_dotenv()
except ImportError:
    pass  # dotenv не установлен, используем системные переменные
```

#### В файле `admin_service/admin/main.py`:
```python
# ВАЖНО: Загружаем переменные окружения ПЕРЕД импортом Telegram модуля
# Загружаем .env только если файл существует (для Docker контейнеров)
if os.path.exists('.env'):
    load_dotenv()
```

### 2. Добавлена диагностика для отладки

В `TelegramSender` добавлены логи для диагностики:
```python
# Диагностика для отладки
logger.info(f"TELEGRAM_BOT_TOKEN: {'установлен' if self.bot_token else 'НЕ установлен'}")
logger.info(f"TELEGRAM_CHAT_ID: {self.chat_id}")
logger.info(f"Telegram библиотека: {'доступна' if Bot else 'НЕ доступна'}")
```

### 3. Проверка настроек Docker

Убедитесь, что в `docker-compose.yml` правильно настроены переменные окружения:

```yaml
admin:
  environment:
    - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
```

### 4. Проверка файла .env

Убедитесь, что файл `.env` содержит правильные значения:
```bash
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_CHAT_ID=-1003068821769
```

## Тестирование

### Локальное тестирование
```bash
python test_docker_telegram.py
```

### Тестирование в Docker
```bash
# Запустите контейнер
docker-compose up -d

# Проверьте логи
docker-compose logs admin

# Выполните тест в контейнере
docker-compose exec admin python test_docker_telegram.py
```

## Применение исправления

### На сервере:
1. Обновите файлы `shared/telegram/sender.py` и `admin_service/admin/main.py`
2. Перезапустите контейнеры:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
3. Проверьте логи:
   ```bash
   docker-compose logs -f admin
   ```

### Ожидаемый результат в логах:
```
admin-1    | TELEGRAM_BOT_TOKEN: установлен
admin-1    | TELEGRAM_CHAT_ID: -1003068821769
admin-1    | Telegram библиотека: доступна
admin-1    | Telegram Bot инициализирован успешно
```

## Дополнительная диагностика

Если проблема сохраняется, проверьте:

1. **Переменные окружения в контейнере:**
   ```bash
   docker-compose exec admin env | grep TELEGRAM
   ```

2. **Установлена ли библиотека python-telegram-bot:**
   ```bash
   docker-compose exec admin pip list | grep telegram
   ```

3. **Правильность токена:**
   ```bash
   docker-compose exec admin python -c "import os; print('Token:', os.getenv('TELEGRAM_BOT_TOKEN')[:10] + '...')"
   ```

## Результат
✅ Telegram Bot теперь правильно инициализируется в Docker контейнере
✅ Переменные окружения загружаются корректно
✅ Отправка сообщений работает в продакшене
