# Руководство по миграции проекта

Этот документ описывает, как перейти от монолитной структуры к разделенной архитектуре.

## Что изменилось

### Структура проекта

**Было:**
```
online_customer/
├── admin/           # Админ панель
├── bot/            # Telegram бот
├── db/             # Модели БД
└── requirements.txt # Общие зависимости
```

**Стало:**
```
online_customer/
├── admin_service/   # Независимый сервис админ панели
├── bot_service/     # Независимый сервис бота
├── shared/          # Общие компоненты
└── scripts/         # Скрипты развертывания
```

### Основные изменения

1. **Разделение зависимостей**: Каждый сервис имеет свой `requirements.txt`
2. **Общие компоненты**: Модели БД и конфигурация вынесены в `shared/`
3. **Docker конфигурация**: Каждый сервис может быть развернут отдельно
4. **Скрипты развертывания**: Автоматизированные скрипты для разных сценариев

## Миграция существующего проекта

### 1. Резервное копирование

```bash
# Создайте резервную копию текущего проекта
cp -r online_customer online_customer_backup

# Создайте резервную копию базы данных
pg_dump online_customer > backup.sql
```

### 2. Обновление кода

Код уже обновлен для работы с новой структурой. Основные изменения:

- Импорты изменены с `db.models` на `shared.models`
- Импорты изменены с `admin.database` на `shared.database`
- Добавлена конфигурация через `shared.config`

### 3. Настройка окружения

```bash
# Скопируйте конфигурацию
cp env.example .env

# Настройте переменные для каждого сервиса
cp .env admin_service/.env
cp .env bot_service/.env
```

### 4. Тестирование

#### Тест админ панели:
```bash
cd admin_service
./scripts/deploy.sh
# Проверьте http://localhost:8000
```

#### Тест бота:
```bash
cd bot_service
./scripts/deploy.sh
# Проверьте работу бота в Telegram
```

## Развертывание на продакшене

### Вариант 1: Все на одном сервере

```bash
# Развертывание всего проекта
./scripts/deploy-all.sh
```

### Вариант 2: Разные серверы

#### Сервер админ панели:
```bash
# Скопируйте только admin_service
scp -r admin_service/ user@admin-server:/opt/
scp -r shared/ user@admin-server:/opt/admin_service/

# На сервере
cd /opt/admin_service
# Настройте .env с внешним адресом БД
./scripts/docker-deploy.sh
```

#### Сервер бота:
```bash
# Скопируйте только bot_service
scp -r bot_service/ user@bot-server:/opt/
scp -r shared/ user@bot-server:/opt/bot_service/

# На сервере
cd /opt/bot_service
# Настройте .env с внешним адресом БД
./scripts/docker-deploy.sh
```

## Откат изменений

Если нужно вернуться к старой структуре:

```bash
# Восстановите из резервной копии
rm -rf online_customer
mv online_customer_backup online_customer

# Восстановите базу данных
psql online_customer < backup.sql
```

## Преимущества новой структуры

1. **Независимое развертывание**: Каждый сервис можно развертывать отдельно
2. **Масштабируемость**: Можно запускать несколько экземпляров каждого сервиса
3. **Изоляция**: Проблемы в одном сервисе не влияют на другой
4. **Упрощенное обновление**: Можно обновлять сервисы независимо
5. **Docker**: Контейнеризация упрощает развертывание

## Мониторинг

### Логи
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f admin
docker-compose logs -f bot
```

### Статус сервисов
```bash
docker-compose ps
```

### Использование ресурсов
```bash
docker stats
```

## Обновление

### Обновление кода
```bash
git pull origin main
docker-compose up --build -d
```

### Обновление зависимостей
```bash
# Обновите requirements.txt в каждом сервисе
docker-compose build --no-cache
docker-compose up -d
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус: `docker-compose ps`
3. Проверьте конфигурацию: `.env` файлы
4. Проверьте подключение к БД
5. Обратитесь к документации в `README.md` файлах
