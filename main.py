import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher()

# данные
gifts = {
    "bear": {"name": "🧸 Мишка", "price": 15},
    "rose": {"name": "🌹 Роза", "price": 25},
    "diamond": {"name": "💎 Бриллиант", "price": 100}
}

promo_codes = {}
user_state = {}

# клавиатуры
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Подарки", callback_data="gifts")],
        [InlineKeyboardButton(text="🎫 Промокод", callback_data="promo")]
    ])

def gifts_kb():
    kb = []
    for key,g in gifts.items():
        kb.append([InlineKeyboardButton(
            text=f"{g['name']} — {g['price']}⭐",
            callback_data=f"gift_{key}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Назад",callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# старт
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Выберите действие",reply_markup=start_kb())

# админ
@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Админка\n/createpromo\n/listpromo")

# кнопки
@dp.callback_query(F.data=="gifts")
async def show_gifts(call: CallbackQuery):
    await call.message.edit_text("Выберите подарок",reply_markup=gifts_kb())

@dp.callback_query(F.data=="back")
async def back(call: CallbackQuery):
    await call.message.edit_text("Выберите действие",reply_markup=start_kb())

@dp.callback_query(F.data.startswith("gift_"))
async def select_gift(call: CallbackQuery):
    gift = call.data.split("_")[1]
    user_state[call.from_user.id]={"gift":gift}
    await call.message.answer("Введите @username получателя")

# ввод username
@dp.message()
async def process(message: Message):
    uid=message.from_user.id

    if uid in user_state:
        gift_key=user_state[uid]["gift"]
        gift=gifts[gift_key]

        await message.answer(
            f"🎁 Подарок {gift['name']} отправлен {message.text}"
        )

        await bot.send_message(
            ADMIN_ID,
            f"Новый подарок\n"
            f"От: {uid}\n"
            f"Кому: {message.text}\n"
            f"Подарок: {gift['name']}"
        )

        del user_state[uid]
        return

    # промокод
    code=message.text.upper()
    if code in promo_codes:
        gift=promo_codes[code]["gift"]

        if promo_codes[code]["uses"]<=0:
            await message.answer("❌ Промокод использован")
            return

        promo_codes[code]["uses"]-=1

        await message.answer(
            f"🎉 Промокод принят!\n"
            f"Вы получили {gifts[gift]['name']}"
        )
        return

# создание промокода
@dp.message(Command("createpromo"))
async def create_promo(message: Message):
    if message.from_user.id!=ADMIN_ID:
        return

    args=message.text.split()

    if len(args)!=4:
        await message.answer(
            "/createpromo CODE gift uses\n"
            "пример:\n"
            "/createpromo FREE bear 5"
        )
        return

    code=args[1].upper()
    gift=args[2]
    uses=int(args[3])

    if gift not in gifts:
        await message.answer("Нет такого подарка")
        return

    promo_codes[code]={
        "gift":gift,
        "uses":uses
    }

    await message.answer("Промокод создан")

# список промокодов
@dp.message(Command("listpromo"))
async def listpromo(message: Message):
    if message.from_user.id!=ADMIN_ID:
        return

    if not promo_codes:
        await message.answer("Промокодов нет")
        return

    text="Промокоды:\n"
    for code,data in promo_codes.items():
        text+=f"{code} | {data['gift']} | {data['uses']}\n"

    await message.answer(text)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
