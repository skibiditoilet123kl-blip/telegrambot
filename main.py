import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8450764497:AAESpLs3rP-BDtQnIIkqg6nhBdtPsDfvG-w"

bot = Bot(8450764497:AAESpLs3rP-BDtQnIIkqg6nhBdtPsDfvG-w)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот работает ✅")

async def main():
    await dp.start_polling(bot)

asyncio.run(main())