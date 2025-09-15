#!/bin/bash

# Скрипт для развертывания проекта на сервере с IP адресом
# Использование: ./scripts/deploy-ip-server.sh

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
    
    if [ ! -f ".env.prod" ]; then
        error "Файл .env.prod не найден! Создайте его на основе env.prod.example"
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
    
    log "Переменные окружения настроены ✓"
}

# Обновление конфигурации Nginx с IP адресом
update_nginx_config() {
    log "Обновление конфигурации Nginx для IP адреса..."
    
    source .env.prod
    
    # Создаем конфигурацию для IP адреса (без SSL)
    cat > nginx/conf.d/default.conf << EOF
# HTTP сервер для IP адреса
server {
    listen 80;
    server_name _;

    # Основное приложение (Telegram Mini App)
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # CORS заголовки
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        # Кеширование статических файлов
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API админ-панели
    location /api/ {
        proxy_pass http://admin:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS заголовки для API
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        # Обработка preflight запросов
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "*";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 200;
        }
    }

    # Админ-панель (веб-интерфейс)
    location /admin/ {
        proxy_pass http://admin:8000/admin/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Статические файлы админ-панели
    location /static/ {
        proxy_pass http://admin:8000/static/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Кеширование
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Документация API
    location /docs/ {
        proxy_pass http://admin:8000/docs/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    log "Конфигурация Nginx обновлена для IP адреса ✓"
}

# Создание необходимых директорий
create_directories() {
    log "Создание необходимых директорий..."
    
    mkdir -p logs
    mkdir -p db/backups
    
    log "Директории созданы ✓"
}

# Остановка старых контейнеров
stop_old_containers() {
    log "Остановка старых контейнеров..."
    
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    log "Старые контейнеры остановлены ✓"
}

# Создание упрощенного docker-compose для IP адреса
create_simple_docker_compose() {
    log "Создание упрощенной конфигурации Docker Compose..."
    
    cat > docker-compose.ip.yml << EOF
version: '3.8'

services:
  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./public:/usr/share/nginx/html:ro
    depends_on:
      - admin
    restart: unless-stopped
    networks:
      - app-network

  # Админ-панель API
  admin:
    build:
      context: .
      dockerfile: admin_service/docker/Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:\${DB_PASSWORD}@db:5432/online_customer
      - ADMIN_USERNAME=\${ADMIN_USERNAME}
      - ADMIN_PASSWORD=\${ADMIN_PASSWORD}
      - SECRET_KEY=\${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - app-network
    volumes:
      - ./admin_service/admin/static:/app/admin/static:ro
      - ./admin_service/admin/templates:/app/admin/templates:ro

  # База данных PostgreSQL
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=online_customer
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=\${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
EOF
    
    log "Упрощенная конфигурация Docker Compose создана ✓"
}

# Инициализация базы данных
init_database() {
    log "Инициализация базы данных..."
    
    # Ждем запуска базы данных
    sleep 10
    
    # Запускаем миграции
    docker-compose -f docker-compose.ip.yml exec -T admin alembic upgrade head || {
        warn "Миграции не выполнены, возможно база данных еще не готова"
    }
    
    # Заполняем тестовыми данными
    docker-compose -f docker-compose.ip.yml exec -T admin python shared/seed.py || {
        warn "Тестовые данные не загружены"
    }
    
    log "База данных инициализирована ✓"
}

# Запуск всех сервисов
start_services() {
    log "Запуск всех сервисов..."
    
    docker-compose -f docker-compose.ip.yml down
    docker-compose -f docker-compose.ip.yml up -d
    
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
    if docker-compose -f docker-compose.ip.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log "База данных работает ✓"
    else
        warn "База данных не отвечает"
    fi
}

# Основная функция
main() {
    log "Начинаем развертывание проекта на IP сервере..."
    
    check_requirements
    setup_env
    update_nginx_config
    create_directories
    stop_old_containers
    create_simple_docker_compose
    start_services
    init_database
    check_services
    
    log "Развертывание завершено успешно! 🎉"
    echo ""
    echo "Ваш проект доступен по адресу:"
    echo "- Telegram Mini App: http://$DOMAIN_NAME"
    echo "- Админ-панель: http://$DOMAIN_NAME/admin/"
    echo "- API документация: http://$DOMAIN_NAME/docs/"
    echo ""
    echo "Логи сервисов:"
    echo "- docker-compose -f docker-compose.ip.yml logs -f"
    echo "- docker-compose -f docker-compose.ip.yml logs -f nginx"
    echo "- docker-compose -f docker-compose.ip.yml logs -f admin"
    echo ""
    echo "Управление сервисами:"
    echo "- Остановка: docker-compose -f docker-compose.ip.yml down"
    echo "- Запуск: docker-compose -f docker-compose.ip.yml up -d"
    echo "- Перезапуск: docker-compose -f docker-compose.ip.yml restart"
}

# Запуск
main "$@"
