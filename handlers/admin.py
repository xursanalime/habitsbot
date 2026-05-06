from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu

router = Router()

@router.message(F.text == "🗑 Clear All")
async def clear_all_menu(message: Message):
    # Tasdiqlash tugmalari
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚠️ Ha, barchasini o'chirish", callback_data="confirm_clear_all")
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_clear_all")
            ]
        ]
    )

    await message.answer(
        "❗ <b>DIQQAT!</b>\n\n"
        "Siz barcha ma'lumotlaringizni (habitlar, namozlar, videolar) o'chirib yubormoqchisiz.\n"
        "Bu amalni orqaga qaytarib bo'lmaydi.\n\n"
        "Rostdan ham o'chirmoqchimisiz?",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "confirm_clear_all")
async def execute_clear_all(callback: CallbackQuery, state: FSMContext, db):
    user_id = callback.from_user.id

    try:
        # 1️⃣ State tozalash
        await state.clear()

        # 2️⃣ Barcha user ma'lumotlarini o'chirish
        await db.execute("DELETE FROM habit_logs WHERE user_id=$1", user_id)
        await db.execute("DELETE FROM habits WHERE user_id=$1", user_id)
        await db.execute("DELETE FROM prayer_logs WHERE user_id=$1", user_id)
        await db.execute("DELETE FROM prayer_times WHERE user_id=$1", user_id)
        await db.execute("DELETE FROM user_videos WHERE user_id=$1", user_id)
        
        # Userni butunlay o'chirish (ixtiyoriy, agar qayta ro'yxatdan o'tishi kerak bo'lsa)
        # await db.execute("DELETE FROM users WHERE telegram_id=$1", user_id)

        await callback.message.edit_text("🗑 Sizga tegishli barcha ma'lumotlar muvaffaqiyatli o'chirildi.")
        
        # Menyuni qaytarish
        await callback.message.answer("Boshlash uchun /start buyrug'ini bosing.", reply_markup=main_menu)
        
    except Exception as e:
        print(f"Clear All error: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data == "cancel_clear_all")
async def cancel_clear_all(callback: CallbackQuery):
    await callback.message.edit_text("❌ O'chirish bekor qilindi.")