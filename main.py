import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    PreCheckoutQuery,
    CallbackQuery
)

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067  # твой Telegram ID

bot = Bot(TOKEN)
dp = Dispatcher()

# подарки с ключами для выбора
gifts = {
    "bear": {"name": "🧸 Мишка", "price": 7},
    "giftbox": {"name": "🎁 Подарочная коробка", "price": 13},
    "ring": {"name": "💍 Обручальное кольцо", "price": 30},
    "diamond": {"name": "💎 Бриллиант", "price": 30},
    "heart": {"name": "❤️ Сердце", "price": 7},
    "flowers": {"name": "💐 Букет цветов", "price": 20},
    "rose": {"name": "🌹 Роза", "price": 13},
    "champagne": {"name": "🍾 Шампанское", "price": 20},
    "cup": {"name": "🏆 Кубок", "price": 30},
    "rocket": {"name": "🚀 Ракета", "price": 20},
}

sales = []

# промокоды
promo_codes = {}  # promo_code -> gift_key

# состояния админа для добавления подарков или промокодов
admin_states = {}

# стартовое меню
def start_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🎁 Подарки", callback_data="show_gifts")],
        [InlineKeyboardButton(text="🎫 Использовать промокод", callback_data="promo_code")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# клавиатура подарков
def gifts_keyboard():
    buttons = []
    for key, value in gifts.items():
        buttons.append([InlineKeyboardButton(text=f"{value['name']} — {value['price']} ⭐", callback_data=key)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# /start
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=start_keyboard())

# обработка кнопок
@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    # показать подарки
    if callback.data == "show_gifts":
        await callback.message.answer("Выберите подарок:", reply_markup=gifts_keyboard())
        await callback.answer()
        return

    # использовать промокод
    if callback.data == "promo_code":
        await callback.message.answer("Введите промокод:")
        await callback.answer()
        return

    # выбор подарка для оплаты
    if callback.data in gifts:
        gift = gifts[callback.data]
        prices = [LabeledPrice(label=gift["name"], amount=gift["price"])]
        await bot.send_invoice(
            chat_id=user_id,
            title=gift["name"],
            description=f"{gift['name']} за {gift['price']}⭐",
            payload=callback.data,
            provider_token="",  # вставь токен
            currency="XTR",
            prices=prices
        )
        await callback.answer()
        return

    # админка кнопки
    if user_id == ADMIN_ID:
        if callback.data == "view_sales":
            if not sales:
                await callback.message.answer("Продаж пока нет")
            else:
                text = "📊 Продажи:\n" + "\n".join(f"{s[0]} купил {s[1]} за {s[2]}⭐" for s in sales)
                await callback.message.answer(text)
        elif callback.data == "clear_sales":
            sales.clear()
            await callback.message.answer("✅ Список продаж очищен")
        elif callback.data == "gift_stats":
            stats = {}
            for _, name, _ in sales:
                stats[name] = stats.get(name, 0) + 1
            text = "📈 Статистика подарков:\n" + "\n".join(f"{k}: {v} шт." for k, v in stats.items())
            await callback.message.answer(text)
        elif callback.data == "add_gift":
            admin_states[user_id] = {"step": "name"}
            await callback.message.answer("Введите название нового подарка:")
        elif callback.data == "add_promo":
            admin_states[user_id] = {"step": "gift_select_for_promo"}
            await callback.message.answer("Введите ключ подарка для промокода (например bear, giftbox и т.д.):")
        await callback.answer()

# админка /admin
@dp.message(Command(commands=["admin"]))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Просмотр продаж", callback_data="view_sales")],
        [InlineKeyboardButton(text="🧹 Очистить продажи", callback_data="clear_sales")],
        [InlineKeyboardButton(text="📈 Статистика подарков", callback_data="gift_stats")],
        [InlineKeyboardButton(text="➕ Добавить подарок", callback_data="add_gift")],
        [InlineKeyboardButton(text="🎫 Создать промокод", callback_data="add_promo")]
    ])
    await message.answer("👑 Админ панель", reply_markup=keyboard)

# обработка сообщений
@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # обработка промокодов пользователем
    if text.upper() in promo_codes:
        gift_key = promo_codes[text.upper()]
        gift = gifts[gift_key]
        sales.append((user_id, gift["name"], 0))
        await message.answer(f"🎉 Промокод принят! Вы получили подарок: {gift['name']}")
        await bot.send_message(ADMIN_ID, f"🎫 Промокод использован\nПользователь: {user_id}\nПодарок: {gift['name']}")
        return

    # обработка шагов админа
    if user_id in admin_states:
        state = admin_states[user_id]
        step = state.get("step")

        if step == "name":
            state["name"] = text
            state["step"] = "price"
            await message.answer("Введите цену подарка (целое число):")
        elif step == "price":
            if not text.isdigit():
                await message.answer("Введите корректное число для цены:")
                return
            state["price"] = int(text)
            state["step"] = "gift_code"
            await message.answer("Введите код для подарка:")
        elif step == "gift_code":
            state["key"] = text.lower().replace(" ", "_")
            gifts[state["key"]] = {"name": state["name"], "price": state["price"]}
            del admin_states[user_id]
            await message.answer(f"✅ Подарок {state['name']} добавлен!")

        elif step == "gift_select_for_promo":
            if text not in gifts:
                await message.answer("Такого подарка нет. Введите ключ существующего подарка:")
                return
            state["gift_key"] = text
            state["step"] = "promo_code"
            await message.answer("Введите новый промокод для этого подарка:")
        elif step == "promo_code":
            code = text.upper()
            promo_codes[code] = state["gift_key"]
            del admin_states[user_id]
            await message.answer(f"✅ Промокод {code} для подарка {gifts[state['gift_key']]['name']} создан!")

# платежи
@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: types.Message):
    gift_id = message.successful_payment.invoice_payload
    gift = gifts[gift_id]
    sales.append((message.from_user.id, gift["name"], gift["price"]))
    await message.answer("❌ Ошибка оплаты, попробуйте ещё раз.")
    await bot.send_message(ADMIN_ID, f"💰 Новая покупка\nПользователь: {message.from_user.id}\nПодарок: {gift['name']}\nЦена: {gift['price']}⭐")

# запуск
async def main():
    await dp.start_polling(bot)

asyncio.run(main())
