#!/bin/bash

# Скрипт для резервного копирования данных
# Использование: ./scripts/backup.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Настройки
BACKUP_DIR="/opt/backups/online_customer"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${DATE}"

# Создание директории для бэкапов
create_backup_directory() {
    log "Создание директории для бэкапов..."
    sudo mkdir -p $BACKUP_DIR
    sudo chown $USER:$USER $BACKUP_DIR
    log "Директория для бэкапов создана ✓"
}

# Бэкап базы данных
backup_database() {
    log "Создание бэкапа базы данных..."
    
    # Загрузка переменных окружения
    source .env.prod
    
    # Создание дампа базы данных
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres online_customer > "$BACKUP_DIR/${BACKUP_NAME}_database.sql"
    
    if [ $? -eq 0 ]; then
        log "Бэкап базы данных создан ✓"
    else
        error "Ошибка создания бэкапа базы данных"
        exit 1
    fi
}

# Бэкап файлов проекта
backup_project_files() {
    log "Создание бэкапа файлов проекта..."
    
    # Создание архива проекта (исключая ненужные файлы)
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_project.tar.gz" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='logs' \
        --exclude='ssl' \
        .
    
    if [ $? -eq 0 ]; then
        log "Бэкап файлов проекта создан ✓"
    else
        error "Ошибка создания бэкапа файлов проекта"
        exit 1
    fi
}

# Бэкап SSL сертификатов
backup_ssl_certificates() {
    log "Создание бэкапа SSL сертификатов..."
    
    if [ -d "ssl" ]; then
        tar -czf "$BACKUP_DIR/${BACKUP_NAME}_ssl.tar.gz" ssl/
        log "Бэкап SSL сертификатов создан ✓"
    else
        warn "Директория ssl не найдена, пропускаем бэкап SSL"
    fi
}

# Создание манифеста бэкапа
create_backup_manifest() {
    log "Создание манифеста бэкапа..."
    
    cat > "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt" << EOF
Backup created: $(date)
Backup name: $BACKUP_NAME
Database: ${BACKUP_NAME}_database.sql
Project files: ${BACKUP_NAME}_project.tar.gz
SSL certificates: ${BACKUP_NAME}_ssl.tar.gz

System information:
- Hostname: $(hostname)
- OS: $(lsb_release -d | cut -f2)
- Docker version: $(docker --version)
- Docker Compose version: $(docker-compose --version)

Project information:
- Domain: ${DOMAIN_NAME:-"not set"}
- Environment: production
EOF

    log "Манифест бэкапа создан ✓"
}

# Очистка старых бэкапов
cleanup_old_backups() {
    log "Очистка старых бэкапов..."
    
    # Удаление бэкапов старше 30 дней
    find $BACKUP_DIR -name "backup_*" -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
    find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete 2>/dev/null || true
    find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete 2>/dev/null || true
    find $BACKUP_DIR -name "backup_*.txt" -mtime +30 -delete 2>/dev/null || true
    
    log "Старые бэкапы очищены ✓"
}

# Восстановление из бэкапа
restore_backup() {
    local backup_name=$1
    
    if [ -z "$backup_name" ]; then
        error "Необходимо указать имя бэкапа для восстановления"
        exit 1
    fi
    
    log "Восстановление из бэкапа: $backup_name"
    
    # Проверка существования файлов бэкапа
    if [ ! -f "$BACKUP_DIR/${backup_name}_database.sql" ]; then
        error "Файл бэкапа базы данных не найден: ${backup_name}_database.sql"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_DIR/${backup_name}_project.tar.gz" ]; then
        error "Файл бэкапа проекта не найден: ${backup_name}_project.tar.gz"
        exit 1
    fi
    
    # Остановка сервисов
    docker-compose -f docker-compose.prod.yml down
    
    # Восстановление файлов проекта
    tar -xzf "$BACKUP_DIR/${backup_name}_project.tar.gz"
    
    # Запуск сервисов
    docker-compose -f docker-compose.prod.yml up -d
    
    # Ожидание запуска базы данных
    sleep 30
    
    # Восстановление базы данных
    docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres -d online_customer < "$BACKUP_DIR/${backup_name}_database.sql"
    
    # Восстановление SSL сертификатов (если есть)
    if [ -f "$BACKUP_DIR/${backup_name}_ssl.tar.gz" ]; then
        tar -xzf "$BACKUP_DIR/${backup_name}_ssl.tar.gz"
    fi
    
    log "Восстановление завершено ✓"
}

# Список доступных бэкапов
list_backups() {
    log "Доступные бэкапы:"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -la "$BACKUP_DIR" | grep -E "(backup_|\.sql$|\.tar\.gz$)" | while read line; do
            echo "  $line"
        done
    else
        echo "  Директория бэкапов не найдена"
    fi
}

# Основная функция
main() {
    case "${1:-backup}" in
        "backup")
            create_backup_directory
            backup_database
            backup_project_files
            backup_ssl_certificates
            create_backup_manifest
            cleanup_old_backups
            log "Бэкап создан успешно! 🎉"
            echo ""
            echo "Файлы бэкапа:"
            echo "- База данных: $BACKUP_DIR/${BACKUP_NAME}_database.sql"
            echo "- Файлы проекта: $BACKUP_DIR/${BACKUP_NAME}_project.tar.gz"
            echo "- SSL сертификаты: $BACKUP_DIR/${BACKUP_NAME}_ssl.tar.gz"
            echo "- Манифест: $BACKUP_DIR/${BACKUP_NAME}_manifest.txt"
            ;;
        "restore")
            restore_backup "$2"
            ;;
        "list")
            list_backups
            ;;
        *)
            echo "Использование: $0 [backup|restore <backup_name>|list]"
            echo ""
            echo "Команды:"
            echo "  backup  - Создать бэкап (по умолчанию)"
            echo "  restore - Восстановить из бэкапа"
            echo "  list    - Показать список бэкапов"
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
