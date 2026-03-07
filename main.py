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
        "✅ Отлично! Теперь вы можете использовать бота.\n\nВыбери подарок:",
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

        gift_id = message.successful_payment.invoice_payload
        name, price = gifts[gift_id]

        await message.answer(
            f"🎉 Оплата прошла успешно!\n\n"
            f"Вы получили подарок:\n{name}"
        )


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
