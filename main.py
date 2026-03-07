import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher()

# подарки
gifts = {
    "bear": {"name": "🧸 Мишка", "price": 15},
    "giftbox": {"name": "🎁 Подарочная коробка", "price": 25},
    "ring": {"name": "💍 Обручальное кольцо", "price": 100},
    "diamond": {"name": "💎 Бриллиант", "price": 100},
    "heart": {"name": "❤️ Сердце", "price": 15},
    "flowers": {"name": "💐 Букет цветов", "price": 50},
    "rose": {"name": "🌹 Роза", "price": 25},
    "champagne": {"name": "🍾 Шампанское", "price": 50},
    "cup": {"name": "🏆 Кубок", "price": 100},
    "rocket": {"name": "🚀 Ракета", "price": 50},
}

sales = []
promo_codes = {}  # promo_code -> {"gift_key": str, "uses_left": int}
user_states = {}  # для пользователя
admin_states = {}  # для админа

# стартовое меню
def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🎁 Подарки", callback_data="show_gifts")],
        [InlineKeyboardButton("🎫 Промокод", callback_data="promo_code")]
    ])

def gifts_keyboard():
    buttons = [[InlineKeyboardButton(f"{v['name']} — {v['price']} ⭐", callback_data=f"select_{k}")] for k,v in gifts.items()]
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def promo_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")]])

# /start
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=start_keyboard())

# обработка callback
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    if data == "back_to_start":
        await callback.message.edit_text("Выберите действие:", reply_markup=start_keyboard())
        await callback.answer()
        return

    if data == "show_gifts":
        await callback.message.edit_text("Выберите подарок:", reply_markup=gifts_keyboard())
        await callback.answer()
        return

    if data == "promo_code":
        await callback.message.edit_text("Введите промокод:", reply_markup=promo_keyboard())
        await callback.answer()
        return

    if data.startswith("select_"):
        gift_key = data.replace("select_", "")
        user_states[user_id] = {"gift_key": gift_key, "step": "username"}
        await callback.message.edit_text(f"Введите @username получателя подарка {gifts[gift_key]['name']}:")
        await callback.answer()
        return

    # админка
    if user_id == ADMIN_ID:
        state = admin_states.get(user_id, {})
        if data == "add_promo":
            admin_states[user_id] = {"step": "gift_select_for_promo"}
            await callback.message.answer("Введите ключ подарка для промокода:")
        await callback.answer()

# обработка сообщений
@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # использование промокода
    if text.upper() in promo_codes:
        promo = promo_codes[text.upper()]
        if promo["uses_left"] > 0:
            gift = gifts[promo["gift_key"]]
            sales.append((user_id, gift['name'], user_id, 0))
            promo["uses_left"] -= 1
            await message.answer(f"🎉 Промокод принят! Вы получили подарок: {gift['name']}")
            await bot.send_message(ADMIN_ID, f"🎫 Промокод использован\nПользователь: {user_id}\nПодарок: {gift['name']}\nОсталось использований: {promo['uses_left']}")
            return
        else:
            await message.answer("❌ Промокод недействителен или уже использован.")
            return
    elif text.upper() not in promo_codes and text.upper() != "":
        # если промокод введён неверно
        if user_id not in user_states or user_states[user_id].get("step") != "username":
            await message.answer("❌ Промокод недействителен или уже использован.")
            return

    # шаг пользователя: ввод username
    if user_id in user_states:
        state = user_states[user_id]
        if state.get("step") == "username":
            state["receiver"] = text
            gift_key = state["gift_key"]
            gift = gifts[gift_key]
            sales.append((user_id, gift['name'], state['receiver'], gift['price']))
            await message.answer(f"🎉 Подарок {gift['name']} будет отправлен пользователю {state['receiver']}.")
            await bot.send_message(ADMIN_ID, f"💰 Новый подарок\nОт: {user_id}\nПодарок: {gift['name']}\nПолучатель: {state['receiver']}\nЦена: {gift['price']}⭐")
            del user_states[user_id]
            return

    # шаги админа при создании промокода
    if user_id in admin_states:
        state = admin_states[user_id]
        step = state.get("step")
        if step == "gift_select_for_promo":
            if text not in gifts:
                await message.answer("Такого подарка нет. Введите ключ существующего подарка:")
                return
            state["gift_key"] = text
            state["step"] = "promo_code"
            await message.answer("Введите промокод:")
        elif step == "promo_code":
            state["code"] = text.upper()
            state["step"] = "promo_uses"
            await message.answer("Введите количество использований промокода (целое число):")
        elif step == "promo_uses":
            if not text.isdigit():
                await message.answer("Введите корректное число использований:")
                return
            uses = int(text)
            promo_codes[state["code"]] = {"gift_key": state["gift_key"], "uses_left": uses}
            del admin_states[user_id]
            await message.answer(f"✅ Промокод {state['code']} для подарка {gifts[state['gift_key']]['name']} создан! Количество использований: {uses}")
