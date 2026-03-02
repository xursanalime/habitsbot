from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.main_menu import main_menu

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, db):
    await db.execute(
        "INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT DO NOTHING",
        message.from_user.id
    )

    await message.answer(
        "Assalomu alaykum.\n\n"
        "Ushbu bot sizning intizomingizni nazorat qiladi.\n"
        "Har kuni soat 23:00 da kunlik tahlil yuboriladi.\n\n"
        "Boshlash uchun menyudan foydalanishingiz mumkin.",
        reply_markup=main_menu
    )

@router.message(CommandStart())
async def start_handler(message: Message, db):
    await db.execute(
        """
        INSERT INTO users (telegram_id)
        VALUES ($1)
        ON CONFLICT (telegram_id) DO NOTHING
        """,
        message.from_user.id
    )

    await message.answer(
        "Assalomu alaykum.\n\n"
        "Ushbu bot sizning intizomingizni nazorat qiladi.\n"
        "Har kuni soat 23:00 da kunlik tahlil yuboriladi.\n\n"
        "Boshlash uchun menyudan foydalanishingiz mumkin."
    )