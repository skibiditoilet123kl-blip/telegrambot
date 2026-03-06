import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8450764497:AAESpLs3rP-BDtQnIIkqg6nhBdtPsDfvG-w"  # вставь сюда токен от BotFather

bot = Bot(TOKEN)
dp = Dispatcher()

# Список подарков прямо в коде
GIFTS = {
    "Мишка": {"price": 50, "link": "https://example.com/mishka.zip"},
    "Тортик": {"price": 30, "link": "https://example.com/tortik.zip"},
    "Игрушка": {"price": 40, "link": "https://example.com/igrushka.zip"},
    "Конфеты": {"price": 20, "link": "https://example.com/konfety.zip"}
}

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    reply = "Привет! ⭐ У нас есть подарки:\n\n"
    for gift, info in GIFTS.items():
        reply += f"{gift} — {info['price']} Stars\n"
    reply += "\nВыбери подарок командой /buy_Название_подарка"
    await message.answer(reply)

# Команды для покупки
@dp.message()
async def buy(message: types.Message):
    text = message.text
    if text.startswith("/buy_"):
        gift_name = text[5:]
        if gift_name in GIFTS:
            # Симуляция покупки за Stars
            await message.answer(f"Вы купили {gift_name} за {GIFTS[gift_name]['price']} Stars! 🎉")
            await message.answer(f"Вот ваш подарок: {GIFTS[gift_name]['link']}")
        else:
            await message.answer("Такого подарка нет. Проверь команду.")
    else:
        await message.answer("Напиши /buy_Название_подарка, чтобы купить подарок.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

asyncio.run(main())
