# 📁 Файлы для развертывания проекта

## 🐳 Docker конфигурация

### Основные файлы
- **`docker-compose.prod.yml`** - Docker Compose для продакшена с HTTPS
- **`env.prod.example`** - Пример файла с переменными окружения

### Структура сервисов
```
├── nginx          # Reverse proxy с SSL
├── admin          # Админ-панель API
├── db            # PostgreSQL база данных
└── certbot       # Автоматическое получение SSL сертификатов
```

## 🌐 Nginx конфигурация

### Файлы конфигурации
- **`nginx/nginx.conf`** - Основная конфигурация Nginx
- **`nginx/conf.d/default.conf`** - Конфигурация виртуального хоста
- **`nginx/webroot/`** - Директория для валидации SSL (Let's Encrypt)

### Особенности
- Автоматический редирект HTTP → HTTPS
- SSL/TLS конфигурация
- CORS заголовки для API
- Кеширование статических файлов
- Безопасность (HSTS, CSP, X-Frame-Options)

## 🚀 Скрипты развертывания

### Основные скрипты
- **`scripts/setup-server.sh`** - Первоначальная настройка сервера
- **`scripts/deploy-production.sh`** - Автоматическое развертывание
- **`scripts/update-app.sh`** - Обновление приложения
- **`scripts/renew-ssl.sh`** - Обновление SSL сертификатов
- **`scripts/backup.sh`** - Резервное копирование

### Права доступа
Все скрипты имеют права на выполнение:
```bash
chmod +x scripts/*.sh
```

## 📚 Документация

### Инструкции
- **`DEPLOYMENT.md`** - Подробная инструкция по развертыванию
- **`BEGET_SETUP.md`** - Специальная инструкция для beget.com
- **`QUICK_START.md`** - Краткое руководство по быстрому запуску
- **`DEPLOYMENT_FILES.md`** - Этот файл с описанием всех файлов

## 🔧 Переменные окружения

### Обязательные переменные в .env.prod
```bash
DOMAIN_NAME=your-domain.com                    # Домен сайта
DB_PASSWORD=your_secure_db_password_here       # Пароль БД
ADMIN_USERNAME=admin                           # Логин админа
ADMIN_PASSWORD=your_secure_admin_password_here # Пароль админа
SECRET_KEY=your-super-secret-key-32-chars+     # Секретный ключ
SSL_EMAIL=your-email@domain.com               # Email для SSL
ENVIRONMENT=production                         # Окружение
```

## 🌍 Порты и сервисы

### Внешние порты
- **80** - HTTP (редирект на HTTPS)
- **443** - HTTPS (основной трафик)

### Внутренние порты
- **8000** - Админ-панель API
- **5432** - PostgreSQL база данных

## 🔒 Безопасность

### SSL/TLS
- Автоматическое получение сертификатов Let's Encrypt
- Автоматическое обновление сертификатов
- HSTS заголовки
- Современные TLS протоколы (1.2, 1.3)

### Файрвол
- Открыты только необходимые порты (22, 80, 443)
- SSH доступ по ключам
- Защита от DDoS

### База данных
- Изолированная сеть Docker
- Сложные пароли
- Регулярные бэкапы

## 📊 Мониторинг

### Логи
```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f admin
docker-compose -f docker-compose.prod.yml logs -f db
```

### Статус
```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Использование ресурсов
docker stats
```

## 💾 Резервное копирование

### Автоматические бэкапы
- База данных (SQL дамп)
- Файлы проекта
- SSL сертификаты
- Манифест бэкапа

### Команды
```bash
# Создание бэкапа
./scripts/backup.sh backup

# Список бэкапов
./scripts/backup.sh list

# Восстановление
./scripts/backup.sh restore backup_name
```

## 🔄 Обновления

### Автоматические
- SSL сертификаты (каждые 2 месяца)
- Резервные копии (ежедневно)

### Ручные
```bash
# Обновление приложения
./scripts/update-app.sh

# Обновление SSL
./scripts/renew-ssl.sh

# Откат изменений
./scripts/update-app.sh rollback
```

## 🎯 Готовые URL после развертывания

- **Telegram Mini App**: `https://your-domain.com`
- **Админ-панель**: `https://your-domain.com/admin/`
- **API документация**: `https://your-domain.com/docs/`
- **API эндпоинты**: `https://your-domain.com/api/`

## ✅ Чек-лист готовности

- [ ] Все файлы скопированы на сервер
- [ ] Переменные окружения настроены
- [ ] DNS записи настроены
- [ ] SSL сертификат получен
- [ ] Все сервисы запущены
- [ ] Сайт доступен по HTTPS
- [ ] Админ-панель работает
- [ ] API отвечает корректно
- [ ] Настроено резервное копирование
- [ ] Настроены автоматические обновления

**Проект готов к продакшену!** 🚀
