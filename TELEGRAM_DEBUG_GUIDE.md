# Диагностика проблем с Telegram Bot на сервере

## Проблема
Ошибка: "Telegram Bot не инициализирован: отсутствует токен или библиотека"

## Быстрая диагностика

### 1. Подключитесь к серверу
```bash
ssh root@45.141.76.16
```

### 2. Перейдите в директорию проекта
```bash
cd /root/online_customer
```

### 3. Запустите быструю проверку
```bash
python3 quick_telegram_check.py
```

### 4. Если нужна полная диагностика
```bash
python3 telegram_debug.py
```

## Возможные причины и решения

### 1. Библиотека не установлена
**Симптомы:** `ImportError: No module named 'telegram'`

**Решение:**
```bash
pip install python-telegram-bot>=20.0
# или
pip install -r requirements.txt
```

### 2. Отсутствует токен бота
**Симптомы:** `TELEGRAM_BOT_TOKEN не установлен`

**Решение:**
1. Получите токен от @BotFather в Telegram
2. Добавьте в файл `.env`:
```bash
echo "TELEGRAM_BOT_TOKEN=your-bot-token-here" >> .env
```

### 3. Неправильный токен
**Симптомы:** `Ошибка инициализации Telegram бота`

**Решение:**
1. Проверьте токен в @BotFather
2. Убедитесь, что токен скопирован полностью
3. Проверьте, что бот не заблокирован

### 4. Проблемы с правами доступа
**Симптомы:** `Permission denied` при чтении .env

**Решение:**
```bash
chmod 644 .env
chown root:root .env
```

## Проверка логов

### 1. Проверьте логи приложения
```bash
# Если используется systemd
journalctl -u your-app-service -f

# Если используется docker
docker logs your-container-name

# Если запускается напрямую
tail -f /var/log/your-app.log
```

### 2. Проверьте логи Python
```bash
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from shared.telegram.sender import TelegramSender
sender = TelegramSender()
print('Bot initialized:', sender.bot is not None)
"
```

## Тестирование

### 1. Тест импорта
```bash
python3 -c "import telegram; print('OK')"
```

### 2. Тест токена
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
print('Token found:', bool(token))
print('Token length:', len(token) if token else 0)
"
```

### 3. Полный тест
```bash
python3 test_telegram.py
```

## Восстановление

### 1. Переустановка зависимостей
```bash
pip uninstall python-telegram-bot
pip install python-telegram-bot>=20.0
```

### 2. Очистка кэша Python
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 3. Перезапуск приложения
```bash
# Если используется systemd
systemctl restart your-app-service

# Если используется docker
docker-compose restart

# Если запускается напрямую
pkill -f python
nohup python3 your-app.py &
```

## Полезные команды

### Проверка установленных пакетов
```bash
pip list | grep telegram
```

### Проверка переменных окружения
```bash
env | grep TELEGRAM
```

### Проверка файла .env
```bash
cat .env | grep TELEGRAM
```

### Проверка версии Python
```bash
python3 --version
```

## Контакты для поддержки

Если проблемы не решаются:
1. Проверьте документацию: https://python-telegram-bot.readthedocs.io/
2. Создайте issue в репозитории проекта
3. Обратитесь к администратору сервера
