# Быстрый старт

## 🚀 Запуск бота на выделенном сервере

### 1. Подготовка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd online_customer

# Перейдите в папку бота
cd bot_service
```

### 2. Настройка токена

```bash
# Отредактируйте .env файл
nano .env

# Замените строку:
# BOT_TOKEN=your-bot-token-here
# На:
# BOT_TOKEN=ваш-реальный-токен-от-botfather
```

**Как получить токен:** см. [BOT_SETUP.md](BOT_SETUP.md)

### 3. Проверка конфигурации

```bash
python3 test_config.py
```

Должно показать: `✅ Конфигурация бота настроена правильно!`

### 4. Запуск

#### Вариант A: Локальный запуск
```bash
./scripts/deploy.sh
```

#### Вариант B: Docker запуск
```bash
./scripts/docker-deploy.sh
```

### 5. Проверка

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Бот должен ответить

## 🛠️ Устранение неполадок

### Ошибка "BOT_TOKEN is not set"
```bash
# Проверьте .env файл
cat .env | grep BOT_TOKEN

# Должно показать:
# BOT_TOKEN=ваш-реальный-токен
```

### Бот не отвечает
```bash
# Проверьте логи
docker-compose logs bot

# Или для локального запуска
tail -f logs/bot.log
```

### Проблемы с базой данных
```bash
# Убедитесь, что PostgreSQL запущен
docker-compose ps

# Проверьте подключение
docker-compose exec bot python -c "from shared.database import get_db_session; print('DB OK')"
```

## 📞 Поддержка

- **Документация:** [README.md](README.md)
- **Настройка бота:** [BOT_SETUP.md](BOT_SETUP.md)
- **Развертывание:** [DEPLOYMENT_README.md](DEPLOYMENT_README.md)
