from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime
from zoneinfo import ZoneInfo
from keyboards.cancel import cancel_keyboard

router = Router()

# Bitta foydalanuvchida maksimal habitlar soni
MAX_HABITS = 20


# ===============================
# 🧠 FSM - Habit qo'shish
# ===============================

class AddHabit(StatesGroup):
    waiting_for_name = State()


# ===============================
# 🔧 Yordamchi funksiya — keyboard yaratish (DRY)
# ===============================

async def build_habits_keyboard(db, user_id, today):
    """Bugungi habitlar uchun inline keyboard yaratadi."""

    rows = await db.fetch(
        "SELECT id, name FROM habits WHERE user_id = $1 ORDER BY created_at",
        user_id
    )

    if not rows:
        return None, 0

    keyboard = []

    for habit in rows:
        log = await db.fetchrow(
            """
            SELECT done
            FROM habit_logs
            WHERE user_id=$1 AND habit_id=$2 AND date=$3
            """,
            user_id,
            habit["id"],
            today
        )

        done = log["done"] if log else False
        icon = "✅" if done else "⬜"

        keyboard.append([
            InlineKeyboardButton(
                text=f"{icon} {habit['name']}",
                callback_data=f"toggle_{habit['id']}"
            )
        ])

    # O'chirish tugmasi
    keyboard.append([
        InlineKeyboardButton(
            text="🗑 Habitni o'chirish",
            callback_data="delete_habit_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard), len(rows)


# ===============================
# ➕ Habit qo'shish
# ===============================

@router.message(F.text == "➕ Habit qo'shish")
async def add_habit_start(message: Message, state: FSMContext, db):

    await state.clear()

    # Limit tekshirish
    count = await db.fetchval(
        "SELECT COUNT(*) FROM habits WHERE user_id = $1",
        message.from_user.id
    )

    if count >= MAX_HABITS:
        await message.answer(
            f"⚠️ Siz maksimal {MAX_HABITS} ta habit qo'sha olasiz.\n"
            "Yangi qo'shish uchun eski habitlardan birini o'chiring."
        )
        return

    await state.set_state(AddHabit.waiting_for_name)
    await message.answer(
        "Iltimos, habit nomini kiriting:",
        reply_markup=cancel_keyboard
    )


@router.message(AddHabit.waiting_for_name)
async def save_habit(message: Message, state: FSMContext, db):
    habit_name = message.text.strip()

    # Bo'sh nom tekshiruvi
    if not habit_name or len(habit_name) > 100:
        await message.answer("❌ Habit nomi 1-100 belgi orasida bo'lishi kerak.")
        return

    try:
        await db.execute(
            "INSERT INTO habits (user_id, name) VALUES ($1, $2)",
            message.from_user.id,
            habit_name
        )
        await message.answer(f"✅ '{habit_name}' muvaffaqiyatli qo'shildi.")
    except Exception as e:
        print(f"Habit save error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

    await state.clear()


# ===============================
# 📋 Bugungi vazifalar
# ===============================

@router.message(F.text == "📋 Bugungi vazifalar")
async def today_habits(message: Message, db):
    user_id = message.from_user.id
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    try:
        markup, count = await build_habits_keyboard(db, user_id, today)
    except Exception as e:
        print(f"Today habits error: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
        return

    if markup is None:
        await message.answer("Sizda hozircha habitlar mavjud emas.\n➕ Habit qo'shish tugmasini bosing.")
        return

    await message.answer(
        "📅 Bugungi vazifalaringiz:",
        reply_markup=markup
    )


# ===============================
# 🔁 Toggle (⬜ ↔ ✅)
# ===============================

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_habit(callback: CallbackQuery, db):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    try:
        log = await db.fetchrow(
            """
            SELECT id, done
            FROM habit_logs
            WHERE user_id=$1 AND habit_id=$2 AND date=$3
            """,
            user_id,
            habit_id,
            today
        )

        if log:
            new_status = not log["done"]
            await db.execute(
                "UPDATE habit_logs SET done=$1 WHERE id=$2",
                new_status,
                log["id"]
            )
        else:
            await db.execute(
                """
                INSERT INTO habit_logs (user_id, habit_id, date, done)
                VALUES ($1, $2, $3, TRUE)
                """,
                user_id,
                habit_id,
                today
            )

        await callback.answer("Holat yangilandi ✅")

        # Keyboardni yangilash (DRY — yordamchi funksiya)
        markup, _ = await build_habits_keyboard(db, user_id, today)
        await callback.message.edit_reply_markup(reply_markup=markup)

    except Exception as e:
        print(f"Toggle habit error: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)


# ===============================
# 🗑 Habit o'chirish
# ===============================

@router.callback_query(F.data == "delete_habit_menu")
async def delete_habit_menu(callback: CallbackQuery, db):
    user_id = callback.from_user.id

    rows = await db.fetch(
        "SELECT id, name FROM habits WHERE user_id = $1 ORDER BY created_at",
        user_id
    )

    if not rows:
        await callback.answer("Habitlar topilmadi.", show_alert=True)
        return

    keyboard = []
    for habit in rows:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {habit['name']}",
                callback_data=f"delhabit_{habit['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_habits")
    ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.answer()
    await callback.message.edit_text(
        "🗑 Qaysi habitni o'chirmoqchisiz?",
        reply_markup=markup
    )


@router.callback_query(F.data.startswith("delhabit_"))
async def delete_habit_confirm(callback: CallbackQuery, db):
    habit_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    try:
        # Avval habit loglari o'chadi (CASCADE bo'lsa ham xavfsizlik uchun)
        await db.execute(
            "DELETE FROM habit_logs WHERE habit_id=$1 AND user_id=$2",
            habit_id, user_id
        )
        result = await db.execute(
            "DELETE FROM habits WHERE id=$1 AND user_id=$2",
            habit_id, user_id
        )

        await callback.answer("✅ Habit o'chirildi.")

        # Keyboardni yangilash
        today = datetime.now(ZoneInfo("Asia/Tashkent")).date()
        markup, count = await build_habits_keyboard(db, user_id, today)

        if markup:
            await callback.message.edit_text(
                "📅 Bugungi vazifalaringiz:",
                reply_markup=markup
            )
        else:
            await callback.message.edit_text("Sizda hozircha habitlar mavjud emas.")

    except Exception as e:
        print(f"Delete habit error: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data == "back_to_habits")
async def back_to_habits(callback: CallbackQuery, db):
    user_id = callback.from_user.id
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    markup, _ = await build_habits_keyboard(db, user_id, today)

    if markup:
        await callback.message.edit_text(
            "📅 Bugungi vazifalaringiz:",
            reply_markup=markup
        )
    else:
        await callback.message.edit_text("Sizda hozircha habitlar mavjud emas.")

    await callback.answer()