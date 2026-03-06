import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8450764497:AAESpLs3rP-BDtQnIIkqg6nhBdtPsDfvG-w"  # вставь сюда токен от BotFather

bot = Bot(TOKEN)
dp = Dispatcher()

# Загружаем подарки
with open("gifts.json", "r", encoding="utf-8") as f:
    gifts = json.load(f)

# Кнопки меню подарков
def gifts_keyboard():
    buttons = [KeyboardButton(gift) for gift in gifts.keys()]
    keyboard = ReplyKeyboardMarkup(keyboard=[[b] for b in buttons], resize_keyboard=True)
    return keyboard

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! 🎁 Выбери подарок из меню ниже:",
        reply_markup=gifts_keyboard()
    )

@dp.message()
async def buy_gift(message: types.Message):
    gift_name = message.text
    if gift_name in gifts:
        # Симуляция покупки
        await message.answer(f"Ты выбрал подарок: {gift_name} 🎉")
        await message.answer(f"Вот твой подарок: {gifts[gift_name]}")
    else:
        await message.answer("Пожалуйста, выбери подарок из меню ниже:", reply_markup=gifts_keyboard())

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
