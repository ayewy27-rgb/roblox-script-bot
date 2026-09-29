import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8820013965:AAEIsLK9t4Q4qcV7934Sr9yA1lNE8Z3Su88")
BOT_USERNAME = os.getenv("BOT_USERNAME", "AsceRobloxScript_bot").replace("@", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@script_drop")
ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

# Mini App URL (Telegram requires HTTPS for WebAppInfo)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://script-drop-app.vercel.app")

DB_PATH = BASE_DIR / "bot_database.sqlite3"
BANNER_PATH = BASE_DIR / "banner.jpg"
AVATAR_PATH = BASE_DIR / "avatar.jpg"
WEBAPP_DIR = BASE_DIR / "webapp"
