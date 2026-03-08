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
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

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

# ---------------- STATES ----------------

class PromoCreate(StatesGroup):
    code = State()
    gift = State()
    uses = State()

class PromoUse(StatesGroup):
    code = State()

class SendGift(StatesGroup):
    username = State()

# ---------------- KEYBOARDS ----------------

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Подарки", callback_data="gifts")],
            [InlineKeyboardButton(text="🎫 Промокод", callback_data="promo_menu")]
        ]
    )

def gifts_menu():
    kb=[]
    for key,data in gifts.items():
        name, price = data
        kb.append([InlineKeyboardButton(text=f"{name} — {price}⭐", callback_data=f"send_{key}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def promo_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Ввести промокод", callback_data="enter_promo")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ]
    )

def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎫 Создать промокод", callback_data="create_promo")],
            [InlineKeyboardButton(text="🎫 Активные промокоды", callback_data="active_promos")],
            [InlineKeyboardButton(text="📊 Продажи", callback_data="sales")],
            [InlineKeyboardButton(text="💰 Прибыль", callback_data="profit")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ]
    )

# ---------------- START ----------------

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("🎁 Магазин подарков", reply_markup=main_menu())

# ---------------- BACK ----------------

@dp.callback_query(F.data=="back_main")
async def back(call: CallbackQuery):
    await call.message.edit_text("🎁 Магазин подарков", reply_markup=main_menu())

# ---------------- GIFTS ----------------

@dp.callback_query(F.data=="gifts")
async def gifts_show(call: CallbackQuery):
    await call.message.edit_text("🎁 Выберите подарок", reply_markup=gifts_menu())

# ---------------- SEND GIFT ----------------

@dp.callback_query(F.data.startswith("send_"))
async def send_gift(call: CallbackQuery, state: FSMContext):
    gift = call.data.split("_")[1]
    await state.update_data(gift=gift)
    await call.message.answer("Введите @username или ID пользователя")
    await state.set_state(SendGift.username)

@dp.message(SendGift.username)
async def get_user(msg: Message, state: FSMContext):
    data = await state.get_data()
    gift = data["gift"]
    name, price = gifts[gift]
    prices = [LabeledPrice(label=name, amount=price)]
    await bot.send_invoice(
        chat_id=msg.from_user.id,
        title=f"Подарок {name}",
        description="Отправка подарка",
        payload=gift,
        provider_token="",
        currency="XTR",
        prices=prices
    )
    await state.clear()

# ---------------- PROMO ----------------

@dp.callback_query(F.data=="promo_menu")
async def promo(call: CallbackQuery):
    await call.message.edit_text("🎫 Промокоды", reply_markup=promo_menu())

@dp.callback_query(F.data=="enter_promo")
async def enter_promo(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите промокод")
    await state.set_state(PromoUse.code)

@dp.message(PromoUse.code)
async def check_promo(msg: Message, state: FSMContext):
    code = msg.text.strip()
    cursor.execute("SELECT uses FROM promo WHERE code=?", (code,))
    promo = cursor.fetchone()

    if not promo:
        # Промокода нет
        await msg.answer("❌ Такого промокода нет")
    else:
        # Код есть — сразу сообщаем, что использован
        await msg.answer("❌ Промокод использован")

    await state.clear()

# ---------------- BUY ----------------

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message(F.successful_payment)
async def payment_result(msg: Message):
    await msg.answer("❌ Ошибка при оплате попробуйте снова")

# ---------------- ADMIN ----------------

@dp.message(Command("admin"))
async def admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("👑 Админ панель", reply_markup=admin_menu())

# ---------------- CREATE PROMO ----------------

@dp.callback_query(F.data=="create_promo")
async def create_promo(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await call.message.answer("Введите код промокода")
    await state.set_state(PromoCreate.code)

@dp.message(PromoCreate.code)
async def promo_code(msg: Message, state: FSMContext):
    await state.update_data(code=msg.text)
    text = "Введите ID подарка:\n"
    for k,v in gifts.items():
        text+=f"{k} - {v[0]}\n"
    await msg.answer(text)
    await state.set_state(PromoCreate.gift)

@dp.message(PromoCreate.gift)
async def promo_gift(msg: Message, state: FSMContext):
    await state.update_data(gift=msg.text)
    await msg.answer("Введите количество использований")
    await state.set_state(PromoCreate.uses)

@dp.message(PromoCreate.uses)
async def promo_uses(msg: Message, state: FSMContext):
    data = await state.get_data()
    code = data["code"]
    gift = data["gift"]
    uses = int(msg.text)
    cursor.execute("INSERT INTO promo VALUES(?,?,?)", (code, gift, uses))
    db.commit()
    await msg.answer("✅ Промокод создан")
    await state.clear()

# ---------------- ACTIVE PROMOS ----------------

@dp.callback_query(F.data=="active_promos")
async def active_promos(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT * FROM promo")
    promos = cursor.fetchall()
    if not promos:
        await call.message.answer("Промокодов нет")
        return
    text="🎫 Активные промокоды\n\n"
    for p in promos:
        code = p[0]
        gift = p[1]
        uses = p[2]
        gift_name = gifts[gift][0]
        text+=f"Код: {code}\nПодарок: {gift_name}\nОсталось: {uses}\n\n"
    await call.message.answer(text)

# ---------------- SALES ----------------

@dp.callback_query(F.data=="sales")
async def sales(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT * FROM sales")
    data = cursor.fetchall()
    if not data:
        await call.message.answer("Продаж нет")
        return
    text="📊 Продажи\n\n"
    for s in data:
        text+=f"{s[0]} | {s[1]} | {s[2]}⭐\n"
    await call.message.answer(text)

# ---------------- PROFIT ----------------

@dp.callback_query(F.data=="profit")
async def profit(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT SUM(price) FROM sales")
    money = cursor.fetchone()[0]
    if money is None:
        money = 0
    await call.message.answer(f"💰 Общая прибыль\n\n{money} ⭐")

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
