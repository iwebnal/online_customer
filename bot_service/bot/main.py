import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers.menu import register_menu_handlers
from utils.menu import send_main_menu, menu_keyboard

# Загружаем переменные окружения из .env файла
load_dotenv()

# Импортируем настройки после загрузки .env
from shared.config import settings

API_TOKEN = settings.BOT_TOKEN

if not API_TOKEN:
    raise ValueError('BOT_TOKEN is not set. Please add it to your .env file or environment variables.')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# УДАЛЁН обработчик /start, чтобы не было конфликта
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     await send_main_menu(message)

register_menu_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
