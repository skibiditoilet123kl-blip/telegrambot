from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

TOKEN = "8614684488:AAFlWlgEm6CcuVaq5kJe8te0PuYHV0Wead8"
ADMIN_ID = 5349252067

bot = Bot(TOKEN)
dp = Dispatcher()

# ===== Подарки =====
gifts = {
    "bear": "🧸 Мишка",
    "giftbox": "🎁 Подарочная коробка",
    "ring": "💍 Обручальное кольцо",
    "diamond": "💎 Бриллиант",
}

sales = []

# ===== Клавиатура подарков =====
def gifts_keyboard():
    buttons = [[InlineKeyboardButton(text=name, callback_data=key)] for key, name in gifts.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== Кнопочная админка =====
def admin_keyboard():
    buttons = [
        [InlineKeyboardButton("📊 Посмотреть продажи", callback_data="view_sales")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== /start =====
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Выбери подарок:", reply_markup=gifts_keyboard())

# ===== /admin =====
@dp.message(Command("admin"))
async def admin(message: types.Message):
    print(f"Admin command from user_id: {message.from_user.id}")  # проверка ID
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админке")
        return
    await message.answer("👑 Админ панель", reply_markup=admin_keyboard())

# ===== Callback =====
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if callback.data in gifts:
        await callback.message.answer(f"Вы выбрали {gifts[callback.data]}")
        await callback.answer()

    elif callback.data == "view_sales" and user_id == ADMIN_ID:
        if not sales:
            await callback.message.answer("Продаж пока нет")
        else:
            text = "📊 Продажи:\n" + "\n".join([f"{s[0]} купил {s[1]}" for s in sales])
            await callback.message.answer(text)
        await callback.answer()

    elif callback.data == "back" and user_id == ADMIN_ID:
        await callback.message.answer("Вы в админке", reply_markup=admin_keyboard())
        await callback.answer()

# ===== Запуск =====
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

asyncio.run(main())
