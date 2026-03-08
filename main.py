import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery
)
from aiogram.filters import Command

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher()

# ---------------- DATABASE ----------------

db = sqlite3.connect("shop.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS promo(
code TEXT,
gift TEXT,
uses INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
user INTEGER,
gift TEXT,
price INTEGER
)
""")

db.commit()

# ---------------- GIFTS ----------------

gifts = {
"bear":("🧸 Мишка",15),
"rose":("🌹 Роза",25),
"flowers":("💐 Букет",50),
"diamond":("💎 Бриллиант",100),
"heart":("❤️ Сердце",15),
"ring":("💍 Кольцо",100),
"box":("🎁 Коробка",25),
"champ":("🍾 Шампанское",50),
"cup":("🏆 Кубок",100),
"rocket":("🚀 Ракета",50)
}

# ---------------- KEYBOARDS ----------------

def start_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Подарки",callback_data="gifts")],
            [InlineKeyboardButton(text="🎫 Промокод",callback_data="promo")]
        ]
    )

def gifts_kb():

    kb=[]

    for key,data in gifts.items():

        name,price=data

        kb.append([
            InlineKeyboardButton(
                text=f"{name} — {price}⭐",
                callback_data=f"buy_{key}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_kb():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎫 Создать промокод",callback_data="createpromo")],
            [InlineKeyboardButton(text="📊 Продажи",callback_data="sales")],
            [InlineKeyboardButton(text="🎟 Промокоды",callback_data="promos")]
        ]
    )

# ---------------- START ----------------

@dp.message(Command("start"))
async def start(msg:Message):

    await msg.answer(
        "🎁 Магазин подарков",
        reply_markup=start_kb()
    )

# ---------------- ADMIN ----------------

@dp.message(Command("admin"))
async def admin(msg:Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        "👑 Админ панель",
        reply_markup=admin_kb()
    )

# ---------------- SHOW GIFTS ----------------

@dp.callback_query(F.data=="gifts")
async def show_gifts(call:CallbackQuery):

    await call.message.edit_text(
        "Выберите подарок",
        reply_markup=gifts_kb()
    )

# ---------------- BUY GIFT ----------------

@dp.callback_query(F.data.startswith("buy_"))
async def buy(call:CallbackQuery):

    gift = call.data.split("_")[1]

    name,price = gifts[gift]

    prices=[LabeledPrice(label=name,amount=price)]

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=name,
        description="Покупка подарка",
        payload=gift,
        provider_token="",
        currency="XTR",
        prices=prices
    )

# ---------------- PRE CHECKOUT ----------------

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_q:PreCheckoutQuery):

    await bot.answer_pre_checkout_query(
        pre_checkout_q.id,
        ok=True
    )

# ---------------- SUCCESS PAYMENT ----------------

@dp.message(F.successful_payment)
async def success(msg:Message):

    gift = msg.successful_payment.invoice_payload

    name,price=gifts[gift]

    cursor.execute(
        "INSERT INTO sales VALUES(?,?,?)",
        (msg.from_user.id,name,price)
    )

    db.commit()

    await msg.answer(
        f"🎉 Покупка успешна!\n"
        f"Вы купили {name}"
    )

    await bot.send_message(
        ADMIN_ID,
        f"💰 Новая покупка\n"
        f"User: {msg.from_user.id}\n"
        f"Gift: {name}\n"
        f"Price: {price}⭐"
    )

# ---------------- ADMIN BUTTONS ----------------

@dp.callback_query(F.data=="sales")
async def sales(call:CallbackQuery):

    if call.from_user.id!=ADMIN_ID:
        return

    cursor.execute("SELECT * FROM sales")
    data=cursor.fetchall()

    if not data:
        await call.message.answer("Продаж нет")
        return

    text="💰 Продажи\n\n"

    for s in data:
        text+=f"{s[0]} | {s[1]} | {s[2]}⭐\n"

    await call.message.answer(text)

@dp.callback_query(F.data=="promos")
async def promos(call:CallbackQuery):

    if call.from_user.id!=ADMIN_ID:
        return

    cursor.execute("SELECT * FROM promo")
    data=cursor.fetchall()

    if not data:
        await call.message.answer("Промокодов нет")
        return

    text="🎫 Промокоды\n\n"

    for p in data:
        text+=f"{p[0]} | {p[1]} | {p[2]}\n"

    await call.message.answer(text)

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
