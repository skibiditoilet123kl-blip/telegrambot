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
ADMIN_ID = 5349252067  # вставь свой Telegram ID

bot = Bot(TOKEN)
dp = Dispatcher()

# подарки с кодами
gifts = {
    "bear": {"name": "🧸 Мишка", "price": 15, "code": "BEAR2026"},
    "giftbox": {"name": "🎁 Подарочная коробка", "price": 25, "code": "GIFTBOX2026"},
    "ring": {"name": "💍 Обручальное кольцо", "price": 100, "code": "RING2026"},
    "diamond": {"name": "💎 Бриллиант", "price": 100, "code": "DIAMOND2026"},
}

sales = []
promo_codes = {}  # словарь промокодов: код → ключ подарка

admin_states = {}  # состояние админа для добавления подарков/промо

# Клавиатура стартового меню
def start_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🎁 Подарки", callback_data="show_gifts")],
        [InlineKeyboardButton(text="🎫 Использовать промокод", callback_data="promo_code")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура подарков
def gifts_keyboard():
    buttons = []
    for key, value in gifts.items():
        name, price = value["name"], value["price"]
        buttons.append([InlineKeyboardButton(text=f"{name} — {price} ⭐", callback_data=key)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# старт
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=start_keyboard())


# обработка кнопок стартового меню и подарков
@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    if callback.data == "show_gifts":
        await callback.message.answer("Выберите подарок:", reply_markup=gifts_keyboard())
        await callback.answer()
        return
    elif callback.data == "promo_code":
        await callback.message.answer("Введите промокод:")
        await callback.answer()
        return

    # обработка выбора подарка для оплаты
    if callback.data in gifts:
        gift_id = callback.data
        gift = gifts[gift_id]
        prices = [LabeledPrice(label=gift["name"], amount=gift["price"])]
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=gift["name"],
            description=f"{gift['name']} за {gift['price']} звёзд",
            payload=gift_id,
            provider_token="",  # вставь свой токен платежного провайдера
            currency="XTR",
            prices=prices
        )
        await callback.answer()
        return

    # админские кнопки
    if callback.from_user.id == ADMIN_ID:
        state = admin_states.get(callback.from_user.id, {})
        if callback.data == "view_sales":
            if not sales:
                await callback.message.answer("Продаж пока нет")
            else:
                text = "📊 Продажи:\n\n" + "\n".join(f"{s[0]} купил {s[1]} за {s[2]}⭐" for s in sales)
                await callback.message.answer(text)
        elif callback.data == "clear_sales":
            sales.clear()
            await callback.message.answer("✅ Список продаж очищен")
        elif callback.data == "gift_stats":
            if not sales:
                await callback.message.answer("Продаж пока нет")
            else:
                stats = {}
                for _, name, _ in sales:
                    stats[name] = stats.get(name, 0) + 1
                text = "📈 Статистика подарков:\n\n" + "\n".join(f"{k}: {v} шт." for k, v in stats.items())
                await callback.message.answer(text)
        elif callback.data == "add_gift":
            admin_states[callback.from_user.id] = {"step": "name"}
            await callback.message.answer("Введите название нового подарка:")
        elif callback.data == "add_promo":
            admin_states[callback.from_user.id] = {"step": "promo_gift"}
            await callback.message.answer("Введите ключ подарка для промокода:")
        await callback.answer()


# админка
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


# обработка сообщений пользователей и админа (промокоды и добавление подарков)
@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id

    # обработка промокодов пользователем
    if message.text.strip().upper() in promo_codes:
        key = promo_codes[message.text.strip().upper()]
        gift = gifts[key]
        sales.append((user_id, gift["name"], 0))
        await message.answer(f"🎉 Промокод принят! Вы получили подарок: {gift['name']}")
        await bot.send_message(ADMIN_ID, f"🎫 Промокод использован\nПользователь: {user_id}\nПодарок: {gift['name']}")
        return
    elif message.text.startswith("/"):
        return  # команды не обрабатываем здесь

    # обработка шагов админа
    if user_id in admin_states:
        state = admin_states[user_id]
        step = state.get("step")

        if step == "name":
            state["name"] = message.text
            state["step"] = "price"
            await message.answer("Введите цену подарка (целое число):")
        elif step == "price":
            if not message.text.isdigit():
                await message.answer("Введите корректное число для цены:")
                return
            state["price"] = int(message.text)
            state["step"] = "code"
            await message.answer("Введите код для подарка:")
        elif step == "code":
            state["code"] = message.text.strip().upper()
            key = state["name"].lower().replace(" ", "_")
            gifts[key] = {"name": state["name"], "price": state["price"], "code": state["code"]}
            del admin_states[user_id]
            await message.answer(f"✅ Подарок {state['name']} добавлен!")

        elif step == "promo_gift":
            gift_key = message.text.strip().lower().replace(" ", "_")
            if gift_key not in gifts:
                await message.answer("Такого подарка нет. Введите ключ существующего подарка:")
                return
            state["gift_key"] = gift_key
            state["step"] = "promo_code"
            await message.answer("Введите промокод для этого подарка:")
        elif step == "promo_code":
            code = message.text.strip().upper()
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
    await bot.send_message(ADMIN_ID,
        f"💰 Новая покупка\nПользователь: {message.from_user.id}\nПодарок: {gift['name']}\nЦена: {gift['price']}⭐")


async def main():
    await dp.start_polling(bot)

asyncio.run(main())
