import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher()

# --- ДАННЫЕ ---
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

sales = []  # (отправитель, подарок, получатель, цена)
promo_codes = {}  # {"PROMO": {"gift_key": str, "uses_left": int}}
user_states = {}  # состояния пользователей
admin_states = {}  # состояния админа

# --- КЛАВИАТУРЫ ---
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

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📊 Продажи", callback_data="view_sales")],
        [InlineKeyboardButton("📈 Статистика подарков", callback_data="gift_stats")],
        [InlineKeyboardButton("➕ Добавить подарок", callback_data="add_gift")],
        [InlineKeyboardButton("🎫 Создать промокод", callback_data="add_promo")],
        [InlineKeyboardButton("🎟 Просмотр промокодов", callback_data="view_promos")]
    ])

# --- СТАРТ ---
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=start_keyboard())

@dp.message(Command(commands=["admin"]))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("👑 Админ панель", reply_markup=admin_keyboard())

# --- CALLBACK ---
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

    # --- Админка ---
    if user_id == ADMIN_ID:
        state = admin_states.get(user_id, {})
        if data == "view_sales":
            if not sales:
                await callback.message.answer("Продаж пока нет")
            else:
                text = "📊 Продажи:\n" + "\n".join(f"{s[0]} купил {s[1]} для {s[2]} за {s[3]}⭐" for s in sales)
                await callback.message.answer(text)
        elif data == "gift_stats":
            stats = {}
            for _, gift_name, _, _ in sales:
                stats[gift_name] = stats.get(gift_name,0)+1
            text = "📈 Статистика подарков:\n" + "\n".join(f"{k}: {v} шт." for k,v in stats.items())
            await callback.message.answer(text)
        elif data == "add_gift":
            admin_states[user_id] = {"step":"name"}
            await callback.message.answer("Введите название нового подарка:")
        elif data == "add_promo":
            admin_states[user_id] = {"step":"gift_select_for_promo"}
            await callback.message.answer("Введите ключ подарка для промокода:")
        elif data == "view_promos":
            if not promo_codes:
                await callback.message.answer("Промокодов пока нет")
            else:
                text = "🎟 Промокоды:\n"
                for code, info in promo_codes.items():
                    gift = gifts[info["gift_key"]]["name"]
                    uses = info["uses_left"]
                    text += f"{code}: {gift}, оставшиеся использования: {uses}\n"
                await callback.message.answer(text)
        await callback.answer()

# --- СООБЩЕНИЯ ---
@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # --- ПРОМОКОД ---
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
        if user_id not in user_states or user_states[user_id].get("step") != "username":
            await message.answer("❌ Промокод недействителен или уже использован.")
            return

    # --- Ввод @username и фиксация подарка ---
    if user_id in user_states:
        state = user_states[user_id]
        if state.get("step") == "username":
            state["receiver"] = text
            gift_key = state["gift_key"]
            gift = gifts[gift_key]

            sales.append((user_id, gift['name'], state['receiver'], gift['price']))
            await message.answer(f"🎉 Подарок {gift['name']} отправлен пользователю {state['receiver']}")
            await bot.send_message(ADMIN_ID, f"💰 Новый подарок\nОт: {user_id}\nПодарок: {gift['name']}\nПолучатель: {state['receiver']}\nЦена: {gift['price']}⭐")
            del user_states[user_id]
            return

    # --- АДМИН: создание подарков и промокодов ---
    if user_id in admin_states:
        state = admin_states[user_id]
        step = state.get("step")

        if step == "name":
            state["name"]=text
            state["step"]="price"
            await message.answer("Введите цену подарка (целое число):")
        elif step == "price":
            if not text.isdigit():
                await message.answer("Введите корректное число:")
                return
            state["price"]=int(text)
            state["step"]="gift_code"
            await message.answer("Введите ключ для подарка (без пробелов):")
        elif step == "gift_code":
            gifts[text.lower()]={"name":state["name"],"price":state["price"]}
            del admin_states[user_id]
            await message.answer(f"✅ Подарок {state['name']} добавлен!")
        elif step == "gift_select_for_promo":
            if text not in gifts:
                await message.answer("Такого подарка нет. Введите ключ существующего подарка:")
                return
            state["gift_key"]=text
            state["step"]="promo_code"
            await message.answer("Введите промокод:")
        elif step == "promo_code":
            state["code"]=text.upper()
            state["step"]="promo_uses"
            await message.answer("Введите количество использований промокода (целое число):")
        elif step == "promo_uses":
            if not text.isdigit():
                await message.answer("Введите корректное число использований:")
                return
            uses=int(text)
            promo_codes[state["code"]]={"gift_key":state["gift_key"],"uses_left":uses}
            del admin_states[user_id]
            await message.answer(f"✅ Промокод {state['code']} для подарка {gifts[state['gift_key']]['name']} создан! Количество использований: {uses}")

# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

asyncio.run(main())
