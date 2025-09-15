# 🚀 Инструкция по развертыванию проекта на сервере beget.com

Данная инструкция поможет вам развернуть Telegram Mini App с админ-панелью на удаленном сервере с поддержкой HTTPS.

## 📋 Требования

### Системные требования
- Ubuntu 20.04+ или Debian 11+
- Минимум 2 GB RAM
- Минимум 20 GB свободного места
- Подключение к интернету
- Доменное имя (например, your-domain.com)

### Подготовка домена
1. Зарегистрируйте домен
2. Настройте DNS записи для вашего домена:
   - A-запись: `@` → IP адрес вашего сервера
   - A-запись: `www` → IP адрес вашего сервера

## 🔧 Подготовка сервера

### 1. Подключение к серверу

```bash
# Подключение по SSH
ssh root@your-server-ip

# Или если у вас есть пользователь
ssh username@your-server-ip
```

### 2. Первоначальная настройка сервера

Скопируйте проект на сервер и запустите скрипт настройки:

```bash
# Скачивание проекта
git clone https://github.com/your-repo/online_customer.git
cd online_customer

# Запуск скрипта настройки сервера
chmod +x scripts/setup-server.sh
./scripts/setup-server.sh
```

**Важно**: После выполнения скрипта перезайдите в систему для применения изменений группы docker.

### 3. Настройка переменных окружения

```bash
# Копирование примера конфигурации
cp env.prod.example .env.prod

# Редактирование конфигурации
nano .env.prod
```

Обязательно настройте следующие переменные в файле `.env.prod`:

```bash
# Домен вашего сайта
DOMAIN_NAME=your-domain.com

# Пароль для базы данных (сложный пароль)
DB_PASSWORD=your_secure_db_password_here

# Пароль администратора (сложный пароль)
ADMIN_PASSWORD=your_secure_admin_password_here

# Секретный ключ (минимум 32 символа)
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars

# Email для SSL сертификата
SSL_EMAIL=your-email@domain.com

# Окружение
ENVIRONMENT=production
```

### 4. Развертывание проекта

```bash
# Запуск скрипта развертывания
chmod +x scripts/deploy-production.sh
./scripts/deploy-production.sh
```

Скрипт автоматически:
- Проверит все требования
- Обновит конфигурацию Nginx
- Получит SSL сертификат от Let's Encrypt
- Запустит все сервисы
- Настроит автоматическое обновление SSL

## 🌐 Доступ к приложению

После успешного развертывания ваше приложение будет доступно по адресам:

- **Telegram Mini App**: `https://your-domain.com`
- **Админ-панель**: `https://your-domain.com/admin/`
- **API документация**: `https://your-domain.com/docs/`

### Вход в админ-панель

1. Перейдите по адресу `https://your-domain.com/admin/`
2. Введите логин: `admin`
3. Введите пароль, который вы указали в `ADMIN_PASSWORD`

## 🔍 Мониторинг и управление

### Проверка статуса сервисов

```bash
# Статус всех контейнеров
docker-compose -f docker-compose.prod.yml ps

# Логи всех сервисов
docker-compose -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f admin
docker-compose -f docker-compose.prod.yml logs -f db
```

### Управление сервисами

```bash
# Остановка всех сервисов
docker-compose -f docker-compose.prod.yml down

# Запуск всех сервисов
docker-compose -f docker-compose.prod.yml up -d

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.prod.yml restart nginx
docker-compose -f docker-compose.prod.yml restart admin
```

### Обновление приложения

```bash
# Остановка сервисов
docker-compose -f docker-compose.prod.yml down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build
```

## 💾 Резервное копирование

### Создание бэкапа

```bash
# Создание полного бэкапа
./scripts/backup.sh backup

# Просмотр списка бэкапов
./scripts/backup.sh list
```

### Восстановление из бэкапа

```bash
# Восстановление из конкретного бэкапа
./scripts/backup.sh restore backup_20241201_120000
```

## 🔒 Безопасность

### Рекомендации по безопасности

1. **Используйте сложные пароли** для всех сервисов
2. **Регулярно обновляйте** систему и зависимости
3. **Настройте файрвол** (уже настроен скриптом)
4. **Используйте SSH ключи** вместо паролей
5. **Регулярно создавайте бэкапы**

### Настройка SSH ключей

```bash
# На вашем локальном компьютере
ssh-keygen -t rsa -b 4096 -C "your-email@domain.com"

# Копирование ключа на сервер
ssh-copy-id username@your-server-ip

# Отключение входа по паролю (после проверки SSH ключа)
sudo nano /etc/ssh/sshd_config
# Раскомментируйте: PasswordAuthentication no
sudo systemctl restart sshd
```

## 🛠️ Устранение неполадок

### Проблемы с SSL сертификатами

```bash
# Принудительное обновление SSL сертификата
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal

# Перезапуск Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Проблемы с базой данных

```bash
# Проверка подключения к базе данных
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Подключение к базе данных
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d online_customer

# Восстановление базы данных
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres -d online_customer < backup.sql
```

### Проблемы с Nginx

```bash
# Проверка конфигурации Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Перезагрузка конфигурации Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Проблемы с приложением

```bash
# Проверка логов приложения
docker-compose -f docker-compose.prod.yml logs admin

# Перезапуск приложения
docker-compose -f docker-compose.prod.yml restart admin
```

## 📊 Мониторинг производительности

### Проверка использования ресурсов

```bash
# Использование CPU и памяти
docker stats

# Использование диска
df -h

# Использование памяти
free -h
```

### Логи системы

```bash
# Логи системы
sudo journalctl -f

# Логи Docker
sudo journalctl -u docker.service -f
```

## 🔄 Автоматизация

### Настройка автоматических обновлений

```bash
# Создание cron задачи для обновления SSL
crontab -e

# Добавьте строку для обновления SSL каждые 2 месяца
0 2 1 */2 * cd /path/to/your/project && ./scripts/renew-ssl.sh
```

### Настройка автоматических бэкапов

```bash
# Добавление в crontab для ежедневных бэкапов в 3:00
0 3 * * * cd /path/to/your/project && ./scripts/backup.sh backup
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте доступность домена
4. Убедитесь, что порты 80 и 443 открыты в файрволе

### Полезные команды для диагностики

```bash
# Проверка открытых портов
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Проверка DNS
nslookup your-domain.com

# Проверка SSL сертификата
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

## 🎯 Заключение

После выполнения всех шагов у вас будет полностью настроенный и защищенный сервер с:

- ✅ Telegram Mini App с HTTPS
- ✅ Админ-панель с веб-интерфейсом
- ✅ API с автоматической документацией
- ✅ Автоматические SSL сертификаты
- ✅ Система резервного копирования
- ✅ Мониторинг и логирование
- ✅ Настройки безопасности

Ваш проект готов к продакшену! 🚀
