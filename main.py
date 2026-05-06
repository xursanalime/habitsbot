import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.habits import router as habits_router
from database import connect_db, create_tables
from scheduler import start_scheduler
from handlers import prayers
from handlers import report
from handlers import videos
from handlers import common
from handlers import admin

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    pool = await connect_db()
    await create_tables(pool)

    dp.include_router(common.router)
    dp.include_router(start_router)
    dp.include_router(prayers.router)
    dp.include_router(habits_router)
    dp.include_router(videos.router)
    dp.include_router(report.router)
    dp.include_router(admin.router)

    start_scheduler(bot, pool)  # 🔥 shu yerda

    await dp.start_polling(bot, db=pool)

if __name__ == "__main__":
    asyncio.run(main())