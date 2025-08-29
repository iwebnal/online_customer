import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/online_customer')
    
    # Admin Panel
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this-in-production')
    
    # Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    ADMIN_PORT = int(os.getenv('ADMIN_PORT', 8000))
    BOT_PORT = int(os.getenv('BOT_PORT', 8001))

settings = Settings()
