from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime
from zoneinfo import ZoneInfo
from keyboards.cencel import cancel_keyboard
router = Router()

# ===============================
# 🧠 FSM - Habit qo‘shish
# ===============================

class AddHabit(StatesGroup):
    waiting_for_name = State()



@router.message(F.text == "➕ Habit qo‘shish")
async def add_habit_start(message: Message, state: FSMContext):

    await state.clear()   # eski state bo‘lsa tozalaydi
    await state.set_state(AddHabit.waiting_for_name)

    await message.answer(
        "Iltimos, habit nomini kiriting:",
        reply_markup=cancel_keyboard   # 👈 mana shu qo‘shildi
    )


@router.message(AddHabit.waiting_for_name)
async def save_habit(message: Message, state: FSMContext, db):
    await db.execute(
        "INSERT INTO habits (user_id, name) VALUES ($1, $2)",
        message.from_user.id,
        message.text
    )

    await message.answer(f"'{message.text}' muvaffaqiyatli qo‘shildi.")
    await state.clear()


# ===============================
# 📋 Bugungi vazifalar
# ===============================

@router.message(F.text == "📋 Bugungi vazifalar")
async def today_habits(message: Message, db):
    user_id = message.from_user.id
    today = datetime.now(ZoneInfo("Asia/Tashkent")).date()

    rows = await db.fetch(
        "SELECT id, name FROM habits WHERE user_id = $1",
        user_id
    )

    if not rows:
        await message.answer("Sizda hozircha habitlar mavjud emas.")
        return

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

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

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

    await callback.answer("Holat yangilandi.")

    # 🔄 Keyboardni yangilash
    rows = await db.fetch(
        "SELECT id, name FROM habits WHERE user_id = $1",
        user_id
    )

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

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_reply_markup(reply_markup=markup)