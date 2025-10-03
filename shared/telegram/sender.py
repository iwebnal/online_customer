"""
Модуль для отправки уведомлений в Telegram
"""
import os
import asyncio
from typing import Optional, Dict, Any
import logging

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    Bot = None
    TelegramError = Exception

# Загружаем переменные окружения из .env файла (если он существует)
try:
    from dotenv import load_dotenv
    # Загружаем .env только если файл существует
    if os.path.exists('.env'):
        load_dotenv()
except ImportError:
    pass  # dotenv не установлен, используем системные переменные

logger = logging.getLogger(__name__)


class TelegramSender:
    """Класс для отправки сообщений в Telegram"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Инициализация отправителя
        
        Args:
            bot_token: Токен Telegram бота
            chat_id: ID чата для отправки сообщений
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '-1003068821769')
        self.bot = None
        self.initialization_error = None
        
        # Расширенная диагностика для отладки
        logger.info(f"TELEGRAM_BOT_TOKEN: {'установлен' if self.bot_token else 'НЕ установлен'}")
        logger.info(f"TELEGRAM_CHAT_ID: {self.chat_id}")
        logger.info(f"Telegram библиотека: {'доступна' if Bot else 'НЕ доступна'}")
        
        # Дополнительная информация для Docker окружения
        if os.path.exists('/.dockerenv'):
            logger.info("Запуск в Docker контейнере обнаружен")
        
        if self.bot_token and Bot:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram Bot инициализирован успешно")
            except Exception as e:
                logger.error(f"Ошибка инициализации Telegram бота: {e}")
                self.initialization_error = str(e)
                self.bot = None
        else:
            if not self.bot_token:
                logger.warning("Telegram Bot не инициализирован: отсутствует TELEGRAM_BOT_TOKEN")
                self.initialization_error = "Отсутствует TELEGRAM_BOT_TOKEN"
            if not Bot:
                logger.warning("Telegram Bot не инициализирован: библиотека python-telegram-bot не установлена")
                self.initialization_error = "Библиотека python-telegram-bot не установлена"
    
    def is_initialized(self) -> bool:
        """Проверяет, инициализирован ли бот"""
        return self.bot is not None
    
    def get_initialization_error(self) -> Optional[str]:
        """Возвращает ошибку инициализации, если есть"""
        return self.initialization_error
    
    async def send_order_notification(self, order_data: Dict[str, Any]) -> bool:
        """
        Отправляет уведомление о новом заказе в Telegram
        
        Args:
            order_data: Данные заказа
            
        Returns:
            bool: True если сообщение отправлено успешно, False в противном случае
        """
        if not self.bot:
            error_msg = self.get_initialization_error() or "Telegram Bot не инициализирован"
            logger.warning(f"Telegram Bot не инициализирован: {error_msg}")
            return False
        
        try:
            # Формируем сообщение о заказе
            message = self._format_order_message(order_data)
            logger.info(f"Отправляем сообщение в чат {self.chat_id} для заказа {order_data.get('order_id', 'unknown')}")
            
            # Отправляем сообщение с таймаутом
            await asyncio.wait_for(
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML'
                ),
                timeout=30.0  # 30 секунд таймаут
            )
            
            logger.info(f"✅ Уведомление о заказе отправлено в Telegram: {order_data.get('order_id', 'unknown')}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ Таймаут при отправке сообщения в Telegram для заказа {order_data.get('order_id', 'unknown')}")
            return False
        except TelegramError as e:
            logger.error(f"❌ Ошибка отправки сообщения в Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"💥 Неожиданная ошибка при отправке в Telegram: {e}")
            return False
    
    def _format_order_message(self, order_data: Dict[str, Any]) -> str:
        """
        Форматирует сообщение о заказе
        
        Args:
            order_data: Данные заказа
            
        Returns:
            str: Отформатированное сообщение
        """
        # Получаем информацию о пользователе
        user_info = ""
        if order_data.get('user'):
            user = order_data['user']
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            username = user.get('username', '')
            if username:
                user_info = f"👤 <b>Клиент:</b> {name} (@{username})\n"
            else:
                user_info = f"👤 <b>Клиент:</b> {name}\n"
        else:
            user_info = "👤 <b>Клиент:</b> Анонимный заказ\n"
        
        # Получаем адрес
        address = order_data.get('address', 'Не указан')
        
        # Формируем список товаров
        items_text = ""
        if order_data.get('order'):
            for item in order_data['order']:
                items_text += f"• {item.get('name', 'Неизвестный товар')} x{item.get('qty', 1)} - {item.get('price', 0)}₽\n"
        
        # Общая сумма
        total = order_data.get('totalSum', 0)
        
        # ID заказа
        order_id = order_data.get('order_id', 'Неизвестно')
        
        # Время заказа
        timestamp = order_data.get('timestamp', '')
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%d.%m.%Y %H:%M')
            except:
                time_str = timestamp
        else:
            time_str = "Неизвестно"
        
        message = f"""
🛒 <b>НОВЫЙ ЗАКАЗ #{order_id}</b>

{user_info}
📍 <b>Адрес:</b> {address}
🕐 <b>Время:</b> {time_str}

<b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {total}₽

<i>Заказ создан через Telegram Mini App</i>
        """.strip()
        
        return message
    
    async def send_test_message(self) -> bool:
        """
        Отправляет тестовое сообщение для проверки работы бота
        
        Returns:
            bool: True если сообщение отправлено успешно
        """
        if not self.bot:
            error_msg = self.get_initialization_error() or "Telegram Bot не инициализирован"
            logger.warning(f"Telegram Bot не инициализирован: {error_msg}")
            return False
        
        try:
            test_message = "🤖 <b>Тестовое сообщение</b>\n\nTelegram бот для уведомлений о заказах работает корректно!\n\n🕐 Время: " + str(asyncio.get_event_loop().time())
            
            await asyncio.wait_for(
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=test_message,
                    parse_mode='HTML'
                ),
                timeout=30.0
            )
            logger.info("✅ Тестовое сообщение отправлено успешно")
            return True
        except asyncio.TimeoutError:
            logger.error("⏰ Таймаут при отправке тестового сообщения")
            return False
        except TelegramError as e:
            logger.error(f"❌ Ошибка отправки тестового сообщения: {e}")
            return False
        except Exception as e:
            logger.error(f"💥 Неожиданная ошибка при отправке тестового сообщения: {e}")
            return False


# Глобальный экземпляр отправителя
_telegram_sender = None


def get_telegram_sender() -> TelegramSender:
    """Получает глобальный экземпляр Telegram отправителя"""
    global _telegram_sender
    if _telegram_sender is None:
        _telegram_sender = TelegramSender()
    return _telegram_sender


async def send_order_to_telegram(order_data: Dict[str, Any]) -> bool:
    """
    Удобная функция для отправки заказа в Telegram
    
    Args:
        order_data: Данные заказа
        
    Returns:
        bool: True если сообщение отправлено успешно
    """
    sender = get_telegram_sender()
    return await sender.send_order_notification(order_data)
