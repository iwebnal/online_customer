# Исправление ошибки "Telegram Bot не инициализирован" на сервере

## Проблема
На сервере `ssh root@45.141.76.16` отображается ошибка:
> "Telegram Bot не инициализирован: отсутствует токен или библиотека"

## Быстрое решение

### 1. Подключитесь к серверу
```bash
ssh root@45.141.76.16
```

### 2. Перейдите в директорию проекта
```bash
cd /root/online_customer
```

### 3. Запустите диагностику
```bash
# Сделайте скрипт исполняемым
chmod +x server_telegram_check.sh

# Запустите диагностику
./server_telegram_check.sh
```

### 4. Или запустите быструю проверку
```bash
python3 quick_telegram_check.py
```

## Наиболее вероятные причины и решения

### Причина 1: Библиотека не установлена
**Симптомы:** `ImportError: No module named 'telegram'`

**Решение:**
```bash
# Установите библиотеку
pip install python-telegram-bot>=20.0

# Или установите все зависимости
pip install -r requirements.txt
```

### Причина 2: Отсутствует токен бота
**Симптомы:** `TELEGRAM_BOT_TOKEN не установлен`

**Решение:**
```bash
# Создайте файл .env если его нет
touch .env

# Добавьте токен бота
echo "TELEGRAM_BOT_TOKEN=your-bot-token-here" >> .env
echo "TELEGRAM_CHAT_ID=-1003068821769" >> .env
```

### Причина 3: Неправильный токен
**Симптомы:** `Ошибка инициализации Telegram бота`

**Решение:**
1. Получите новый токен от @BotFather в Telegram
2. Убедитесь, что токен скопирован полностью
3. Проверьте, что бот не заблокирован

## Пошаговая диагностика

### Шаг 1: Проверка библиотеки
```bash
python3 -c "import telegram; print('OK, версия:', telegram.__version__)"
```

### Шаг 2: Проверка переменных
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Token:', bool(os.getenv('TELEGRAM_BOT_TOKEN')))
print('Chat ID:', os.getenv('TELEGRAM_CHAT_ID'))
"
```

### Шаг 3: Проверка инициализации
```bash
python3 -c "
from shared.telegram.sender import TelegramSender
sender = TelegramSender()
print('Bot initialized:', sender.bot is not None)
"
```

### Шаг 4: Полный тест
```bash
python3 test_telegram.py
```

## Восстановление после проблем

### Если библиотека повреждена
```bash
pip uninstall python-telegram-bot
pip install python-telegram-bot>=20.0
```

### Если кэш Python поврежден
```bash
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Если нужно перезапустить приложение
```bash
# Если используется systemd
systemctl restart your-app-service

# Если используется docker
docker-compose restart

# Если запускается напрямую
pkill -f python
nohup python3 your-app.py &
```

## Проверка после исправления

После выполнения исправлений запустите:
```bash
python3 quick_telegram_check.py
```

Если все работает, вы увидите:
```
🎉 Telegram Bot работает!
```

## Получение токена бота

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Введите имя для бота
4. Введите username для бота
5. Скопируйте полученный токен

## Получение ID чата

1. Создайте группу в Telegram
2. Добавьте бота в группу как администратора
3. Добавьте @userinfobot в группу
4. Отправьте любое сообщение в группу
5. Скопируйте Chat ID

## Файлы для диагностики

В проекте созданы следующие файлы для диагностики:
- `telegram_debug.py` - полная диагностика
- `quick_telegram_check.py` - быстрая проверка
- `server_telegram_check.sh` - bash скрипт для сервера
- `test_telegram.py` - тест интеграции

## Контакты

Если проблемы не решаются:
1. Проверьте логи приложения
2. Убедитесь, что бот не заблокирован
3. Проверьте интернет-соединение сервера
4. Обратитесь к администратору сервера
