#!/usr/bin/env python3
"""
Скрипт для проверки статуса системы
"""

import requests
import sys
from pathlib import Path

def check_service(url, name):
    """Проверка доступности сервиса"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: Доступен ({url})")
            return True
        else:
            print(f"❌ {name}: Ошибка {response.status_code} ({url})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Недоступен ({url})")
        return False
    except Exception as e:
        print(f"❌ {name}: Ошибка - {e}")
        return False

def check_api_endpoints():
    """Проверка API эндпоинтов"""
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/restaurants",
        "/api/products", 
        "/api/categories"
    ]
    
    print("\n🔍 Проверка API эндпоинтов:")
    all_working = True
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'restaurants' in data:
                    print(f"   ✅ {endpoint}: {len(data['restaurants'])} ресторанов")
                elif 'products' in data:
                    print(f"   ✅ {endpoint}: {len(data['products'])} товаров")
                elif 'categories' in data:
                    print(f"   ✅ {endpoint}: {len(data['categories'])} категорий")
            else:
                print(f"   ❌ {endpoint}: Ошибка {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
            all_working = False
    
    return all_working

def main():
    print("🎯 Проверка статуса системы Telegram Mini App")
    print("=" * 50)
    
    # Проверяем сервисы
    admin_ok = check_service("http://localhost:8000", "Админ-панель")
    mini_app_ok = check_service("http://localhost:3000", "Mini App")
    
    # Проверяем API если админ-панель доступна
    api_ok = False
    if admin_ok:
        api_ok = check_api_endpoints()
    
    print("\n📊 Итоговый статус:")
    print(f"   Админ-панель: {'✅ Работает' if admin_ok else '❌ Не работает'}")
    print(f"   Mini App: {'✅ Работает' if mini_app_ok else '❌ Не работает'}")
    print(f"   API: {'✅ Работает' if api_ok else '❌ Не работает'}")
    
    if admin_ok and mini_app_ok and api_ok:
        print("\n🎉 Все системы работают нормально!")
        print("   📱 Mini App: http://localhost:3000")
        print("   🖥️  Админ-панель: http://localhost:8000")
        return 0
    else:
        print("\n⚠️  Некоторые сервисы не работают")
        print("   Запустите: python start_all.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
