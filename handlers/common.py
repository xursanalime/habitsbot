from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu  # ⚠️ main keyboard import

router = Router()


# =========================================
# ❌ GLOBAL CANCEL
# =========================================

@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):

    current_state = await state.get_state()

    # Agar hech qanday jarayon bo‘lmasa
    if current_state is None:
        await message.answer(
            "Hech qanday faol jarayon yo‘q.",
            reply_markup=main_menu
        )
        return

    # State tozalaymiz
    await state.clear()

    await message.answer(
        "❌ Jarayon bekor qilindi.\nAsosiy menyuga qaytdingiz.",
        reply_markup=main_menu
    )