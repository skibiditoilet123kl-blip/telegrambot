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
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN="8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID=5349252067

bot=Bot(TOKEN)
dp=Dispatcher(storage=MemoryStorage())

# ---------------- DATABASE ----------------

db=sqlite3.connect("shop.db")
cursor=db.cursor()

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

gifts={
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

# ---------------- STATES ----------------

class PromoCreate(StatesGroup):

    code=State()
    gift=State()
    uses=State()

class PromoUse(StatesGroup):

    code=State()

# ---------------- KEYBOARDS ----------------

def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Подарки",callback_data="gifts")],
            [InlineKeyboardButton(text="🎫 Промокод",callback_data="promo_menu")]
        ]
    )

def gifts_menu():

    kb=[]

    for key,data in gifts.items():

        name,price=data

        kb.append([
            InlineKeyboardButton(
                text=f"{name} — {price}⭐",
                callback_data=f"buy_{key}"
            )
        ])

    kb.append([InlineKeyboardButton(text="⬅️ Назад",callback_data="back_main")])

    return InlineKeyboardMarkup(inline_keyboard=kb)

def promo_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Ввести промокод",callback_data="enter_promo")],
            [InlineKeyboardButton(text="⬅️ Назад",callback_data="back_main")]
        ]
    )

def admin_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎫 Создать промокод",callback_data="create_promo")],
            [InlineKeyboardButton(text="📊 Продажи",callback_data="sales")],
            [InlineKeyboardButton(text="⬅️ Назад",callback_data="back_main")]
        ]
    )

# ---------------- START ----------------

@dp.message(Command("start"))
async def start(msg:Message):

    await msg.answer(
        "🎁 Магазин подарков",
        reply_markup=main_menu()
    )

# ---------------- BACK ----------------

@dp.callback_query(F.data=="back_main")
async def back(call:CallbackQuery):

    await call.message.edit_text(
        "🎁 Магазин подарков",
        reply_markup=main_menu()
    )

# ---------------- GIFTS ----------------

@dp.callback_query(F.data=="gifts")
async def gifts_show(call:CallbackQuery):

    await call.message.edit_text(
        "🎁 Выберите подарок",
        reply_markup=gifts_menu()
    )

# ---------------- PROMO MENU ----------------

@dp.callback_query(F.data=="promo_menu")
async def promo(call:CallbackQuery):

    await call.message.edit_text(
        "🎫 Промокоды",
        reply_markup=promo_menu()
    )

# ---------------- ENTER PROMO ----------------

@dp.callback_query(F.data=="enter_promo")
async def enter_promo(call:CallbackQuery,state:FSMContext):

    await call.message.answer("Введите промокод")

    await state.set_state(PromoUse.code)

# ---------------- CHECK PROMO ----------------

@dp.message(PromoUse.code)
async def check_promo(msg:Message,state:FSMContext):

    code=msg.text

    cursor.execute("SELECT * FROM promo WHERE code=?",(code,))
    promo=cursor.fetchone()

    if not promo:

        await msg.answer("❌ Промокод не действителен")
        return

    gift=promo[1]
    uses=promo[2]

    if uses<=0:

        await msg.answer("❌ Промокод использован")
        return

    name,price=gifts[gift]

    cursor.execute(
        "UPDATE promo SET uses=? WHERE code=?",
        (uses-1,code)
    )

    db.commit()

    await msg.answer(
        f"🎁 Вы получили подарок\n{name}"
    )

    await state.clear()

# ---------------- BUY GIFT ----------------

@dp.callback_query(F.data.startswith("buy_"))
async def buy(call:CallbackQuery):

    gift=call.data.split("_")[1]

    name,price=gifts[gift]

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

    await bot.answer_pre_checkout_query(pre_checkout_q.id,ok=True)

# ---------------- PAYMENT SUCCESS ----------------

@dp.message(F.successful_payment)
async def success(msg:Message):

    gift=msg.successful_payment.invoice_payload

    name,price=gifts[gift]

    cursor.execute(
        "INSERT INTO sales VALUES(?,?,?)",
        (msg.from_user.id,name,price)
    )

    db.commit()

    await msg.answer(
        f"🎉 Покупка успешна!\n{name}"
    )

# ---------------- ADMIN ----------------

@dp.message(Command("admin"))
async def admin(msg:Message):

    if msg.from_user.id!=ADMIN_ID:
        return

    await msg.answer(
        "👑 Админ панель",
        reply_markup=admin_menu()
    )

# ---------------- CREATE PROMO ----------------

@dp.callback_query(F.data=="create_promo")
async def create_promo(call:CallbackQuery,state:FSMContext):

    if call.from_user.id!=ADMIN_ID:
        return

    await call.message.answer("Введите код промокода")

    await state.set_state(PromoCreate.code)

@dp.message(PromoCreate.code)
async def promo_code(msg:Message,state:FSMContext):

    await state.update_data(code=msg.text)

    text="Выберите подарок\n\n"

    for k,v in gifts.items():
        text+=f"{k} - {v[0]}\n"

    await msg.answer(text)

    await state.set_state(PromoCreate.gift)

@dp.message(PromoCreate.gift)
async def promo_gift(msg:Message,state:FSMContext):

    await state.update_data(gift=msg.text)

    await msg.answer("Введите количество использований")

    await state.set_state(PromoCreate.uses)

@dp.message(PromoCreate.uses)
async def promo_uses(msg:Message,state:FSMContext):

    data=await state.get_data()

    code=data["code"]
    gift=data["gift"]
    uses=int(msg.text)

    cursor.execute(
        "INSERT INTO promo VALUES(?,?,?)",
        (code,gift,uses)
    )

    db.commit()

    await msg.answer("✅ Промокод создан")

    await state.clear()

# ---------------- SALES ----------------

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

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
