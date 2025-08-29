# Online Customer - Система заказа еды

Проект разделен на два независимых сервиса для удобного развертывания на виртуальных серверах.

## 🏗️ Архитектура

```
online_customer/
├── admin_service/          # 🌐 Админ панель (FastAPI)
├── bot_service/           # 🤖 Telegram бот (aiogram)
├── shared/                # 📦 Общие компоненты
├── scripts/               # 🚀 Скрипты развертывания
└── docker-compose.yml     # 🐳 Общая конфигурация
```

## 🚀 Быстрый старт

### Развертывание всего проекта
```bash
# 1. Клонируйте репозиторий
git clone <your-repo-url>
cd online_customer

# 2. Настройте окружение
cp env.example .env
# Отредактируйте .env файл

# 3. Запустите все сервисы
./scripts/deploy-all.sh
```

### Развертывание отдельных сервисов

#### Только админ панель
```bash
cd admin_service
cp .env.example .env
./scripts/docker-deploy.sh
```

#### Только Telegram бот
```bash
cd bot_service
cp .env.example .env
./scripts/docker-deploy.sh
```

## 📋 Требования

- **Python 3.11+**
- **PostgreSQL 15+**
- **Docker & Docker Compose** (для контейнерного развертывания)

## 🔧 Настройка

### Переменные окружения

Создайте `.env` файл на основе `env.example`:

```env
# База данных
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/online_customer

# Админ панель
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=your-super-secret-key-change-this-in-production

# Telegram бот
BOT_TOKEN=your-bot-token-here
```

### Получение токена бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в `.env` файл

**Подробные инструкции:** см. [BOT_SETUP.md](BOT_SETUP.md)

## 🌐 Доступ к сервисам

После развертывания:

- **Админ панель**: http://localhost:8000
- **Telegram бот**: Найдите вашего бота в Telegram
- **База данных**: localhost:5432

## 📚 Документация

- [📖 Руководство по развертыванию](DEPLOYMENT_README.md)
- [🔄 Руководство по миграции](MIGRATION_GUIDE.md)
- [🌐 Админ панель](admin_service/README.md)
- [🤖 Telegram бот](bot_service/README.md)

## 🛠️ Разработка

### Локальная разработка

```bash
# Админ панель
cd admin_service
python -m venv venv
source venv/bin/activate
pip install -r requirements/requirements.txt
python -m uvicorn admin.main:app --reload

# Бот
cd bot_service
python -m venv venv
source venv/bin/activate
pip install -r requirements/requirements.txt
python bot/main.py
```

### Добавление новых функций

1. **Модели БД**: Добавьте в `shared/models/models.py`
2. **API endpoints**: Добавьте в `admin_service/admin/routes/`
3. **Команды бота**: Добавьте в `bot_service/bot/handlers/`

## 🐳 Docker

### Основные команды

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Пересборка
docker-compose up --build -d
```

### Мониторинг

```bash
# Статус сервисов
docker-compose ps

# Использование ресурсов
docker stats

# Логи конкретного сервиса
docker-compose logs -f admin
docker-compose logs -f bot
```

## 🔒 Безопасность

1. **Измените пароли по умолчанию** в `.env`
2. **Используйте HTTPS** для админ панели
3. **Ограничьте доступ к БД** через firewall
4. **Регулярно обновляйте** зависимости

## 🆘 Поддержка

### Частые проблемы

**Бот не отвечает:**
- Проверьте токен в `.env`
- Убедитесь, что бот запущен
- Проверьте логи: `docker-compose logs bot`

**Админ панель недоступна:**
- Проверьте порт 8000
- Убедитесь, что БД запущена
- Проверьте логи: `docker-compose logs admin`

**Проблемы с БД:**
- Проверьте подключение
- Запустите миграции: `alembic upgrade head`
- Проверьте логи: `docker-compose logs db`

### Получение помощи

1. Проверьте документацию в папках сервисов
2. Изучите логи сервисов
3. Проверьте конфигурацию `.env`
4. Создайте issue в репозитории

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Запуск нескольких экземпляров админ панели
docker-compose up --scale admin=3 -d

# Запуск нескольких экземпляров бота
docker-compose up --scale bot=2 -d
```

### Развертывание на разных серверах

См. [DEPLOYMENT_README.md](DEPLOYMENT_README.md) для подробных инструкций.

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

---

**Готово к развертыванию! 🚀**
