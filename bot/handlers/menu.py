from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


from bot.services.db import get_products_by_category_name, get_all_categories, get_all_restaurants, \
    get_products_by_restaurant, get_user_by_telegram_id, create_user, create_order
from bot.utils.menu import send_main_menu

# Ключ для хранения корзины в FSMContext
CART_KEY = 'cart'
RESTAURANT_KEY = 'restaurant_id'
RESTAURANT_NAME = 'restaurant_name'
RESTAURANT_ADDRESS = 'restaurant_address'
CHOOSE_RESTAURANT_BTN = '🏢 Выбрать ресторан'
MENU_BTN = 'Наше меню'

CONFIRM_ORDER_BTN = '✅ Подтвердить заказ'
MAIN_MENU_BTN = '⬅️ В главное меню'  # ADDED

choose_restaurant_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
choose_restaurant_keyboard.add(KeyboardButton(CHOOSE_RESTAURANT_BTN))

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(KeyboardButton(MENU_BTN))


async def get_products_by_category(category_name):
    # TODO: заменить на реальный запрос к БД
    # Пример заглушки
    if 'Напитки' in category_name:
        return [
            {'name': 'Капучино1', 'size': '250 мл', 'price': 150},
            {'name': 'Американо1', 'size': '250 мл', 'price': 120},
        ]
    elif 'Завтраки' in category_name:
        return [
            {'name': 'Омлет с сыром1', 'size': '200 г', 'price': 250},
            {'name': 'Каша овсяная1', 'size': '300 г', 'price': 180},
        ]
    elif 'Десерты' in category_name:
        return [
            {'name': 'Чизкейк1', 'size': '120 г', 'price': 220},
            {'name': 'Эклер1', 'size': '80 г', 'price': 90},
        ]
    else:
        return []


def register_menu_handlers(dp: Dispatcher):
    @dp.message_handler(commands=['start'])
    async def start_handler(message: types.Message, state: FSMContext):
        await state.update_data({RESTAURANT_KEY: None, RESTAURANT_NAME: None, RESTAURANT_ADDRESS: None})
        # Сначала отправляем приветствие и акции без клавиатуры
        welcome_text = (
            'Добро пожаловать! 🎉\n'
            'Здесь вы можете выбрать и заказать что-то вкусненькое, узнать о скидках и оплатить свой заказ👇'
        )
        await message.answer(welcome_text, reply_markup=ReplyKeyboardRemove())
        sales_text = (
            '🎉 Акции и скидки на сегодня! 🎉\n\n'
            '📌 Скидка 20% на все десерты!\n'
            'Только сегодня сладости со скидкой. Побалуйте себя!\n'
            '⏳ Действует до 23:59.\n\n'
            '📌 Каждому заказу от 1500₽ — напиток в подарок!\n'
            'Выберите любой товар, наберите сумму от 1500₽ и получите любимый напиток бесплатно.\n'
            '☕ Выбор напитка уточняется после оформления заказа.\n\n'
            '📌 Сет "Завтрак для двоих" — за 799₽ вместо 990₽!\n'
            'Отличный вариант для приятного утра вдвоём.\n'
            '📦 В наличии ограниченное количество наборов!\n\n'
            '🔔 Не пропустите! Количество акционных товаров ограничено.'
        )
        await message.answer(sales_text, reply_markup=ReplyKeyboardRemove())
        # Затем только кнопка выбора ресторана
        await message.answer('Для начала работы выберите ресторан:', reply_markup=choose_restaurant_keyboard)

    @dp.message_handler(lambda m: m.text == CHOOSE_RESTAURANT_BTN)
    async def choose_restaurant(message: types.Message, state: FSMContext):
        restaurants = await get_all_restaurants()
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for r in restaurants:
            keyboard.add(f"{r.name} | {r.address}")
        await message.answer('Пожалуйста, выберите ресторан:', reply_markup=keyboard)

    @dp.message_handler(lambda m: '|' in m.text)
    async def select_restaurant(message: types.Message, state: FSMContext):
        name, address = [s.strip() for s in message.text.split('|', 1)]
        restaurants = await get_all_restaurants()
        for r in restaurants:
            if r.name == name and r.address == address:
                await state.update_data({RESTAURANT_KEY: r.id, RESTAURANT_NAME: r.name, RESTAURANT_ADDRESS: r.address})
                await message.answer(f'Вы выбрали ресторан: {r.name}\nАдрес: {r.address}', reply_markup=menu_keyboard)
                return
        await message.answer('Ресторан не найден. Пожалуйста, выберите из списка.',
                             reply_markup=choose_restaurant_keyboard)

    @dp.message_handler(lambda m: m.text == MENU_BTN)
    async def show_menu(message: types.Message, state: FSMContext):
        data = await state.get_data()
        if not data.get(RESTAURANT_KEY):
            await message.answer('Сначала выберите ресторан:', reply_markup=choose_restaurant_keyboard)
            return
        restaurant_id = data.get(RESTAURANT_KEY)
        products = await get_products_by_restaurant(restaurant_id)
        categories = set(p.category.name for p in products if p.category)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for cat in categories:
            keyboard.add(cat)
        keyboard.add('🛒 Оформить заказ')
        keyboard.add('⬅️ В главное меню')
        await message.answer('Выберите категорию:', reply_markup=keyboard)

    @dp.message_handler(lambda m: m.text not in [MENU_BTN, '⬅️ В главное меню', '🛒 Оформить заказ', '⬅️ К категориям',
                                                 CHOOSE_RESTAURANT_BTN] and '|' not in m.text)
    async def show_products_or_add_to_cart(message: types.Message, state: FSMContext):
        data = await state.get_data()
        restaurant_id = data.get(RESTAURANT_KEY)
        if not restaurant_id:
            await message.answer('Сначала выберите ресторан:', reply_markup=choose_restaurant_keyboard)
            return
        products = await get_products_by_restaurant(restaurant_id)
        filtered = [p for p in products if p.category and p.category.name == message.text]
        if filtered:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for product in filtered:
                keyboard.add(product.name)
            keyboard.add('⬅️ К категориям')
            await message.answer('Выберите продукт:', reply_markup=keyboard)
        else:
            async with state.proxy() as data:
                cart = data.get(CART_KEY, [])
                cart.append(message.text)
                data[CART_KEY] = cart
            await message.answer(f'Товар "{message.text}" добавлен в заказ!')

    @dp.message_handler(lambda m: m.text == '⬅️ К категориям')
    async def back_to_categories(message: types.Message, state: FSMContext):
        data = await state.get_data()
        restaurant_id = data.get(RESTAURANT_KEY)
        if not restaurant_id:
            await message.answer('Сначала выберите ресторан:', reply_markup=choose_restaurant_keyboard)
            return
        products = await get_products_by_restaurant(restaurant_id)
        categories = set(p.category.name for p in products if p.category)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for cat in categories:
            keyboard.add(cat)
        keyboard.add('🛒 Оформить заказ')
        keyboard.add('⬅️ В главное меню')
        await message.answer('Выберите категорию:', reply_markup=keyboard)

    @dp.message_handler(lambda m: m.text == '⬅️ В главное меню')
    async def back_to_main_menu(message: types.Message, state: FSMContext):
        await message.answer('Для продолжения выберите ресторан:', reply_markup=choose_restaurant_keyboard)

    @dp.message_handler(lambda m: m.text == '🛒 Оформить заказ')
    async def show_cart(message: types.Message, state: FSMContext):
        data = await state.get_data()
        restaurant_name = data.get(RESTAURANT_NAME)
        restaurant_address = data.get(RESTAURANT_ADDRESS)
        async with state.proxy() as data:
            cart = data.get(CART_KEY, [])
        if not cart:
            await message.answer('Ваша корзина пуста.')
            return
        from collections import Counter
        items = Counter(cart)
        text = f'Ваш заказ в ресторане {restaurant_name}\nАдрес: {restaurant_address}\n\n'
        total = 0
        products = await get_products_by_restaurant(data.get(RESTAURANT_KEY))
        product_map = {p.name: p for p in products}
        order_items = []
        for product_name, qty in items.items():
            product = product_map.get(product_name)
            if not product:
                price = 0
                discount_price = None
                product_id = None
            else:
                price = product.price
                discount_price = product.discount_price
                product_id = product.id
            price_to_show = discount_price or price
            text += f'{product_name} x{qty} — {price_to_show}₽\n'
            if isinstance(price_to_show, (int, float)):
                total += price_to_show * qty
            if product_id:
                order_items.append({
                    'product_id': product_id,
                    'quantity': qty,
                    'price': price,
                    'discount_price': discount_price
                })
        text += f'\nИтого: {total}₽'
        # Если нет order_items, не показываем кнопку подтверждения заказа
        if not order_items:
            await message.answer('Ваша корзина пуста.')
            return
        await message.answer(text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(CONFIRM_ORDER_BTN))
        # Сохраняем order_items и total во временное состояние для подтверждения
        await state.update_data(order_items=order_items, order_total=total)

    @dp.message_handler(lambda m: m.text == CONFIRM_ORDER_BTN)
    async def confirm_order(message: types.Message, state: FSMContext):
        data = await state.get_data()
        order_items = data.get('order_items', [])
        total = data.get('order_total', 0)
        restaurant_id = data.get(RESTAURANT_KEY)
        if not order_items or not restaurant_id:
            await message.answer('Ошибка: не удалось получить данные заказа. Попробуйте снова.',
                                 reply_markup=ReplyKeyboardRemove())
            return

        telegram_id = str(message.from_user.id)
        user = await get_user_by_telegram_id(telegram_id)
        if not user:
            user = await create_user(telegram_id=telegram_id, name=message.from_user.full_name)
        order = await create_order(user_id=user.id, restaurant_id=restaurant_id, total=total, items=order_items)

        # Очищаем корзину и временные данные заказа
        async with state.proxy() as data:
            data[CART_KEY] = []
            data['order_items'] = []
            data['order_total'] = 0
        await state.update_data(order_items=[], order_total=0)

        # Сначала убираем клавиатуру (визуально быстрее)
        await message.answer("Спасибо! Ваш заказ принят.", reply_markup=ReplyKeyboardRemove())

        # Затем отправляем сообщение о подтверждении заказа
        await message.answer(
            f'Ваш заказ №{order.id} успешно оформлен и передан в обработку!',
            reply_markup=ReplyKeyboardRemove()
        )

        # Переводим пользователя на начальный этап работы с ботом
        await start_handler(message, state)

    @dp.message_handler(lambda m: m.text == '⬅️ В главное меню')
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        # Здесь вызываем функцию показа главного меню
        await send_main_menu(message)
