import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import LabeledPrice

TOKEN = "8450764497:AAESpLs3rP-BDtQnIIkqg6nhBdtPsDfvG-w"

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Напиши /buy чтобы купить подарки по дешовке⭐")

@dp.message(Command("buy"))
async def buy(message: types.Message):
    prices = [LabeledPrice(label="Подарок", amount=9⭐)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Подарки ⭐",
        description="Подарки⭐",
        payload="product1",
        provider_token="",
        currency="XTR",
        prices=prices
    )

@dp.message(lambda msg: msg.successful_payment)
async def payment(msg: types.Message):
    await msg.answer("Оплата получена ⭐")
    await msg.answer("Вот ваш товар: https://site.com/file.zip")

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
