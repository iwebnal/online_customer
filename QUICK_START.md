# 🚀 Быстрый старт - Развертывание на beget.com

## ⚡ Краткая инструкция

### 1. Подготовка
```bash
# Подключение к серверу
ssh root@your-server-ip

# Клонирование проекта
git clone https://github.com/your-repo/online_customer.git
cd online_customer
```

### 2. Настройка сервера
```bash
# Автоматическая настройка
chmod +x scripts/setup-server.sh
./scripts/setup-server.sh

# Перезайти в систему
exit && ssh username@your-server-ip
```

### 3. Конфигурация
```bash
# Настройка переменных
cp env.prod.example .env.prod
nano .env.prod  # Изменить DOMAIN_NAME, пароли и email
```

### 4. Развертывание
```bash
# Автоматическое развертывание
chmod +x scripts/deploy-production.sh
./scripts/deploy-production.sh
```

### 5. Готово! 🎉
- **Telegram Mini App**: https://your-domain.com
- **Админ-панель**: https://your-domain.com/admin/
- **API**: https://your-domain.com/docs/

---

## 📋 Обязательные настройки в .env.prod

```bash
DOMAIN_NAME=your-domain.com                    # Ваш домен
DB_PASSWORD=your_secure_db_password_here       # Сложный пароль
ADMIN_PASSWORD=your_secure_admin_password_here # Сложный пароль
SECRET_KEY=your-super-secret-key-32-chars+     # 32+ символов
SSL_EMAIL=your-email@domain.com               # Ваш email
```

---

## 🛠️ Полезные команды

### Управление сервисами
```bash
# Статус
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапуск
docker-compose -f docker-compose.prod.yml restart
```

### Обновление
```bash
# Обновление приложения
./scripts/update-app.sh

# Обновление SSL
./scripts/renew-ssl.sh
```

### Резервное копирование
```bash
# Создание бэкапа
./scripts/backup.sh backup

# Восстановление
./scripts/backup.sh restore backup_name
```

---

## 🔧 Устранение неполадок

### Проблемы с SSL
```bash
./scripts/renew-ssl.sh force
```

### Проблемы с базой данных
```bash
docker-compose -f docker-compose.prod.yml logs db
```

### Проблемы с Nginx
```bash
docker-compose -f docker-compose.prod.yml logs nginx
```

---

## 📞 Поддержка

- **Полная документация**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Настройка для beget.com**: [BEGET_SETUP.md](./BEGET_SETUP.md)
- **Поддержка beget**: https://beget.com/help

---

## ✅ Чек-лист

- [ ] Домен настроен в DNS
- [ ] .env.prod файл настроен
- [ ] SSL сертификат получен
- [ ] Все сервисы запущены
- [ ] Сайт доступен по HTTPS
- [ ] Админ-панель работает
- [ ] API отвечает

**Готово к работе!** 🚀
