from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Bugungi vazifalar"),
            KeyboardButton(text="➕ Habit qo‘shish")
        ],
        [
            KeyboardButton(text="🕌 Namoz vaqtini kiritish"),
            KeyboardButton(text="📊 Statistika")
        ],
        [
            KeyboardButton(text="🎥 Video"),
            KeyboardButton(text="🗑 Clear All")
        ]
    ],
    resize_keyboard=True
)