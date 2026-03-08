import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher()

# ---------------- DATABASE ----------------

db = sqlite3.connect("gifts.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS promo(
code TEXT PRIMARY KEY,
gift TEXT,
uses INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
sender INTEGER,
receiver TEXT,
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

user_state = {}

# ---------------- KEYBOARDS ----------------

def start_kb():
 return InlineKeyboardMarkup(
 inline_keyboard=[
 [InlineKeyboardButton(text="🎁 Подарки",callback_data="gifts")],
 [InlineKeyboardButton(text="🎫 Промокод",callback_data="promo")]
 ])

def gifts_kb():

 kb=[]

 for key,data in gifts.items():
  name,price=data

  kb.append([
   InlineKeyboardButton(
   text=f"{name} — {price}⭐",
   callback_data=f"gift_{key}")
  ])

 kb.append([
 InlineKeyboardButton(text="⬅️ Назад",callback_data="back")
 ])

 return InlineKeyboardMarkup(inline_keyboard=kb)

# ---------------- START ----------------

@dp.message(Command("start"))
async def start(msg:Message):

 await msg.answer(
 "🎁 Добро пожаловать в магазин подарков",
 reply_markup=start_kb()
 )

# ---------------- ADMIN ----------------

@dp.message(Command("admin"))
async def admin(msg:Message):

 if msg.from_user.id!=ADMIN_ID:
  return

 await msg.answer(
 "Админ команды:\n\n"
 "/createpromo CODE gift uses\n"
 "/promos\n"
 "/sales"
 )

# ---------------- BUTTONS ----------------

@dp.callback_query(F.data=="gifts")
async def show_gifts(call:CallbackQuery):

 await call.message.edit_text(
 "Выберите подарок",
 reply_markup=gifts_kb()
 )

@dp.callback_query(F.data=="back")
async def back(call:CallbackQuery):

 await call.message.edit_text(
 "Главное меню",
 reply_markup=start_kb()
 )

# ---------------- SELECT GIFT ----------------

@dp.callback_query(F.data.startswith("gift_"))
async def select_gift(call:CallbackQuery):

 gift=call.data.split("_")[1]

 user_state[call.from_user.id]=gift

 await call.message.answer(
 "Введите @username получателя"
 )

# ---------------- MESSAGE ----------------

@dp.message()
async def messages(msg:Message):

 uid=msg.from_user.id
 text=msg.text

 # отправка подарка

 if uid in user_state:

  gift=user_state[uid]

  name,price=gifts[gift]

  cursor.execute(
  "INSERT INTO sales VALUES(?,?,?,?)",
  (uid,text,name,price)
  )
  db.commit()

  await msg.answer(
  f"🎁 Вы отправили {name} пользователю {text}"
  )

  await bot.send_message(
  ADMIN_ID,
  f"💰 Новая покупка\n"
  f"От: {uid}\n"
  f"Кому: {text}\n"
  f"Подарок: {name}\n"
  f"Цена: {price}⭐"
  )

  del user_state[uid]
  return

 # проверка промокода

 cursor.execute(
 "SELECT * FROM promo WHERE code=?",
 (text.upper(),)
 )

 promo=cursor.fetchone()

 if promo:

  code,gift,uses=promo

  if uses<=0:
   await msg.answer("❌ Промокод использован")
   return

  cursor.execute(
  "UPDATE promo SET uses=? WHERE code=?",
  (uses-1,code)
  )
  db.commit()

  name,price=gifts[gift]

  await msg.answer(
  f"🎉 Промокод принят!\n"
  f"Подарок: {name}"
  )

# ---------------- CREATE PROMO ----------------

@dp.message(Command("createpromo"))
async def createpromo(msg:Message):

 if msg.from_user.id!=ADMIN_ID:
  return

 args=msg.text.split()

 if len(args)!=4:
  await msg.answer(
  "Использование:\n"
  "/createpromo CODE gift uses\n"
  "пример:\n"
  "/createpromo FREE bear 5"
  )
  return

 code=args[1].upper()
 gift=args[2]
 uses=int(args[3])

 if gift not in gifts:
  await msg.answer("Нет такого подарка")
  return

 cursor.execute(
 "INSERT OR REPLACE INTO promo VALUES(?,?,?)",
 (code,gift,uses)
 )

 db.commit()

 await msg.answer("✅ Промокод создан")

# ---------------- LIST PROMO ----------------

@dp.message(Command("promos"))
async def promos(msg:Message):

 if msg.from_user.id!=ADMIN_ID:
  return

 cursor.execute("SELECT * FROM promo")
 promos=cursor.fetchall()

 if not promos:
  await msg.answer("Промокодов нет")
  return

 text="🎫 Промокоды\n\n"

 for p in promos:
  text+=f"{p[0]} | {p[1]} | {p[2]}\n"

 await msg.answer(text)

# ---------------- SALES ----------------

@dp.message(Command("sales"))
async def sales(msg:Message):

 if msg.from_user.id!=ADMIN_ID:
  return

 cursor.execute("SELECT * FROM sales")
 data=cursor.fetchall()

 if not data:
  await msg.answer("Продаж нет")
  return

 text="💰 Продажи\n\n"

 for s in data:
  text+=f"{s[0]} -> {s[1]} | {s[2]} | {s[3]}⭐\n"

 await msg.answer(text)

# ---------------- RUN ----------------

async def main():
 await dp.start_polling(bot)

asyncio.run(main())
