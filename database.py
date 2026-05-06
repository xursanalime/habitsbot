import asyncpg
from config import DATABASE_URL


# =========================================
# 🔌 CONNECT DATABASE
# =========================================

async def connect_db():
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        print("✅ Database-ga muvaffaqiyatli ulandi.")
        return pool
    except Exception as e:
        print(f"❌ Database-ga ulanishda xatolik: {e}")
        raise


# =========================================
# 🏗 CREATE TABLES
# =========================================

async def create_tables(pool):
    async with pool.acquire() as conn:

        # =========================================
        # 👤 USERS
        # =========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # =========================================
        # 📌 HABITS
        # =========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(telegram_id)
                    ON DELETE CASCADE
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_habits_user
            ON habits(user_id);
        """)

        # =========================================
        # 📊 HABIT LOGS
        # =========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS habit_logs (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                habit_id INTEGER NOT NULL,
                date DATE NOT NULL,
                done BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id)
                    REFERENCES users(telegram_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (habit_id)
                    REFERENCES habits(id)
                    ON DELETE CASCADE,
                UNIQUE (user_id, habit_id, date)
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_user_date
            ON habit_logs(user_id, date);
        """)

        # =========================================
        # 🕌 PRAYER TIMES (eslatma vaqtlari)
        # =========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS prayer_times (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                fajr TIME,
                dhuhr TIME,
                asr TIME,
                maghrib TIME,
                isha TIME,
                FOREIGN KEY (user_id)
                    REFERENCES users(telegram_id)
                    ON DELETE CASCADE
            );
        """)

        # =========================================
        # 🕌 PRAYER LOGS
        # =========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS prayer_logs (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                prayer_name TEXT NOT NULL,
                date DATE NOT NULL,
                done BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id)
                    REFERENCES users(telegram_id)
                    ON DELETE CASCADE,
                UNIQUE(user_id, prayer_name, date)
            );
        """)

        # =========================================
        # 🎥 USER VIDEOS
        # =========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_videos (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                file_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(telegram_id)
                    ON DELETE CASCADE
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_videos_user
            ON user_videos(user_id);
        """)

    print("✅ Barcha jadvallar tayyor.")