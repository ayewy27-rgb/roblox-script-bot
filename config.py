import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8820013965:AAEIsLK9t4Q4qcV7934Sr9yA1lNE8Z3Su88")
BOT_USERNAME = os.getenv("BOT_USERNAME", "AsceRobloxScript_bot").replace("@", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@script_drop")
ADMIN_IDS = [5891418490] + [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit() and int(x.strip()) != 5891418490
]

# Mini App URL (Live on Render)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://roblox-script-bot.onrender.com")

DB_PATH = BASE_DIR / "bot_database.sqlite3"
SCRIPTS_STORE_PATH = BASE_DIR / "scripts_store.json"
SHOWN_HISTORY_PATH = BASE_DIR / "shown_history.json"
BANNER_PATH = BASE_DIR / "banner.jpg"
BANNER_WELCOME = BASE_DIR / "banner_welcome.jpg"
BANNER_DELIVERY = BASE_DIR / "banner_delivery.jpg"
BANNER_DELTA = BASE_DIR / "banner_delta.jpg"
BANNER_UPDATE = BASE_DIR / "banner_update.png"
BANNER_SUGGEST = BASE_DIR / "banner_suggest.jpg"
BANNER_LAPIS = BASE_DIR / "banner_lapis.jpg"
BANNER_LAPIS_CENTER = BASE_DIR / "banner_lapis_center.jpg"
BANNER_LAPIS_CLEAN = BASE_DIR / "banner_lapis_clean.jpg"
BANNER_SUB_RED = BASE_DIR / "banner_sub_red.jpg"
AVATAR_PATH = BASE_DIR / "avatar.jpg"
WEBAPP_DIR = BASE_DIR / "webapp"

