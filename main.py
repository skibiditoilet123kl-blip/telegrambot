import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"

bot = Bot(TOKEN)
dp = Dispatcher()

# список подарков
gifts = {
    "bear": ("🧸 Мишка", 15),
    "giftbox": ("🎁 Подарочная коробка", 25),
    "ring": ("💍 Обручальное кольцо", 100),
    "diamond": ("💎 Бриллиант", 100),
    "heart": ("❤️ Сердце", 15),
    "flowers": ("💐 Букет цветов", 50),
    "rose": ("🌹 Роза", 25),
    "champagne": ("🍾 Шампанское", 50),
    "cup": ("🏆 Кубок", 100),
    "rocket": ("🚀 Ракета", 50),
}

# клавиатура подарков
def gifts_keyboard():
    buttons = []
    for key, value in gifts.items():
        name, price = value
        buttons.append(
            [InlineKeyboardButton(
                text=f"{name} — {price} звёзд",
                callback_data=key
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ Отлично! Теперь вы можете использовать бота.\n\nВыбери подарок:",
        reply_markup=gifts_keyboard()
    )


@dp.callback_query()
async def gift_selected(callback: types.CallbackQuery):

    key = callback.data
    name, price = gifts[key]

    await callback.message.answer(
        f"{name}\n{name} за {price} звёзд ⭐"
    )

    await callback.answer()


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
