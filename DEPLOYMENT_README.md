# Развертывание Online Customer

Проект разделен на два независимых сервиса, которые можно развертывать отдельно или вместе.

## Структура проекта

```
online_customer/
├── admin_service/          # Админ панель
│   ├── admin/             # Код админ панели
│   ├── shared/            # Общие компоненты
│   ├── requirements/      # Зависимости
│   ├── scripts/           # Скрипты развертывания
│   └── docker/            # Docker конфигурация
├── bot_service/           # Telegram бот
│   ├── bot/              # Код бота
│   ├── shared/           # Общие компоненты
│   ├── requirements/     # Зависимости
│   ├── scripts/          # Скрипты развертывания
│   └── docker/           # Docker конфигурация
├── shared/               # Общие компоненты (модели, БД)
└── scripts/              # Общие скрипты
```

## Требования

- Python 3.11+
- PostgreSQL 15+
- Docker и Docker Compose (для контейнерного развертывания)

## Настройка окружения

1. Скопируйте файл конфигурации:
```bash
cp env.example .env
```

2. Настройте переменные в `.env`:
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

## Варианты развертывания

### 1. Развертывание всего проекта (рекомендуется)

```bash
# Запуск всех сервисов
./scripts/deploy-all.sh
```

### 2. Развертывание только админ панели

#### Локальное развертывание:
```bash
cd admin_service
cp .env.example .env
# Настройте .env файл
./scripts/deploy.sh
```

#### Docker развертывание:
```bash
cd admin_service
cp .env.example .env
# Настройте .env файл
./scripts/docker-deploy.sh
```

### 3. Развертывание только бота

#### Локальное развертывание:
```bash
cd bot_service
cp .env.example .env
# Настройте .env файл
./scripts/deploy.sh
```

#### Docker развертывание:
```bash
cd bot_service
cp .env.example .env
# Настройте .env файл
./scripts/docker-deploy.sh
```

## Развертывание на виртуальном сервере

### Подготовка сервера

1. Установите Docker и Docker Compose:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

2. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd online_customer
```

3. Настройте переменные окружения:
```bash
cp env.example .env
nano .env  # Настройте переменные
```

### Развертывание

#### Вариант 1: Все сервисы на одном сервере
```bash
./scripts/deploy-all.sh
```

#### Вариант 2: Разные серверы для каждого сервиса

**Сервер 1 - Админ панель:**
```bash
# Скопируйте только admin_service на сервер
scp -r admin_service/ user@server1:/opt/online_customer/
scp -r shared/ user@server1:/opt/online_customer/admin_service/

# На сервере
cd /opt/online_customer/admin_service
cp .env.example .env
# Настройте .env (укажите внешний адрес БД)
./scripts/docker-deploy.sh
```

**Сервер 2 - Telegram бот:**
```bash
# Скопируйте только bot_service на сервер
scp -r bot_service/ user@server2:/opt/online_customer/
scp -r shared/ user@server2:/opt/online_customer/bot_service/

# На сервере
cd /opt/online_customer/bot_service
cp .env.example .env
# Настройте .env (укажите внешний адрес БД)
./scripts/docker-deploy.sh
```

**Сервер 3 - База данных (опционально):**
```bash
# Запустите только PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_DB=online_customer \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15
```

## Мониторинг и управление

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f admin
docker-compose logs -f bot
docker-compose logs -f db
```

### Остановка сервисов
```bash
# Остановить все
docker-compose down

# Остановить конкретный сервис
docker-compose stop admin
docker-compose stop bot
```

### Обновление сервисов
```bash
# Пересобрать и перезапустить
docker-compose up --build -d

# Обновить конкретный сервис
docker-compose up --build -d admin
```

## Безопасность

1. **Измените пароли по умолчанию** в `.env` файле
2. **Используйте HTTPS** для админ панели (настройте nginx/apache)
3. **Ограничьте доступ к базе данных** (настройте firewall)
4. **Регулярно обновляйте** зависимости и образы Docker

## Устранение неполадок

### Проблемы с базой данных
```bash
# Проверьте статус
docker-compose ps

# Перезапустите базу данных
docker-compose restart db

# Проверьте логи
docker-compose logs db
```

### Проблемы с миграциями
```bash
# Запустите миграции вручную
docker-compose exec admin alembic upgrade head
```

### Проблемы с ботом
```bash
# Проверьте токен бота
docker-compose exec bot env | grep BOT_TOKEN

# Перезапустите бота
docker-compose restart bot
```

## Полезные команды

```bash
# Войти в контейнер
docker-compose exec admin bash
docker-compose exec bot bash

# Выполнить команду в контейнере
docker-compose exec admin python -c "print('Hello')"

# Просмотр использования ресурсов
docker stats

# Очистка неиспользуемых образов
docker system prune -a
```
