from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date
from zoneinfo import ZoneInfo
import asyncio
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date

# =========================================
# 🚀 START SCHEDULER
# =========================================

def start_scheduler(bot, db):

    scheduler = AsyncIOScheduler(
        event_loop=asyncio.get_event_loop(),
        timezone=ZoneInfo("Asia/Tashkent")
    )

    scheduler.add_job(
        send_daily_report,
        trigger="cron",
        hour=23,
        minute=0,
        args=[bot, db]
    )
    scheduler.add_job(
        send_prayer_reminders,
        trigger="cron",
        minute="*",
        args=[bot, db]
    )

    scheduler.start()


# =========================================
# 📊 DAILY REPORT
# =========================================

async def send_daily_report(bot, db):

    today = date.today()

    # users jadvalidan hamma foydalanuvchilarni olish
    users = await db.fetch("SELECT telegram_id FROM users")

    for user in users:

        user_id = user["telegram_id"]

        try:
            # foydalanuvchining habitlari va bugungi statusi
            habits = await db.fetch("""
                SELECT h.id,
                       h.name,
                       COALESCE(l.done, FALSE) AS done
                FROM habits h
                LEFT JOIN habit_logs l
                  ON h.id = l.habit_id
                  AND l.user_id = $1
                  AND l.date = $2
                WHERE h.user_id = $1
            """, user_id, today)

            if not habits:
                continue

            done_list = []
            not_done_list = []

            for habit in habits:
                if habit["done"]:
                    done_list.append(habit["name"])
                else:
                    not_done_list.append(habit["name"])

            text = "📊 Kunlik statistika:\n\n"

            if done_list:
                text += "✅ Bajarilganlar:\n"
                for h in done_list:
                    text += f"• {h}\n"

            if not_done_list:
                text += "\n❌ Bajarilmaganlar:\n"
                for h in not_done_list:
                    text += f"• {h}\n"

            await bot.send_message(user_id, text)

        except Exception as e:
            print(f"Report error for user {user_id}: {e}")
            continue

async def send_prayer_reminders(bot, db):

    now = datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%H:%M")

    users = await db.fetch("""
            SELECT user_id, fajr, dhuhr, asr, maghrib, isha
            FROM prayer_times
        """)
    for user in users:

        prayers = {
            "🌅 Bomdod": user["fajr"],
            "☀️ Peshin": user["dhuhr"],
            "🌇 Asr": user["asr"],
            "🌙 Shom": user["maghrib"],
            "🌌 Xufton": user["isha"],
        }

        for name, time_value in prayers.items():

            if time_value and time_value.strftime("%H:%M") == now:

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ O‘qidim",
                            callback_data=f"prayer_done:{name}"
                        )
                    ]
                ])

                await bot.send_message(
                    user["user_id"],
                    f"🕌 {name} vaqti bo‘ldi.\nAlloh qabul qilsin 🤲",
                    reply_markup=keyboard
                )