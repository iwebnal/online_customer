#!/usr/bin/env python3
"""
Тест функциональности запроса номера телефона в боте
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_phone_functionality():
    """Тестирует основную функциональность запроса номера телефона"""
    
    print("🧪 Тестирование функциональности запроса номера телефона...")
    
    try:
        # Импортируем необходимые модули
        from bot_service.bot.services.db import get_user_by_telegram_id, create_user, update_user_phone
        from bot_service.shared.database import get_db_session
        
        print("✅ Импорт модулей успешен")
        
        # Тест 1: Создание пользователя
        print("\n📝 Тест 1: Создание пользователя")
        test_telegram_id = "123456789"
        test_name = "Тестовый Пользователь"
        test_phone = "+79001234567"
        
        user = await create_user(
            telegram_id=test_telegram_id,
            name=test_name,
            phone=test_phone
        )
        
        if user and user.telegram_id == test_telegram_id:
            print(f"✅ Пользователь создан: {user.name} (ID: {user.id})")
        else:
            print("❌ Ошибка создания пользователя")
            return False
        
        # Тест 2: Получение пользователя
        print("\n🔍 Тест 2: Получение пользователя")
        retrieved_user = await get_user_by_telegram_id(test_telegram_id)
        
        if retrieved_user and retrieved_user.id == user.id:
            print(f"✅ Пользователь найден: {retrieved_user.name}")
        else:
            print("❌ Ошибка получения пользователя")
            return False
        
        # Тест 3: Обновление номера телефона
        print("\n📱 Тест 3: Обновление номера телефона")
        new_phone = "+79009876543"
        updated_user = await update_user_phone(test_telegram_id, new_phone)
        
        if updated_user and updated_user.phone == new_phone:
            print(f"✅ Номер телефона обновлен: {updated_user.phone}")
        else:
            print("❌ Ошибка обновления номера телефона")
            return False
        
        # Тест 4: Проверка обновления
        print("\n✅ Тест 4: Проверка обновления")
        final_user = await get_user_by_telegram_id(test_telegram_id)
        
        if final_user.phone == new_phone:
            print(f"✅ Проверка успешна: {final_user.phone}")
        else:
            print("❌ Ошибка проверки обновления")
            return False
        
        print("\n🎉 Все тесты прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """Тестирует подключение к базе данных"""
    
    print("🔌 Тестирование подключения к базе данных...")
    
    try:
        from bot_service.shared.database import get_db_session
        
        async with get_db_session() as session:
            # Простой запрос для проверки подключения
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            
            if value == 1:
                print("✅ Подключение к базе данных успешно")
                return True
            else:
                print("❌ Ошибка подключения к базе данных")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    
    print("🚀 Запуск тестов функциональности запроса номера телефона")
    print("=" * 60)
    
    # Тест подключения к БД
    if not await test_database_connection():
        print("\n❌ Тест подключения к БД не прошел. Проверьте настройки.")
        return
    
    # Основной тест функциональности
    if await test_phone_functionality():
        print("\n🎯 Функциональность запроса номера телефона работает корректно!")
    else:
        print("\n💥 Обнаружены проблемы в функциональности")
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено")

if __name__ == "__main__":
    # Запускаем тесты
    asyncio.run(main())
