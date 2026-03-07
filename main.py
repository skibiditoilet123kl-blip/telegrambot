from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery
import asyncio

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067  # твой numeric Telegram ID

bot = Bot(TOKEN)
dp = Dispatcher()

# ===== Список подарков =====
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

# ===== Клавиатура подарков =====
def gifts_keyboard():
    buttons = []
    for key, value in gifts.items():
        name, price = value
        buttons.append([InlineKeyboardButton(f"{name} — {price} ⭐", callback_data=key)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== Кнопочная админка =====
def admin_keyboard():
    buttons = [
        [InlineKeyboardButton("📊 Посмотреть продажи", callback_data="view_sales")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== Старт =====
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "✅ Отлично! Теперь вы можете использовать бота.\n\nВыбери подарок:",
        reply_markup=gifts_keyboard()
    )

# ===== Выбор подарка / кнопки =====
@dp.callback_query()
async def gift_selected(callback: types.CallbackQuery):
    gift_id = callback.data

    # Проверка подарка
    if gift_id in gifts:
        name, price = gifts[gift_id]
        prices = [LabeledPrice(label=name, amount=price * 100)]  # сумма в минимальных единицах
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=name,
            description=f"{name} за {price} звёзд",
            payload=gift_id,
            provider_token="",  # вставь свой платежный токен
            currency="XTR",
            prices=prices
        )
        await callback.answer()

    # Кнопки админки
    elif callback.data.startswith("view_sales") and callback.from_user.id == ADMIN_ID:
        if not sales:
            await callback.message.answer("Продаж пока нет")
        else:
            text = "📊 Продажи:\n\n"
            for s in sales:
                text += f"{s[0]} купил {s[1]} за {s[2]}⭐\n"
            await callback.message.answer(text)
        await callback.answer()

    elif callback.data == "back" and callback.from_user.id == ADMIN_ID:
        await callback.message.answer("👑 Админка", reply_markup=admin_keyboard())
        await callback.answer()

# ===== Проверка перед оплатой =====
@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ===== После успешной оплаты =====
@dp.message()
async def successful_payment(message: types.Message):
    if message.successful_payment:
        gift_id = message.successful_payment.invoice_payload
        name, price = gifts[gift_id]
        sales.append((message.from_user.id, name, price))
        await message.answer(f"✅ Оплата прошла успешно! Вы купили {name} за {price}⭐")
        await bot.send_message(
            ADMIN_ID,
            f"💰 Новая покупка\n\n"
            f"Пользователь: {message.from_user.id}\n"
            f"Подарок: {name}\n"
            f"Цена: {price}⭐"
        )

# ===== Админ панель =====
@dp.message(Command("admin"))
async def admin(message: types.Message):
    print(f"Admin command from user_id: {message.from_user.id}")  # лог для проверки ID
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админке")
        return
    await message.answer("👑 Админ панель", reply_markup=admin_keyboard())

# ===== Запуск бота =====
async def main():
    await dp.start_polling(bot)

asyncio.run(main())
