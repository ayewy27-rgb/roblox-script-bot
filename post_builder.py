import re

def format_game_name(raw_name: str) -> str:
    """Formats game name with Title Case and known acronyms."""
    words = raw_name.strip().split()
    formatted_words = []
    
    known_acronyms = {
        "esp": "ESP",
        "fps": "FPS",
        "psx": "PSX",
        "tps": "TPS",
        "r6": "R6",
        "r15": "R15",
        "pvp": "PvP",
        "pve": "PvE",
        "npc": "NPC",
        "gui": "GUI",
        "hub": "Hub",
    }
    
    for w in words:
        low = w.lower()
        if low in known_acronyms:
            formatted_words.append(known_acronyms[low])
        else:
            formatted_words.append(w.capitalize())
            
    return " ".join(formatted_words)

DEFAULT_FEATURES = (
    "• ESP (Подсветка игроков / предметов)\n"
    "• Auto Farm (Автоматический фарм)\n"
    "• WalkSpeed & JumpPower (Скорость и прыжок)\n"
    "• Teleport / Safe Zone (Телепортация)"
)

DEFAULT_EXECUTORS = "ПК и Мобильные (Delta, Arceus X, Fluxus, Codex, Solara)"

def format_features(raw_features: str) -> str:
    """Formats features list into a neat bulleted list with emojis."""
    if not raw_features or raw_features.strip().lower() in ["по дефолту", "дефолт", "default", "-", "1"]:
        return DEFAULT_FEATURES
    
    items = re.split(r'[,;\n]+', raw_features)
    formatted = []
    
    replacements = {
        "есп": "ESP (ВХ / Подсветка)",
        "esp": "ESP (ВХ / Подсветка)",
        "аим": "Aimbot (Аимбот)",
        "aim": "Aimbot (Аимбот)",
        "автофарм": "Auto Farm (Авто-фарм)",
        "авто фарм": "Auto Farm (Авто-фарм)",
        "autofarm": "Auto Farm (Авто-фарм)",
        "спид": "Speed (Увеличение скорости)",
        "флай": "Fly (Режим полёта)",
        "тп": "Teleport (Телепортация)",
        "годмод": "God Mode (Бессмертие)",
        "инфинит": "Infinite Jump (Бесконечный прыжок)",
    }
    
    for item in items:
        item = item.strip()
        if not item:
            continue
        low = item.lower()
        matched = False
        for k, v in replacements.items():
            if k == low or k in low:
                formatted.append(f"• {v}")
                matched = True
                break
        if not matched:
            cleaned = item.lstrip("•-* ").strip()
            if cleaned:
                formatted.append(f"• {cleaned.capitalize()}")
                
    if not formatted:
        return DEFAULT_FEATURES
    return "\n".join(formatted)

def build_channel_post(game_name: str, features: str, executors: str = DEFAULT_EXECUTORS) -> str:
    """Generates a stylish post for the Telegram channel."""
    title = format_game_name(game_name)
    features_list = format_features(features)
    
    post = (
        f"⚡ <b>НОВЫЙ СКРИПТ | {title}</b> ⚡\n\n"
        f"🎮 <b>Игра:</b> <code>{title}</code>\n\n"
        f"🛠 <b>Функционал:</b>\n"
        f"{features_list}\n\n"
        f"📌 <b>Статус:</b> 🟢 <i>Работает / Undetected</i>\n"
        f"📱 <b>Поддержка:</b> {executors}\n\n"
        f"👇 <b>Нажмите на кнопку ниже, чтобы получить скрипт:</b>"
    )
    return post

def build_user_delivery_message(script_code: str) -> str:
    """Generates the exact response message matching the screenshot."""
    return f"✅ <b>Спасибо за подписку!</b>\n\n{script_code}"
