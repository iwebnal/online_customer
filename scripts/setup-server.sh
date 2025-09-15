#!/bin/bash

# Скрипт для первоначальной настройки сервера
# Использование: ./scripts/setup-server.sh

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

# Обновление системы
update_system() {
    log "Обновление системы..."
    sudo apt update && sudo apt upgrade -y
    log "Система обновлена ✓"
}

# Установка Docker
install_docker() {
    log "Установка Docker..."
    
    if command -v docker &> /dev/null; then
        log "Docker уже установлен ✓"
        return
    fi
    
    # Установка зависимостей
    sudo apt-get update
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Добавление официального GPG ключа Docker
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Добавление репозитория Docker
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Установка Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Добавление пользователя в группу docker
    sudo usermod -aG docker $USER
    
    log "Docker установлен ✓"
    warn "Перезайдите в систему для применения изменений группы docker"
}

# Установка Docker Compose
install_docker_compose() {
    log "Установка Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log "Docker Compose уже установлен ✓"
        return
    fi
    
    # Установка Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log "Docker Compose установлен ✓"
}

# Настройка файрвола
setup_firewall() {
    log "Настройка файрвола..."
    
    # Установка ufw если не установлен
    if ! command -v ufw &> /dev/null; then
        sudo apt install -y ufw
    fi
    
    # Настройка правил
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Включение файрвола
    sudo ufw --force enable
    
    log "Файрвол настроен ✓"
}

# Установка дополнительных утилит
install_utilities() {
    log "Установка дополнительных утилит..."
    
    sudo apt install -y \
        curl \
        wget \
        git \
        htop \
        nano \
        vim \
        unzip \
        certbot \
        nginx-common
    
    log "Утилиты установлены ✓"
}

# Создание пользователя для приложения
create_app_user() {
    log "Создание пользователя для приложения..."
    
    if id "app" &>/dev/null; then
        log "Пользователь app уже существует ✓"
        return
    fi
    
    sudo useradd -m -s /bin/bash app
    sudo usermod -aG docker app
    sudo usermod -aG sudo app
    
    log "Пользователь app создан ✓"
    warn "Установите пароль для пользователя app: sudo passwd app"
}

# Настройка SSH
setup_ssh() {
    log "Настройка SSH..."
    
    # Создание резервной копии конфигурации
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Настройка SSH
    sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    
    # Перезапуск SSH
    sudo systemctl restart sshd
    
    log "SSH настроен ✓"
    warn "Убедитесь, что у вас настроен SSH ключ перед отключением паролей!"
}

# Настройка автоматических обновлений безопасности
setup_auto_updates() {
    log "Настройка автоматических обновлений безопасности..."
    
    sudo apt install -y unattended-upgrades
    
    # Настройка конфигурации
    echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades
    echo 'Unattended-Upgrade::Remove-Unused-Dependencies "true";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades
    
    # Включение автоматических обновлений
    echo 'APT::Periodic::Update-Package-Lists "1";' | sudo tee /etc/apt/apt.conf.d/20auto-upgrades
    echo 'APT::Periodic::Unattended-Upgrade "1";' | sudo tee -a /etc/apt/apt.conf.d/20auto-upgrades
    
    log "Автоматические обновления настроены ✓"
}

# Создание директории для проекта
create_project_directory() {
    log "Создание директории для проекта..."
    
    sudo mkdir -p /opt/online_customer
    sudo chown app:app /opt/online_customer
    
    log "Директория проекта создана ✓"
}

# Основная функция
main() {
    log "Начинаем настройку сервера..."
    
    update_system
    install_docker
    install_docker_compose
    setup_firewall
    install_utilities
    create_app_user
#    setup_ssh
    setup_auto_updates
    create_project_directory
    
    log "Настройка сервера завершена! 🎉"
    echo ""
    echo "Следующие шаги:"
    echo "1. Перезайдите в систему для применения изменений группы docker"
    echo "2. Скопируйте проект в /opt/online_customer"
    echo "3. Запустите ./scripts/deploy-production.sh"
    echo ""
    echo "Важные замечания:"
    echo "- Убедитесь, что у вас настроен SSH ключ"
    echo "- Установите пароль для пользователя app: sudo passwd app"
    echo "- Проверьте настройки файрвола: sudo ufw status"
}

# Запуск
main "$@"
