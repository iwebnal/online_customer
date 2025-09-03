from aiogram.dispatcher.filters.state import State, StatesGroup

class PhoneRequestStates(StatesGroup):
    """Состояния для запроса номера телефона"""
    waiting_for_phone = State()
