from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import re
from datetime import datetime, date
from keyboards.cencel import cancel_keyboard

router = Router()


# =========================================
# ⏱ TIME VALIDATION
# =========================================

def valid_time(text: str):
    pattern = r"^([01]\d|2[0-3]):([0-5]\d)$"
    return re.match(pattern, text)


# =========================================
# 🕌 FSM STATES
# =========================================

class SetPrayer(StatesGroup):
    fajr = State()
    dhuhr = State()
    asr = State()
    maghrib = State()
    isha = State()


# =========================================
# 🚀 START
# =========================================

@router.message(F.text == "🕌 Namoz vaqtini kiritish")
async def start_set_prayer(message: Message, state: FSMContext):
    await message.answer("🌅 Bomdod vaqtini kiriting (HH:MM):",reply_markup=cancel_keyboard)

    await state.set_state(SetPrayer.fajr)


# =========================================
# 🌅 FAJR
# =========================================

@router.message(SetPrayer.fajr)
async def set_fajr(message: Message, state: FSMContext):
    if not valid_time(message.text):
        await message.answer("❌ Format noto‘g‘ri.\nMasalan: 06:15")
        return

    await state.update_data(fajr=message.text)
    await message.answer("☀️ Peshin vaqtini kiriting (HH:MM):")
    await state.set_state(SetPrayer.dhuhr)


# =========================================
# ☀️ DHUHR
# =========================================

@router.message(SetPrayer.dhuhr)
async def set_dhuhr(message: Message, state: FSMContext):
    if not valid_time(message.text):
        await message.answer("❌ Format noto‘g‘ri.\nMasalan: 12:45")
        return

    await state.update_data(dhuhr=message.text)
    await message.answer("🌇 Asr vaqtini kiriting (HH:MM):")
    await state.set_state(SetPrayer.asr)


# =========================================
# 🌇 ASR
# =========================================

@router.message(SetPrayer.asr)
async def set_asr(message: Message, state: FSMContext):
    if not valid_time(message.text):
        await message.answer("❌ Format noto‘g‘ri.\nMasalan: 16:30")
        return

    await state.update_data(asr=message.text)
    await message.answer("🌙 Shom vaqtini kiriting (HH:MM):")
    await state.set_state(SetPrayer.maghrib)


# =========================================
# 🌙 MAGHRIB
# =========================================

@router.message(SetPrayer.maghrib)
async def set_maghrib(message: Message, state: FSMContext):
    if not valid_time(message.text):
        await message.answer("❌ Format noto‘g‘ri.\nMasalan: 18:50")
        return

    await state.update_data(maghrib=message.text)
    await message.answer("🌌 Xufton vaqtini kiriting (HH:MM):")
    await state.set_state(SetPrayer.isha)


# =========================================
# 🌌 ISHA + SAVE
# =========================================

@router.message(SetPrayer.isha)
async def save_prayers(message: Message, state: FSMContext, db):
    if not valid_time(message.text):
        await message.answer("❌ Format noto‘g‘ri.\nMasalan: 20:10")
        return

    data = await state.get_data()

    fajr_time = datetime.strptime(data["fajr"], "%H:%M").time()
    dhuhr_time = datetime.strptime(data["dhuhr"], "%H:%M").time()
    asr_time = datetime.strptime(data["asr"], "%H:%M").time()
    maghrib_time = datetime.strptime(data["maghrib"], "%H:%M").time()
    isha_time = datetime.strptime(message.text, "%H:%M").time()

    await db.execute("""
        INSERT INTO prayer_times
        (user_id, fajr, dhuhr, asr, maghrib, isha)
        VALUES ($1,$2,$3,$4,$5,$6)
        ON CONFLICT (user_id)
        DO UPDATE SET
            fajr=EXCLUDED.fajr,
            dhuhr=EXCLUDED.dhuhr,
            asr=EXCLUDED.asr,
            maghrib=EXCLUDED.maghrib,
            isha=EXCLUDED.isha;
    """,
        message.from_user.id,
        fajr_time,
        dhuhr_time,
        asr_time,
        maghrib_time,
        isha_time
    )

    await message.answer(
        f"✅ Namoz vaqtlari saqlandi:\n\n"
        f"🌅 Bomdod: {data['fajr']}\n"
        f"☀️ Peshin: {data['dhuhr']}\n"
        f"🌇 Asr: {data['asr']}\n"
        f"🌙 Shom: {data['maghrib']}\n"
        f"🌌 Xufton: {message.text}"
    )

    await state.clear()


# =========================================
# ✅ O‘QIDIM CALLBACK
# =========================================

@router.callback_query(F.data.startswith("prayer_done:"))
async def prayer_done(callback: CallbackQuery, db):

    prayer_name = callback.data.split(":")[1]

    await db.execute("""
        INSERT INTO prayer_logs (user_id, prayer_name, date, done)
        VALUES ($1,$2,$3,TRUE)
        ON CONFLICT (user_id, prayer_name, date)
        DO NOTHING
    """,
        callback.from_user.id,
        prayer_name,
        date.today()
    )

    await callback.answer("Qabul bo‘lsin 🤲")
    await callback.message.edit_reply_markup(reply_markup=None)


# =========================================
# 📊 BUGUNGI STATISTIKA
# =========================================

@router.message(F.text == "📊 Namoz statistikasi")
async def prayer_stats(message: Message, db):

    rows = await db.fetch("""
        SELECT prayer_name
        FROM prayer_logs
        WHERE user_id=$1 AND date=$2
    """,
        message.from_user.id,
        date.today()
    )

    done_prayers = [r["prayer_name"] for r in rows]

    all_prayers = [
        "🌅 Bomdod",
        "☀️ Peshin",
        "🌇 Asr",
        "🌙 Shom",
        "🌌 Xufton"
    ]

    text = "📊 Bugungi namoz statistikasi:\n\n"

    for prayer in all_prayers:
        if prayer in done_prayers:
            text += f"✅ {prayer}\n"
        else:
            text += f"❌ {prayer}\n"

    await message.answer(text)