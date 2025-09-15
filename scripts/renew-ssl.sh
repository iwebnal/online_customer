#!/bin/bash

# Скрипт для обновления SSL сертификатов
# Использование: ./scripts/renew-ssl.sh

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

# Проверка наличия .env.prod файла
check_env() {
    if [ ! -f ".env.prod" ]; then
        error "Файл .env.prod не найден!"
        exit 1
    fi
    
    source .env.prod
    
    if [ -z "$DOMAIN_NAME" ]; then
        error "DOMAIN_NAME не настроен в .env.prod"
        exit 1
    fi
    
    log "Переменные окружения загружены ✓"
}

# Проверка статуса SSL сертификата
check_ssl_status() {
    log "Проверка статуса SSL сертификата..."
    
    # Проверка срока действия сертификата
    if command -v openssl &> /dev/null; then
        local cert_info=$(echo | openssl s_client -servername $DOMAIN_NAME -connect $DOMAIN_NAME:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            local not_after=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
            local expiry_date=$(date -d "$not_after" +%s)
            local current_date=$(date +%s)
            local days_until_expiry=$(( (expiry_date - current_date) / 86400 ))
            
            log "Сертификат действителен до: $not_after"
            log "Дней до истечения: $days_until_expiry"
            
            if [ $days_until_expiry -lt 30 ]; then
                warn "Сертификат истекает менее чем через 30 дней!"
                return 0
            else
                log "Сертификат действителен ✓"
                return 1
            fi
        else
            warn "Не удалось проверить сертификат"
            return 0
        fi
    else
        warn "OpenSSL не установлен, пропускаем проверку сертификата"
        return 0
    fi
}

# Обновление SSL сертификата
renew_ssl() {
    log "Обновление SSL сертификата..."
    
    # Остановка nginx для освобождения порта 80
    docker-compose -f docker-compose.prod.yml stop nginx
    
    # Обновление сертификата
    docker-compose -f docker-compose.prod.yml run --rm certbot renew
    
    if [ $? -eq 0 ]; then
        log "SSL сертификат обновлен ✓"
    else
        error "Ошибка обновления SSL сертификата"
        docker-compose -f docker-compose.prod.yml start nginx
        exit 1
    fi
    
    # Перезапуск nginx с новым сертификатом
    docker-compose -f docker-compose.prod.yml start nginx
    
    log "Nginx перезапущен с новым сертификатом ✓"
}

# Проверка работы после обновления
verify_ssl() {
    log "Проверка работы SSL после обновления..."
    
    # Ожидание запуска nginx
    sleep 10
    
    # Проверка доступности сайта
    if curl -f -s https://$DOMAIN_NAME > /dev/null 2>&1; then
        log "Сайт доступен по HTTPS ✓"
    else
        error "Сайт недоступен по HTTPS"
        return 1
    fi
    
    # Проверка нового сертификата
    if command -v openssl &> /dev/null; then
        local cert_info=$(echo | openssl s_client -servername $DOMAIN_NAME -connect $DOMAIN_NAME:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            local not_after=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
            log "Новый сертификат действителен до: $not_after"
        fi
    fi
    
    return 0
}

# Принудительное обновление
force_renew() {
    log "Принудительное обновление SSL сертификата..."
    
    docker-compose -f docker-compose.prod.yml stop nginx
    docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
    docker-compose -f docker-compose.prod.yml start nginx
    
    log "Принудительное обновление завершено ✓"
}

# Настройка автоматического обновления
setup_auto_renewal() {
    log "Настройка автоматического обновления SSL..."
    
    # Создание скрипта для cron
    local script_path="$(pwd)/scripts/renew-ssl.sh"
    
    # Добавление в crontab (проверка каждые 2 месяца)
    (crontab -l 2>/dev/null | grep -v "renew-ssl.sh"; echo "0 2 1 */2 * $script_path") | crontab -
    
    log "Автоматическое обновление SSL настроено ✓"
    log "Cron задача: проверка каждые 2 месяца в 02:00"
}

# Основная функция
main() {
    case "${1:-check}" in
        "check")
            check_env
            if check_ssl_status; then
                renew_ssl
                verify_ssl
            else
                log "Обновление не требуется ✓"
            fi
            ;;
        "renew")
            check_env
            renew_ssl
            verify_ssl
            ;;
        "force")
            check_env
            force_renew
            verify_ssl
            ;;
        "setup-auto")
            setup_auto_renewal
            ;;
        "status")
            check_env
            check_ssl_status
            ;;
        *)
            echo "Использование: $0 [check|renew|force|setup-auto|status]"
            echo ""
            echo "Команды:"
            echo "  check      - Проверить и обновить если необходимо (по умолчанию)"
            echo "  renew      - Принудительно обновить сертификат"
            echo "  force      - Принудительно обновить даже если не истек"
            echo "  setup-auto - Настроить автоматическое обновление"
            echo "  status     - Показать статус сертификата"
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
