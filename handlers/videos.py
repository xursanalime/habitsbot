from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboards.cencel import cancel_keyboard
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

    await state.clear()  # Eski state bo‘lsa tozalaydi

    user_id = message.from_user.id

    # 🔥 MANA SEN SO‘RAGAN JOY
    videos = await db.fetch(
        "SELECT file_id FROM user_videos WHERE user_id=$1 ORDER BY created_at",
        user_id
    )

    buttons = [
        [InlineKeyboardButton(text="➕ Video qo‘shish", callback_data="add_video")]
    ]

    # 🔥 Raqamlash 1 dan boshlanadi
    for index, video in enumerate(videos, start=1):
        buttons.append(
            [InlineKeyboardButton(
                text=f"🎬 Video {index}",
                callback_data=f"video_{index}"
            )]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "🎥 Sizning videolaringiz:",
        reply_markup=keyboard
    )
# =========================================
# ➕ ADD VIDEO
# =========================================

@router.callback_query(F.data == "add_video")
async def add_video_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📤 Iltimos video yuboring.")
    await state.set_state(AddVideo.waiting_for_video)


@router.message(AddVideo.waiting_for_video, F.video)
async def save_video(message: Message, state: FSMContext, db):

    file_id = message.video.file_id

    await db.execute("""
        INSERT INTO user_videos (user_id, file_id)
        VALUES ($1,$2)
    """, message.from_user.id, file_id)

    await message.answer("✅ Video saqlandi.")
    await state.clear()


# =========================================
# 🎬 WATCH VIDEO
# =========================================

@router.callback_query(F.data.startswith("watch_"))
async def watch_video(callback: CallbackQuery, db):

    video_id = int(callback.data.split("_")[1])

    video = await db.fetchrow("""
        SELECT file_id FROM user_videos
        WHERE id=$1 AND user_id=$2
    """, video_id, callback.from_user.id)

    if video:
        await callback.answer()
        await callback.message.answer_video(video=video["file_id"])
    else:
        await callback.answer("Topilmadi.", show_alert=True)