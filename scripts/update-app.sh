#!/bin/bash

# Скрипт для обновления приложения
# Использование: ./scripts/update-app.sh

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Создание бэкапа перед обновлением
create_backup() {
    log "Создание бэкапа перед обновлением..."
    
    if [ -f "scripts/backup.sh" ]; then
        ./scripts/backup.sh backup
        log "Бэкап создан ✓"
    else
        warn "Скрипт бэкапа не найден, пропускаем создание бэкапа"
    fi
}

# Обновление кода из репозитория
update_code() {
    log "Обновление кода из репозитория..."
    
    # Сохранение локальных изменений
    if [ -n "$(git status --porcelain)" ]; then
        warn "Обнаружены локальные изменения"
        git stash push -m "Backup before update $(date)"
        log "Локальные изменения сохранены в stash"
    fi
    
    # Получение обновлений
    git fetch origin
    
    # Проверка наличия обновлений
    local current_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/main)
    
    if [ "$current_commit" = "$remote_commit" ]; then
        log "Обновлений нет ✓"
        return 1
    fi
    
    # Применение обновлений
    git pull origin main
    
    log "Код обновлен ✓"
    return 0
}

# Обновление зависимостей
update_dependencies() {
    log "Обновление зависимостей..."
    
    # Проверка изменений в requirements.txt
    if git diff HEAD~1 HEAD --name-only | grep -q "requirements.txt"; then
        log "Обнаружены изменения в requirements.txt"
        log "Пересборка контейнеров..."
        
        # Пересборка админ-панели
        docker-compose -f docker-compose.prod.yml build admin
        
        log "Зависимости обновлены ✓"
    else
        log "Изменений в зависимостях нет ✓"
    fi
}

# Обновление конфигурации
update_config() {
    log "Проверка конфигурации..."
    
    # Проверка изменений в nginx конфигурации
    if git diff HEAD~1 HEAD --name-only | grep -q "nginx/"; then
        log "Обнаружены изменения в конфигурации Nginx"
        
        # Обновление конфигурации Nginx
        source .env.prod
        sed -i.bak "s/your-domain.com/$DOMAIN_NAME/g" nginx/conf.d/default.conf
        
        log "Конфигурация Nginx обновлена ✓"
    fi
    
    # Проверка изменений в docker-compose
    if git diff HEAD~1 HEAD --name-only | grep -q "docker-compose.prod.yml"; then
        log "Обнаружены изменения в docker-compose.prod.yml"
        warn "Проверьте настройки в docker-compose.prod.yml"
    fi
}

# Применение миграций базы данных
run_migrations() {
    log "Проверка миграций базы данных..."
    
    # Проверка наличия новых миграций
    if [ -d "alembic" ]; then
        log "Применение миграций базы данных..."
        
        # Запуск миграций
        docker-compose -f docker-compose.prod.yml exec -T admin alembic upgrade head
        
        if [ $? -eq 0 ]; then
            log "Миграции применены ✓"
        else
            error "Ошибка применения миграций"
            exit 1
        fi
    else
        log "Миграции не найдены ✓"
    fi
}

# Перезапуск сервисов
restart_services() {
    log "Перезапуск сервисов..."
    
    # Остановка сервисов
    docker-compose -f docker-compose.prod.yml down
    
    # Запуск сервисов
    docker-compose -f docker-compose.prod.yml up -d
    
    # Ожидание запуска
    sleep 30
    
    log "Сервисы перезапущены ✓"
}

# Проверка работоспособности
verify_services() {
    log "Проверка работоспособности сервисов..."
    
    source .env.prod
    
    # Проверка Nginx
    if curl -f -s http://localhost > /dev/null 2>&1; then
        log "Nginx работает ✓"
    else
        warn "Nginx не отвечает"
    fi
    
    # Проверка API
    if curl -f -s http://localhost/api/restaurants > /dev/null 2>&1; then
        log "API работает ✓"
    else
        warn "API не отвечает"
    fi
    
    # Проверка базы данных
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log "База данных работает ✓"
    else
        warn "База данных не отвечает"
    fi
    
    # Проверка HTTPS
    if curl -f -s https://$DOMAIN_NAME > /dev/null 2>&1; then
        log "HTTPS работает ✓"
    else
        warn "HTTPS не работает"
    fi
}

# Откат изменений
rollback() {
    log "Откат к предыдущей версии..."
    
    # Откат кода
    git reset --hard HEAD~1
    
    # Перезапуск сервисов
    restart_services
    
    log "Откат завершен ✓"
}

# Показать статус
show_status() {
    log "Статус сервисов:"
    echo ""
    
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    log "Последние коммиты:"
    git log --oneline -5
    
    echo ""
    log "Статус git:"
    git status --short
}

# Основная функция
main() {
    case "${1:-update}" in
        "update")
            log "Начинаем обновление приложения..."
            
            create_backup
            
            if update_code; then
                update_dependencies
                update_config
                run_migrations
                restart_services
                verify_services
                log "Обновление завершено успешно! 🎉"
            else
                log "Обновлений нет, проверяем статус..."
                show_status
            fi
            ;;
        "rollback")
            rollback
            ;;
        "status")
            show_status
            ;;
        "restart")
            restart_services
            verify_services
            ;;
        "migrate")
            run_migrations
            ;;
        "backup")
            create_backup
            ;;
        *)
            echo "Использование: $0 [update|rollback|status|restart|migrate|backup]"
            echo ""
            echo "Команды:"
            echo "  update   - Обновить приложение (по умолчанию)"
            echo "  rollback - Откатиться к предыдущей версии"
            echo "  status   - Показать статус сервисов и git"
            echo "  restart  - Перезапустить сервисы"
            echo "  migrate  - Применить миграции БД"
            echo "  backup   - Создать бэкап"
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
