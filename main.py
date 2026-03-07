import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    PreCheckoutQuery
)

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"

bot = Bot(TOKEN)
dp = Dispatcher()

# список подарков
gifts = {
    "bear": ("🧸 Мишка", 9),
    "giftbox": ("🎁 Подарочная коробка", 15),
    "ring": ("💍 Обручальное кольцо", 30),
    "diamond": ("💎 Бриллиант", 30),
    "heart": ("❤️ Сердце", 9),
    "flowers": ("💐 Букет цветов", 20),
    "rose": ("🌹 Роза", 10),
    "champagne": ("🍾 Шампанское", 25),
    "cup": ("🏆 Кубок", 30),
    "rocket": ("🚀 Ракета", 25),
}

# клавиатура
def gifts_keyboard():
    buttons = []
    for key, value in gifts.items():
        name, price = value
        buttons.append(
            [InlineKeyboardButton(
                text=f"{name} — {price} ⭐",
                callback_data=key
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ Отлично! \n\nвыбери подарок:",
        reply_markup=gifts_keyboard()
    )


# выбор подарка
@dp.callback_query()
async def gift_selected(callback: types.CallbackQuery):

    gift_id = callback.data
    name, price = gifts[gift_id]

    prices = [LabeledPrice(label=name, amount=price)]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=name,
        description=f"{name} за {price} звёзд",
        payload=gift_id,
        provider_token="",  # для Stars оставляем пустым
        currency="XTR",
        prices=prices
    )

    await callback.answer()


# проверка перед оплатой
@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# после успешной оплаты
@dp.message()
async def successful_payment(message: types.Message):

    if message.successful_payment:

        await message.answer(
            "❌ Ошибка оплаты.\nПопробуйте ещё раз."
        )

async def main():
    await dp.start_polling(bot)


asyncio.run(main())
