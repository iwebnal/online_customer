// JavaScript для админ-панели

document.addEventListener('DOMContentLoaded', function() {
    // Загружаем статистику на главной странице
    if (document.getElementById('products-count')) {
        loadDashboardStats();
    }
    
    // Инициализируем тултипы Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Загрузка статистики для дашборда
async function loadDashboardStats() {
    try {
        // Загружаем количество товаров
        const productsResponse = await fetch('/admin/products');
        const productsData = await productsResponse.json();
        document.getElementById('products-count').textContent = productsData.products?.length || 0;
        
        // Загружаем количество заказов
        const ordersResponse = await fetch('/admin/orders');
        const ordersData = await ordersResponse.json();
        document.getElementById('orders-count').textContent = ordersData.orders?.length || 0;
        
        // Загружаем количество скидок
        const discountsResponse = await fetch('/admin/discounts');
        const discountsData = await discountsResponse.json();
        document.getElementById('discounts-count').textContent = discountsData.discounts?.length || 0;
        
        // Загружаем последние заказы
        loadRecentOrders();
        
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// Загрузка последних заказов
async function loadRecentOrders() {
    try {
        const response = await fetch('/admin/orders');
        const data = await response.json();
        const recentOrders = data.orders?.slice(0, 5) || [];
        
        const container = document.getElementById('recent-orders');
        if (recentOrders.length === 0) {
            container.innerHTML = '<p class="text-muted">Нет заказов</p>';
            return;
        }
        
        let html = '<div class="list-group list-group-flush">';
        recentOrders.forEach(order => {
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>Заказ #${order.id}</strong>
                        <br>
                        <small class="text-muted">${order.user}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-primary">${order.total}₽</span>
                        <br>
                        <small class="text-muted">${order.status}</small>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
        document.getElementById('recent-orders').innerHTML = 
            '<p class="text-danger">Ошибка загрузки данных</p>';
    }
}

// Функция для подтверждения удаления
function confirmDelete(message = 'Вы уверены, что хотите удалить этот элемент?') {
    return confirm(message);
}

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
} 