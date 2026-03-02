from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu

router = Router()

@router.message(F.text == "🗑 Clear All")
async def clear_all(message: Message, state: FSMContext, db):

    user_id = message.from_user.id

    # 1️⃣ State tozalash
    await state.clear()

    # 2️⃣ Barcha user ma’lumotlarini o‘chirish
    await db.execute("DELETE FROM habit_logs WHERE user_id=$1", user_id)
    await db.execute("DELETE FROM habits WHERE user_id=$1", user_id)
    await db.execute("DELETE FROM prayer_times WHERE user_id=$1", user_id)
    await db.execute("DELETE FROM user_videos WHERE user_id=$1", user_id)
    # Agar users table bo‘lsa va userni ham o‘chirmoqchi bo‘lsang:
    # await db.execute("DELETE FROM users WHERE user_id=$1", user_id)

    await message.answer(
        "🗑 Sizga tegishli barcha ma'lumotlar o‘chirildi.",
        reply_markup=main_menu
    )