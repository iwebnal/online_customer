#!/usr/bin/env python3
"""
Mock API сервер для Mini App (заменяет админ-панель)
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Добавляем CORS заголовки
        self.send_cors_headers()
        
        if parsed_path.path == "/api/restaurants":
            self.send_restaurants()
        elif parsed_path.path == "/api/products":
            self.send_products()
        elif parsed_path.path == "/api/categories":
            self.send_categories()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        # Добавляем CORS заголовки
        self.send_cors_headers()
        
        if parsed_path.path == "/api/orders":
            self.create_order()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        # Обработка preflight запросов
        self.send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def send_cors_headers(self):
        """Отправка CORS заголовков"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
    
    def send_restaurants(self):
        """Отправка данных о ресторанах"""
        restaurants = {
            "restaurants": [
                {
                    "id": 1,
                    "name": "You Coffee (Nalchik)",
                    "address": "г. Нальчик, ул. Кабардинская, 25"
                },
                {
                    "id": 2,
                    "name": "Coffee House (Moscow)",
                    "address": "г. Москва, ул. Арбат, 15"
                }
            ]
        }
        self.end_headers()
        self.wfile.write(json.dumps(restaurants, ensure_ascii=False).encode('utf-8'))
    
    def send_products(self):
        """Отправка данных о товарах"""
        products = {
            "products": [
                {
                    "id": 1,
                    "name": "Американо",
                    "description": "Классический черный кофе 250 мл",
                    "price": 150,
                    "discount_price": None,
                    "size": "250 мл",
                    "photo": "",
                    "is_available": True,
                    "stock": 100,
                    "category": {"id": 1, "name": "Напитки"},
                    "restaurant_id": 1
                },
                {
                    "id": 2,
                    "name": "Капучино",
                    "description": "Кофе с молоком и пенкой 300 мл",
                    "price": 210,
                    "discount_price": 190,
                    "size": "300 мл",
                    "photo": "",
                    "is_available": True,
                    "stock": 80,
                    "category": {"id": 1, "name": "Напитки"},
                    "restaurant_id": 1
                },
                {
                    "id": 3,
                    "name": "Латте",
                    "description": "Нежный латте с молоком 300 мл",
                    "price": 230,
                    "discount_price": None,
                    "size": "300 мл",
                    "photo": "",
                    "is_available": True,
                    "stock": 60,
                    "category": {"id": 1, "name": "Напитки"},
                    "restaurant_id": 1
                },
                {
                    "id": 4,
                    "name": "Круассан",
                    "description": "Сливочный круассан, свежая выпечка",
                    "price": 180,
                    "discount_price": None,
                    "size": "1 шт",
                    "photo": "",
                    "is_available": True,
                    "stock": 40,
                    "category": {"id": 2, "name": "Выпечка"},
                    "restaurant_id": 1
                },
                {
                    "id": 5,
                    "name": "Чизкейк",
                    "description": "Классический Нью-Йорк чизкейк",
                    "price": 260,
                    "discount_price": 240,
                    "size": "1 порция",
                    "photo": "",
                    "is_available": True,
                    "stock": 20,
                    "category": {"id": 3, "name": "Десерты"},
                    "restaurant_id": 1
                }
            ]
        }
        self.end_headers()
        self.wfile.write(json.dumps(products, ensure_ascii=False).encode('utf-8'))
    
    def send_categories(self):
        """Отправка данных о категориях"""
        categories = {
            "categories": [
                {"id": 1, "name": "Напитки", "restaurant_id": 1},
                {"id": 2, "name": "Выпечка", "restaurant_id": 1},
                {"id": 3, "name": "Десерты", "restaurant_id": 1}
            ]
        }
        self.end_headers()
        self.wfile.write(json.dumps(categories, ensure_ascii=False).encode('utf-8'))
    
    def create_order(self):
        """Создание заказа"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            order_data = json.loads(post_data.decode('utf-8'))
            print(f"Получен заказ: {order_data}")
            
            response = {
                "status": "success",
                "message": "Заказ успешно создан",
                "order_id": 12345
            }
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Ошибка создания заказа: {str(e)}"
            }
        
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Отключаем логирование для чистоты вывода"""
        pass

def main():
    port = 8000
    server = HTTPServer(('localhost', port), MockAPIHandler)
    print(f"🚀 Mock API сервер запущен на http://localhost:{port}")
    print("📋 Доступные эндпоинты:")
    print("   GET  /api/restaurants")
    print("   GET  /api/products")
    print("   GET  /api/categories")
    print("   POST /api/orders")
    print("🛑 Нажмите Ctrl+C для остановки")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Mock API сервер остановлен")
        server.shutdown()

if __name__ == "__main__":
    main()
