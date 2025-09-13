#!/usr/bin/env python3
"""
Простой веб-сервер для обслуживания Telegram Mini App
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Настройки сервера
PORT = 3000
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Добавляем CORS заголовки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Обработка preflight запросов
        self.send_response(200)
        self.end_headers()

def main():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 Mini App сервер запущен на http://localhost:{PORT}")
        print(f"📁 Обслуживает файлы из: {DIRECTORY}")
        print("🛑 Нажмите Ctrl+C для остановки")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
            sys.exit(0)

if __name__ == "__main__":
    main()
