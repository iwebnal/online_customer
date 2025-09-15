# 🚀 Быстрая настройка на beget.com

Данная инструкция специально адаптирована для хостинга beget.com.

## 📋 Предварительные требования

1. **VPS/VDS сервер** на beget.com с Ubuntu 20.04+
2. **Доменное имя** (можно зарегистрировать через beget)
3. **SSH доступ** к серверу

## 🔧 Пошаговая настройка

### Шаг 1: Подключение к серверу

```bash
# Подключение по SSH
ssh root@your-server-ip

# Или если используется пользователь
ssh username@your-server-ip
```

### Шаг 2: Клонирование проекта

```bash
# Установка git (если не установлен)
apt update && apt install -y git

# Клонирование проекта
git clone https://github.com/your-repo/online_customer.git
cd online_customer
```

### Шаг 3: Автоматическая настройка сервера

```bash
# Запуск скрипта настройки
chmod +x scripts/setup-server.sh
./scripts/setup-server.sh
```

**Важно**: После выполнения перезайдите в систему:
```bash
exit
ssh username@your-server-ip
```

### Шаг 4: Настройка переменных окружения

```bash
# Копирование конфигурации
cp env.prod.example .env.prod

# Редактирование (замените на ваши данные)
nano .env.prod
```

**Обязательно измените:**
```bash
DOMAIN_NAME=your-domain.com                    # Ваш домен
DB_PASSWORD=your_secure_db_password_here       # Сложный пароль
ADMIN_PASSWORD=your_secure_admin_password_here # Сложный пароль
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars  # 32+ символов
SSL_EMAIL=your-email@domain.com               # Ваш email
```

### Шаг 5: Настройка DNS (в панели beget)

1. Зайдите в панель управления beget.com
2. Перейдите в раздел "Домены"
3. Настройте DNS записи:
   - **A-запись**: `@` → IP вашего сервера
   - **A-запись**: `www` → IP вашего сервера

### Шаг 6: Развертывание приложения

```bash
# Запуск скрипта развертывания
chmod +x scripts/deploy-production.sh
./scripts/deploy-production.sh
```

Скрипт автоматически:
- ✅ Получит SSL сертификат
- ✅ Настроит Nginx
- ✅ Запустит все сервисы

### Шаг 7: Проверка работы

После завершения развертывания проверьте:

1. **Telegram Mini App**: https://your-domain.com
2. **Админ-панель**: https://your-domain.com/admin/
3. **API документация**: https://your-domain.com/docs/

## 🔍 Проверка статуса

```bash
# Статус сервисов
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f
```

## 🛠️ Управление на beget.com

### Через панель управления

1. **Мониторинг**: Раздел "Мониторинг" → "Статистика"
2. **Бэкапы**: Раздел "Резервные копии"
3. **Файрвол**: Раздел "Безопасность" → "Файрвол"

### Через SSH

```bash
# Остановка сервисов
docker-compose -f docker-compose.prod.yml down

# Запуск сервисов
docker-compose -f docker-compose.prod.yml up -d

# Обновление
git pull && docker-compose -f docker-compose.prod.yml up -d --build
```

## 💾 Резервное копирование

### Автоматическое (рекомендуется)

```bash
# Создание бэкапа
./scripts/backup.sh backup

# Восстановление
./scripts/backup.sh restore backup_YYYYMMDD_HHMMSS
```

### Через панель beget

1. Зайдите в "Резервные копии"
2. Создайте снимок сервера
3. При необходимости восстановите из снимка

## 🔒 Безопасность для beget.com

### Настройка файрвола в панели

1. Зайдите в "Безопасность" → "Файрвол"
2. Разрешите порты:
   - **22** (SSH)
   - **80** (HTTP)
   - **443** (HTTPS)
3. Запретите все остальные порты

### SSH ключи

```bash
# На локальном компьютере
ssh-keygen -t rsa -b 4096

# Копирование на сервер
ssh-copy-id username@your-server-ip
```

## 📊 Мониторинг

### Через панель beget

- **CPU/RAM**: Раздел "Мониторинг"
- **Диск**: Раздел "Файловая система"
- **Сеть**: Раздел "Сетевые интерфейсы"

### Через SSH

```bash
# Использование ресурсов
htop

# Статус Docker
docker stats

# Логи системы
journalctl -f
```

## 🚨 Устранение неполадок

### Проблемы с доменом

```bash
# Проверка DNS
nslookup your-domain.com

# Проверка доступности
curl -I https://your-domain.com
```

### Проблемы с SSL

```bash
# Принудительное обновление SSL
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker-compose -f docker-compose.prod.yml restart nginx
```

### Проблемы с базой данных

```bash
# Проверка подключения
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Восстановление из бэкапа
./scripts/backup.sh restore backup_name
```

## 📞 Поддержка beget.com

Если возникли проблемы:

1. **Техподдержка beget**: https://beget.com/help
2. **Документация**: https://beget.com/docs
3. **Форум**: https://forum.beget.com

### Контакты поддержки

- **Email**: support@beget.com
- **Телефон**: 8 (800) 700-06-08
- **Онлайн чат**: В панели управления

## ✅ Чек-лист готовности

Перед запуском в продакшн убедитесь:

- [ ] Домен настроен и указывает на сервер
- [ ] SSL сертификат получен и работает
- [ ] Админ-панель доступна по HTTPS
- [ ] API отвечает корректно
- [ ] База данных работает
- [ ] Настроено резервное копирование
- [ ] Файрвол настроен
- [ ] SSH ключи настроены
- [ ] Пароли изменены на сложные

## 🎯 Готово!

Ваш проект успешно развернут на beget.com! 

**Доступные адреса:**
- 🌐 **Telegram Mini App**: https://your-domain.com
- ⚙️ **Админ-панель**: https://your-domain.com/admin/
- 📚 **API документация**: https://your-domain.com/docs/

**Логин в админ-панель:**
- **Логин**: admin
- **Пароль**: тот, что указали в ADMIN_PASSWORD
