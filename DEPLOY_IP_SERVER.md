# 🚀 Развертывание на сервере с IP адресом 45.141.76.16

Данная инструкция поможет вам развернуть Telegram Mini App с админ-панелью на сервере с IP адресом без доменного имени.

## 📋 Предварительные требования

1. **VPS/VDS сервер** с Ubuntu 20.04+ или Debian 11+
2. **SSH доступ** к серверу
3. **IP адрес**: 45.141.76.16 (или ваш IP)
4. **Открытые порты**: 22 (SSH), 80 (HTTP)

## 🔧 Пошаговая настройка

### Шаг 1: Подключение к серверу

```bash
# Подключение по SSH
ssh root@45.141.76.16

# Или если используется пользователь
ssh username@45.141.76.16
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
ssh username@45.141.76.16
cd online_customer
```

### Шаг 4: Настройка переменных окружения

Файл `.env.prod` уже настроен для IP адреса 45.141.76.16:

```bash
# Проверяем настройки
cat .env.prod
```

Если нужно изменить IP адрес:
```bash
# Редактирование IP адреса
nano .env.prod
# Измените DOMAIN_NAME на ваш IP адрес
```

### Шаг 5: Развертывание приложения

```bash
# Запуск скрипта развертывания для IP сервера
chmod +x scripts/deploy-ip-server.sh
./scripts/deploy-ip-server.sh
```

Скрипт автоматически:
- ✅ Создаст упрощенную конфигурацию без SSL
- ✅ Настроит Nginx для работы с IP адресом
- ✅ Запустит все сервисы
- ✅ Инициализирует базу данных

### Шаг 6: Проверка работы

После завершения развертывания проверьте:

1. **Telegram Mini App**: http://45.141.76.16
2. **Админ-панель**: http://45.141.76.16/admin/
3. **API документация**: http://45.141.76.16/docs/

## 🔍 Проверка статуса

```bash
# Статус сервисов
docker-compose -f docker-compose.ip.yml ps

# Логи
docker-compose -f docker-compose.ip.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.ip.yml logs -f nginx
docker-compose -f docker-compose.ip.yml logs -f admin
docker-compose -f docker-compose.ip.yml logs -f db
```

## 🛠️ Управление сервисами

### Основные команды

```bash
# Остановка сервисов
docker-compose -f docker-compose.ip.yml down

# Запуск сервисов
docker-compose -f docker-compose.ip.yml up -d

# Перезапуск сервисов
docker-compose -f docker-compose.ip.yml restart

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.ip.yml restart nginx
docker-compose -f docker-compose.ip.yml restart admin
```

### Обновление приложения

```bash
# Остановка сервисов
docker-compose -f docker-compose.ip.yml down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose -f docker-compose.ip.yml up -d --build
```

## 💾 Резервное копирование

### Создание бэкапа базы данных

```bash
# Создание бэкапа
docker-compose -f docker-compose.ip.yml exec db pg_dump -U postgres online_customer > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
docker-compose -f docker-compose.ip.yml exec -T db psql -U postgres online_customer < backup_file.sql
```

## 🔒 Безопасность

### Настройка файрвола

```bash
# Установка ufw
apt install -y ufw

# Настройка правил
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp

# Включение файрвола
ufw --force enable

# Проверка статуса
ufw status
```

### Настройка SSH ключей

```bash
# На локальном компьютере
ssh-keygen -t rsa -b 4096

# Копирование на сервер
ssh-copy-id username@45.141.76.16
```

## 📊 Мониторинг

### Проверка использования ресурсов

```bash
# Использование CPU и памяти
docker stats

# Использование диска
df -h

# Использование памяти
free -h

# Логи системы
journalctl -f
```

## 🚨 Устранение неполадок

### Проблемы с доступом к сайту

```bash
# Проверка открытых портов
netstat -tulpn | grep :80

# Проверка статуса nginx
docker-compose -f docker-compose.ip.yml logs nginx

# Проверка конфигурации nginx
docker-compose -f docker-compose.ip.yml exec nginx nginx -t
```

### Проблемы с базой данных

```bash
# Проверка подключения к базе данных
docker-compose -f docker-compose.ip.yml exec db pg_isready -U postgres

# Подключение к базе данных
docker-compose -f docker-compose.ip.yml exec db psql -U postgres -d online_customer

# Проверка логов базы данных
docker-compose -f docker-compose.ip.yml logs db
```

### Проблемы с API

```bash
# Проверка логов админ-панели
docker-compose -f docker-compose.ip.yml logs admin

# Тестирование API
curl -X GET http://45.141.76.16/api/restaurants
curl -X GET http://45.141.76.16/api/products
```

### Проблемы с CORS

Если возникают проблемы с CORS, проверьте:

1. **Конфигурацию Nginx** - убедитесь, что CORS заголовки настроены
2. **URL в frontend** - проверьте, что в `public/app.js` используются правильные URL
3. **Логи браузера** - проверьте консоль браузера на ошибки

## 🔧 Дополнительные настройки

### Настройка автоматического запуска

```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/online-customer.service
```

Содержимое файла:
```ini
[Unit]
Description=Online Customer App
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/online_customer
ExecStart=/usr/local/bin/docker-compose -f docker-compose.ip.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.ip.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Активация сервиса:
```bash
sudo systemctl enable online-customer.service
sudo systemctl start online-customer.service
```

### Настройка логирования

```bash
# Создание директории для логов
mkdir -p logs

# Настройка ротации логов
sudo nano /etc/logrotate.d/online-customer
```

Содержимое файла:
```
/path/to/online_customer/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## ✅ Чек-лист готовности

Перед запуском в продакшн убедитесь:

- [ ] IP адрес настроен в .env.prod
- [ ] URL в public/app.js обновлены на IP адрес
- [ ] Все сервисы запущены и работают
- [ ] Админ-панель доступна по HTTP
- [ ] API отвечает корректно
- [ ] База данных работает
- [ ] Файрвол настроен
- [ ] SSH ключи настроены
- [ ] Пароли изменены на сложные

## 🎯 Готово!

Ваш проект успешно развернут на IP сервере! 

**Доступные адреса:**
- 🌐 **Telegram Mini App**: http://45.141.76.16
- ⚙️ **Админ-панель**: http://45.141.76.16/admin/
- 📚 **API документация**: http://45.141.76.16/docs/

**Логин в админ-панель:**
- **Логин**: admin
- **Пароль**: AdminSecurePass456! (или тот, что указан в ADMIN_PASSWORD)

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте доступность IP адреса
4. Убедитесь, что порт 80 открыт в файрволе

### Полезные команды для диагностики

```bash
# Проверка открытых портов
sudo netstat -tulpn | grep :80

# Проверка доступности
curl -I http://45.141.76.16

# Проверка DNS (если используется домен)
nslookup your-domain.com
```
