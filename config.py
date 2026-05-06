import os
import sys
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================
# ✅ MUHIM O'ZGARUVCHILARNI TEKSHIRISH
# =========================================

if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")
    sys.exit(1)

if not DATABASE_URL:
    print("❌ DATABASE_URL topilmadi! .env faylini tekshiring.")
    sys.exit(1)