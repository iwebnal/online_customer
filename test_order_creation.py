#!/usr/bin/env python3
"""
Тестовый скрипт для проверки создания заказов в базе данных
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(__file__))

from bot.services.db import (
    get_all_restaurants, 
    get_products_by_restaurant, 
    get_user_by_telegram_id, 
    create_user, 
    create_order
)

async def test_order_creation():
    """Тестирует создание заказа в базе данных"""
    
    print("🧪 Тестирование создания заказа...")
    
    # 1. Получаем список ресторанов
    restaurants = await get_all_restaurants()
    if not restaurants:
        print("❌ Нет ресторанов в базе данных")
        return
    
    restaurant = restaurants[0]
    print(f"✅ Найден ресторан: {restaurant.name} (ID: {restaurant.id})")
    
    # 2. Получаем продукты ресторана
    products = await get_products_by_restaurant(restaurant.id)
    if not products:
        print("❌ Нет продуктов в ресторане")
        return
    
    print(f"✅ Найдено продуктов: {len(products)}")
    
    # 3. Получаем или создаем тестового пользователя
    test_telegram_id = "123456789"
    user = await get_user_by_telegram_id(test_telegram_id)
    if not user:
        user = await create_user(telegram_id=test_telegram_id, name="Тестовый пользователь")
        print(f"✅ Создан новый пользователь: {user.name} (ID: {user.id})")
    else:
        print(f"✅ Найден пользователь: {user.name} (ID: {user.id})")
    
    # 4. Создаем тестовый заказ
    test_items = []
    total = 0
    
    for product in products[:2]:  # Берем первые 2 продукта
        price = product.discount_price or product.price
        test_items.append({
            'product_id': product.id,
            'quantity': 2,
            'price': product.price,
            'discount_price': product.discount_price
        })
        total += price * 2
    
    print(f"✅ Создаем заказ на сумму: {total}₽")
    print(f"✅ Количество позиций: {len(test_items)}")
    
    # 5. Создаем заказ
    try:
        order = await create_order(
            user_id=user.id,
            restaurant_id=restaurant.id,
            total=total,
            items=test_items
        )
        print(f"✅ Заказ успешно создан! ID заказа: {order.id}")
        print(f"✅ Статус заказа: {order.status}")
        print(f"✅ Сумма заказа: {order.total}₽")
        print(f"✅ Дата создания: {order.created_at}")
        
        # Выводим информацию о позициях заказа
        print("\n📋 Позиции заказа:")
        for item in order.items:
            print(f"  - {item.product.name} x{item.quantity} = {item.price}₽")
            if item.discount_price:
                print(f"    (со скидкой: {item.discount_price}₽)")
        
    except Exception as e:
        print(f"❌ Ошибка при создании заказа: {e}")
        return
    
    print("\n🎉 Тест завершен успешно!")

if __name__ == "__main__":
    asyncio.run(test_order_creation())
