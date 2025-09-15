#!/bin/bash

# Скрипт для развертывания проекта на продакшн сервере
# Использование: ./scripts/deploy-production.sh

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия необходимых файлов
check_requirements() {
    log "Проверка требований..."
    
    if [ ! -f "env.prod.example" ]; then
        error "Файл env.prod.example не найден!"
        exit 1
    fi
    
    if [ ! -f "docker-compose.prod.yml" ]; then
        error "Файл docker-compose.prod.yml не найден!"
        exit 1
    fi
    
    if [ ! -d "nginx" ]; then
        error "Папка nginx не найдена!"
        exit 1
    fi
    
    log "Все требования выполнены ✓"
}

# Создание .env файла для продакшена
setup_env() {
    log "Настройка переменных окружения..."
    
    if [ ! -f ".env.prod" ]; then
        if [ -f "env.prod.example" ]; then
            cp env.prod.example .env.prod
            warn "Создан файл .env.prod на основе env.prod.example"
            warn "ВАЖНО: Отредактируйте файл .env.prod перед продолжением!"
            echo ""
            echo "Необходимо настроить следующие переменные:"
            echo "- DOMAIN_NAME: ваш домен"
            echo "- DB_PASSWORD: пароль для базы данных"
            echo "- ADMIN_PASSWORD: пароль администратора"
            echo "- SECRET_KEY: секретный ключ (минимум 32 символа)"
            echo "- SSL_EMAIL: email для SSL сертификата"
            echo ""
            read -p "Нажмите Enter после редактирования .env.prod файла..."
        else
            error "Файл env.prod.example не найден!"
            exit 1
        fi
    fi
    
    # Проверка обязательных переменных
    source .env.prod
    
    if [ -z "$DOMAIN_NAME" ] || [ "$DOMAIN_NAME" = "your-domain.com" ]; then
        error "Необходимо настроить DOMAIN_NAME в файле .env.prod"
        exit 1
    fi
    
    if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your_secure_db_password_here" ]; then
        error "Необходимо настроить DB_PASSWORD в файле .env.prod"
        exit 1
    fi
    
    if [ -z "$ADMIN_PASSWORD" ] || [ "$ADMIN_PASSWORD" = "your_secure_admin_password_here" ]; then
        error "Необходимо настроить ADMIN_PASSWORD в файле .env.prod"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production-min-32-chars" ]; then
        error "Необходимо настроить SECRET_KEY в файле .env.prod"
        exit 1
    fi
    
    if [ -z "$SSL_EMAIL" ] || [ "$SSL_EMAIL" = "your-email@domain.com" ]; then
        error "Необходимо настроить SSL_EMAIL в файле .env.prod"
        exit 1
    fi
    
    log "Переменные окружения настроены ✓"
}

# Обновление конфигурации Nginx с доменом
update_nginx_config() {
    log "Обновление конфигурации Nginx..."
    
    source .env.prod
    
    # Замена домена в конфигурации Nginx
    sed -i.bak "s/your-domain.com/$DOMAIN_NAME/g" nginx/conf.d/default.conf
    
    log "Конфигурация Nginx обновлена ✓"
}

# Создание необходимых директорий
create_directories() {
    log "Создание необходимых директорий..."
    
    mkdir -p ssl
    mkdir -p nginx/webroot
    mkdir -p logs
    
    log "Директории созданы ✓"
}

# Остановка старых контейнеров
stop_old_containers() {
    log "Остановка старых контейнеров..."
    
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    log "Старые контейнеры остановлены ✓"
}

# Получение SSL сертификата
get_ssl_certificate() {
    log "Получение SSL сертификата..."

    source .env.prod

    # Проверка переменных
    if [ -z "$DOMAIN_NAME" ]; then
        error "DOMAIN_NAME не настроен в .env.prod"
        exit 1
    fi

    if [ -z "$SSL_EMAIL" ]; then
        error "SSL_EMAIL не настроен в .env.prod"
        exit 1
    fi

    # Сначала запускаем nginx для валидации домена
    docker-compose -f docker-compose.prod.yml up -d nginx

    # Ждем запуска nginx
    sleep 10

    # Получаем сертификат с явным указанием email
    docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email "$SSL_EMAIL" --agree-tos --no-eff-email -d "$DOMAIN_NAME"

    if [ $? -eq 0 ]; then
        log "SSL сертификат получен ✓"
    else
        error "Ошибка получения SSL сертификата"
        exit 1
    fi
}

# Запуск всех сервисов
start_services() {
    log "Запуск всех сервисов..."
    
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    
    log "Сервисы запущены ✓"
}

# Проверка статуса сервисов
check_services() {
    log "Проверка статуса сервисов..."
    
    sleep 30  # Ждем запуска всех сервисов
    
    # Проверка nginx
    if curl -f -s http://localhost > /dev/null 2>&1; then
        log "Nginx работает ✓"
    else
        warn "Nginx не отвечает"
    fi
    
    # Проверка админ-панели
    if curl -f -s http://localhost/api/restaurants > /dev/null 2>&1; then
        log "API админ-панели работает ✓"
    else
        warn "API админ-панели не отвечает"
    fi
    
    # Проверка базы данных
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log "База данных работает ✓"
    else
        warn "База данных не отвечает"
    fi
}

# Создание cron задачи для обновления SSL
setup_ssl_renewal() {
    log "Настройка автоматического обновления SSL сертификатов..."
    
    # Создаем скрипт для обновления SSL
    cat > scripts/renew-ssl.sh << 'EOF'
#!/bin/bash
cd /path/to/your/project
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
EOF
    
    chmod +x scripts/renew-ssl.sh
    
    # Добавляем в crontab (обновление каждые 2 месяца)
    (crontab -l 2>/dev/null; echo "0 2 1 */2 * /path/to/your/project/scripts/renew-ssl.sh") | crontab -
    
    log "Автоматическое обновление SSL настроено ✓"
}

# Основная функция
main() {
    log "Начинаем развертывание проекта..."
    
    check_requirements
    setup_env
    update_nginx_config
    create_directories
    stop_old_containers
    get_ssl_certificate
    start_services
    check_services
    setup_ssl_renewal
    
    log "Развертывание завершено успешно! 🎉"
    echo ""
    echo "Ваш проект доступен по адресу:"
    echo "- Telegram Mini App: https://$DOMAIN_NAME"
    echo "- Админ-панель: https://$DOMAIN_NAME/admin/"
    echo "- API документация: https://$DOMAIN_NAME/docs/"
    echo ""
    echo "Логи сервисов:"
    echo "- docker-compose -f docker-compose.prod.yml logs -f"
    echo "- docker-compose -f docker-compose.prod.yml logs -f nginx"
    echo "- docker-compose -f docker-compose.prod.yml logs -f admin"
}

# Запуск
main "$@"
