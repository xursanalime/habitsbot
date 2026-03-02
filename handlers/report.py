from aiogram import Router, F
from keyboards.cencel import cancel_keyboard
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from datetime import date, timedelta
router = Router()


# =========================================
# 📊 STATISTIKA MENU
# =========================================

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@router.message(F.text == "📊 Statistika")
async def stats_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 7 kun", callback_data="stats_7"),
                InlineKeyboardButton(text="🗓 30 kun", callback_data="stats_30"),
            ]
        ]
    )

    await message.answer(
        "📊 Qaysi davr statistikasi kerak?",
        reply_markup=keyboard
    )
    await message.answer(
        "❌ Bekor qilish uchun pastdagi tugmani bosing.",
        reply_markup=cancel_keyboard
    )


# =========================================
# 📅 7 KUN
# =========================================

@router.callback_query(F.data == "stats_7")
async def stats_7_days(callback: CallbackQuery, db):
    await callback.answer()
    await send_detailed_stats(callback.message, db, 7)


# =========================================
# 🗓 30 KUN
# =========================================

@router.callback_query(F.data == "stats_30")
async def stats_30_days(callback: CallbackQuery, db):
    await callback.answer()
    await send_detailed_stats(callback.message, db, 30)


# =========================================
# 🔥 ASOSIY STATISTIKA FUNKSIYA
# =========================================

async def send_detailed_stats(message: Message, db, days: int):

    user_id = message.chat.id
    today = date.today()

    prayers = [
        "🌅 Bomdod",
        "☀️ Peshin",
        "🌇 Asr",
        "🌙 Shom",
        "🌌 Xufton"
    ]

    text = f"📊 So‘nggi {days} kun statistikasi\n"

    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)

        text += f"\n\n📅 {day}:\n"

        # ---------------- HABIT ----------------
        habit_rows = await db.fetch("""
            SELECT h.name, COALESCE(l.done, FALSE) as done
            FROM habits h
            LEFT JOIN habit_logs l
            ON h.id = l.habit_id
            AND l.date = $2
            WHERE h.user_id = $1
        """, user_id, day)

        if habit_rows:
            text += "🧠 Habit:\n"
            for row in habit_rows:
                icon = "✅" if row["done"] else "❌"
                text += f"{icon} {row['name']}\n"
        else:
            text += "🧠 Habit: yo‘q\n"

        # ---------------- NAMOZ ----------------
        prayer_rows = await db.fetch("""
            SELECT prayer_name
            FROM prayer_logs
            WHERE user_id=$1 AND date=$2
        """, user_id, day)

        done_list = [r["prayer_name"] for r in prayer_rows]

        text += "🕌 Namoz:\n"

        for prayer in prayers:
            icon = "✅" if prayer in done_list else "❌"
            text += f"{icon} {prayer}\n"

    # Telegram limit uchun
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await message.answer(text[i:i+4000])
    else:
        await message.answer(text)