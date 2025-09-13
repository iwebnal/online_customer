#!/usr/bin/env python3
"""
Утилита для остановки процессов на портах 8000 и 3000
"""

import subprocess
import sys
import os

def kill_port(port):
    """Остановка процесса на указанном порту"""
    try:
        # Находим процесс на порту
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🛑 Останавливаем процесс {pid} на порту {port}")
                    subprocess.run(['kill', pid], check=False)
                    print(f"✅ Процесс {pid} остановлен")
            return True
        else:
            print(f"ℹ️  Нет процессов на порту {port}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при остановке процесса на порту {port}: {e}")
        return False

def main():
    print("🛑 Остановка процессов на портах")
    print("=" * 40)
    
    ports = [8000, 3000]  # Порты админ-панели и Mini App
    
    for port in ports:
        print(f"\n🔍 Проверка порта {port}...")
        kill_port(port)
    
    print("\n✅ Проверка завершена")
    print("💡 Теперь можно запустить: python start_all.py")

if __name__ == "__main__":
    main()
