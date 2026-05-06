from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboards.cancel import cancel_keyboard
router = Router()


# =========================================
# FSM
# =========================================

class AddVideo(StatesGroup):
    waiting_for_video = State()


# =========================================
# 🎥 VIDEO MENU
# =========================================

@router.message(F.text == "🎥 Video")
async def video_menu(message: Message, state: FSMContext, db):

    await state.clear()  # Eski state bo'lsa tozalaydi

    user_id = message.from_user.id

    try:
        videos = await db.fetch(
            "SELECT id, file_id FROM user_videos WHERE user_id=$1 ORDER BY created_at",
            user_id
        )

        buttons = [
            [InlineKeyboardButton(text="➕ Video qo'shish", callback_data="add_video")]
        ]

        for index, video in enumerate(videos, start=1):
            buttons.append(
                [
                    InlineKeyboardButton(text=f"🎬 Video {index}", callback_data=f"watch_{video['id']}"),
                    InlineKeyboardButton(text="🗑", callback_data=f"delvideo_{video['id']}")
                ]
            )

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            "🎥 Sizning videolaringiz:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Video menu error: {e}")
        await message.answer("❌ Videolarni yuklashda xatolik yuz berdi.")


# =========================================
# ➕ ADD VIDEO
# =========================================

@router.callback_query(F.data == "add_video")
async def add_video_start(callback: CallbackQuery, state: FSMContext, db):
    # Maksimal video sonini tekshirish (masalan 10 ta)
    count = await db.fetchval("SELECT COUNT(*) FROM user_videos WHERE user_id=$1", callback.from_user.id)
    if count >= 10:
        await callback.answer("⚠️ Maksimal video soniga (10ta) yetdingiz.", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer("📤 Iltimos video yuboring.", reply_markup=cancel_keyboard)
    await state.set_state(AddVideo.waiting_for_video)


@router.message(AddVideo.waiting_for_video, F.video)
async def save_video(message: Message, state: FSMContext, db):

    file_id = message.video.file_id

    # Juda katta videolarni rad etish (>50 MB)
    if message.video.file_size and message.video.file_size > 50 * 1024 * 1024:
        await message.answer("❌ Video hajmi 50MB dan kichik bo'lishi kerak.")
        return

    try:
        await db.execute("""
            INSERT INTO user_videos (user_id, file_id)
            VALUES ($1,$2)
        """, message.from_user.id, file_id)

        await message.answer("✅ Video saqlandi.")
    except Exception as e:
        print(f"Video save error: {e}")
        await message.answer("❌ Videoni saqlashda xatolik yuz berdi.")

    await state.clear()


# =========================================
# 🎬 WATCH VIDEO
# =========================================

@router.callback_query(F.data.startswith("watch_"))
async def watch_video(callback: CallbackQuery, db):

    video_id = int(callback.data.split("_")[1])

    try:
        video = await db.fetchrow("""
            SELECT file_id FROM user_videos
            WHERE id=$1 AND user_id=$2
        """, video_id, callback.from_user.id)

        if video:
            await callback.answer()
            await callback.message.answer_video(video=video["file_id"])
        else:
            await callback.answer("Topilmadi.", show_alert=True)
    except Exception as e:
        print(f"Watch video error: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)

# =========================================
# 🗑 DELETE VIDEO
# =========================================

@router.callback_query(F.data.startswith("delvideo_"))
async def delete_video(callback: CallbackQuery, db):
    video_id = int(callback.data.split("_")[1])

    try:
        await db.execute("""
            DELETE FROM user_videos
            WHERE id=$1 AND user_id=$2
        """, video_id, callback.from_user.id)

        await callback.answer("✅ Video o'chirildi", show_alert=True)
        # Menuni qayta yuklash uchun xabarni o'chirish kerak yoki edit qilish kerak
        await callback.message.delete()
    except Exception as e:
        print(f"Delete video error: {e}")
        await callback.answer("❌ O'chirishda xatolik yuz berdi", show_alert=True)