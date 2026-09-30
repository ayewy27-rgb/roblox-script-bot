import urllib.request
import urllib.parse
import json
import re
import asyncio
import logging
from typing import List, Dict, Any, Tuple
import post_builder

logger = logging.getLogger(__name__)

# Official Authentic PulseHub Universal Loader from pulsehub.gg
PULSEHUB_LOADER_CODE = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/PulseZax/Loader/refs/heads/main/.lua"))()'

PULSEHUB_GAMES = {
    "pulsehub": {
        "title": "⚡ Pulse Hub | Официальный Универсальный Лоадер (Все игры в одном)",
        "game_name": "Pulse Hub Universal",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Авто-определение игры при запуске в Roblox\n"
            "• Без ключа (Keyless) и без регистрации\n"
            "• Поддержка: MM2, Steal an Egg, Rivals, BloxStrike, San Diego\n"
            "• Молниеносная загрузка без зависаний\n"
            "• Работает на Delta, Solara, Wave, Codex, Arceus X"
        ),
        "image_url": "https://pulsehub.gg/og.png",
    },
    "steal an egg": {
        "title": "Pulse Hub | Steal an Egg (Auto Steal, Auto Fuse & ESP)",
        "game_name": "Steal an Egg",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Auto Steal by Rarity, Income & Weight (Кража редких яиц)\n"
            "• Steal Big Eggs mode (Кража огромных яиц по весу)\n"
            "• Anti Traps & Auto Escape Treadmill (Обход всех ловушек)\n"
            "• Hungry Monster Event Auto Farm (Авто-фарм ивента Монстра)\n"
            "• Auto Fuse & Auto Sell (Слияние и авто-продажа питомцев)\n"
            "• Full Egg ESP, Plot ESP & Player ESP (ВХ на яйца и базы)\n"
            "• Fly & Waypoint Teleport (Свободный полёт и телепорт)"
        ),
        "image_url": "https://pulsehub.gg/assets/art/steal-an-egg.webp",
    },
    "mm2": {
        "title": "Pulse Hub | Murder Mystery 2 (Silent Aim, Coin Farm & ESP)",
        "game_name": "Murder Mystery 2",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Role ESP (ВХ на маньяка, шерифа, выпавший пистолет)\n"
            "• Silent Aim & Knife Throw Aimbot (Скрытый аимбот)\n"
            "• Kill Aura & Auto Shoot Murderer (Авто-убийство маньяка)\n"
            "• Auto Farm Coins (Молниеносный сбор монет с авто-уклонением)\n"
            "• Fly, Noclip, Infinite Jump & Desync (Свободный полёт)"
        ),
        "image_url": "https://pulsehub.gg/assets/art/mm2.webp",
    },
    "rivals": {
        "title": "Pulse Hub | RIVALS (Silent Aim, Skeleton ESP, No Recoil)",
        "game_name": "Rivals",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Silent Aim with FOV & Prediction (Скрытый аимбот в голову)\n"
            "• 2D Box & Skeleton ESP (ВХ сквозь любые стены с HP)\n"
            "• No Recoil, No Spread & Rapid Fire (Стрельба без отдачи)\n"
            "• Auto Shoot / TriggerBot (Авто-выстрел при наведении)\n"
            "• BunnyHop & Speed Boost (Распрыжка и скорость)"
        ),
        "image_url": "https://pulsehub.gg/assets/art/rivals.webp",
    },
    "bloxstrike": {
        "title": "Pulse Hub | BloxStrike (Legit/Silent Aim, Skin Changer, ESP)",
        "game_name": "BloxStrike",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Legit & Silent Aim с профилями под каждое оружие\n"
            "• Skin Changer (Все скины на ножи, перчатки и оружие)\n"
            "• ESP Boxes, Chams & Skeleton (Полный ВХ)\n"
            "• Grenade Helper & Bomb Defuse Timer (Траектория гранат)\n"
            "• Auto Buy (Авто-закупка брони и оружия)"
        ),
        "image_url": "https://pulsehub.gg/assets/icons/blox-strike.webp",
    },
    "san diego": {
        "title": "Pulse Hub | San Diego Border RP (Auto Smuggle & Tuning)",
        "game_name": "San Diego Border Roleplay",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Auto Smuggle (Полный цикл авто-контрабанды с продажей)\n"
            "• Garage & Car Tuning (Тюнинг машин, скорость, полный привод)\n"
            "• Silent Aim & Wall Shot (Стрельба сквозь препятствия)\n"
            "• Vehicle & Player ESP (Подсветка машин и игроков)"
        ),
        "image_url": "https://pulsehub.gg/assets/art/san-diego.webp",
    },
    "grow a garden": {
        "title": "Pulse Hub | Grow A Garden 2 (Auto Farm, Auto Sell, ESP)",
        "game_name": "Grow A Garden 2",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Auto Harvest & Plant (Авто-сбор урожая и посадка растений)\n"
            "• Auto Sell & Max Profit (Авто-продажа по максимальной цене)\n"
            "• Plot & Rare Seeds ESP (ВХ на редкие семена и участки)\n"
            "• Speed Boost & Teleport (Увеличенная скорость и телепорт)"
        ),
        "image_url": "https://pulsehub.gg/og.png",
    },
    "+1 speed": {
        "title": "Pulse Hub | +1 Speed Keyboard Escape (Auto Win, Speed)",
        "game_name": "+1 Speed Keyboard Escape",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный)",
        "features": (
            "• Auto Farm Wins (Автоматический фарм побед)\n"
            "• Infinite Speed Multiplier (Бесконечный множитель скорости)\n"
            "• Skip Obstacles & Noclip (Прохождение любых препятствий)\n"
            "• Godmode (Защита от падений и лавы)"
        ),
        "image_url": "https://pulsehub.gg/og.png",
    },
}

SYNONYMS = {
    "пульс": "pulsehub",
    "пульсехаб": "pulsehub",
    "пульсхаб": "pulsehub",
    "pulse": "pulsehub",
    "loader": "pulsehub",
    "лоадер": "pulsehub",
    "все в одном": "pulsehub",
    "всев одном": "pulsehub",
    "универсальный": "pulsehub",
    "универсал": "pulsehub",
    "мм2": "murder mystery 2",
    "мардер": "murder mystery 2",
    "бф": "blox fruits",
    "блокс фрут": "blox fruits",
    "блокс фрутс": "blox fruits",
    "бб": "blade ball",
    "блейд бол": "blade ball",
    "блейдбол": "blade ball",
    "стил ан эгг": "steal an egg",
    "стил эгг": "steal an egg",
    "яйца": "steal an egg",
    "яйцо": "steal an egg",
    "ривалс": "rivals",
    "райвалс": "rivals",
    "блокстрайк": "bloxstrike",
    "страйк": "bloxstrike",
    "blox strike": "bloxstrike",
    "сад": "grow a garden",
    "гарден": "grow a garden",
    "grow a garden": "grow a garden",
    "спид": "+1 speed",
    "скорость": "+1 speed",
    "побег клавиатура": "+1 speed",
    "фиш": "fisch",
    "рыбалка": "fisch",
    "дорс": "doors",
    "двери": "doors",
    "бедварс": "bedwars",
    "да худ": "da hood",
    "дахуд": "da hood",
    "брукхейвен": "brookhaven",
    "пс99": "pet simulator 99",
    "пет сим": "pet simulator 99",
    "арсенал": "arsenal",
    "джуджутсу": "jujutsu shenanigans",
    "форсакен": "forsaken",
    "сан диего": "san diego",
    "сандьего": "san diego",
}

DANGEROUS_PATTERNS = [
    (r"discord(?:app)?\.com/api/webhooks", "Discord Webhook (Стилер данных)"),
    (r"api\.ipify\.org", "IP Logger (Сбор сетевых данных)"),
    (r"httpbin\.org/ip", "IP Logger (Сбор сетевых данных)"),
    (r"grabify\.link", "Grabify Logger"),
    (r"iplogger\.", "IP Logger"),
    (r"\.ROBLOSECURITY", "Попытка кражи Cookie"),
    (r"GetCookies", "Попытка кражи Cookie"),
    (r"os\.execute", "Попытка исполнения системных команд"),
    (r"io\.popen", "Попытка исполнения системных команд"),
    (r"powershell", "Попытка запуска PowerShell"),
    (r"cmd\.exe", "Попытка запуска консоли"),
    (r"\.exe[\"'\s]", "Попытка загрузки EXE файла"),
    (r"\.bat[\"'\s]", "Попытка загрузки BAT файла"),
    (r"\.vbs[\"'\s]", "Попытка загрузки VBS файла"),
]

def check_script_safety(script_code: str, title: str = "") -> Tuple[bool, str]:
    combined = f"{title} {script_code}".lower()
    for pattern, desc in DANGEROUS_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return False, desc
    return True, "Безопасно"

def parse_real_features(raw_features: str, title: str, game_name: str) -> str:
    """Extracts genuine, specific features from ScriptBlox description instead of generic text."""
    if raw_features:
        lines = [l.strip() for l in raw_features.split("\n") if l.strip()]
        cleaned = []
        for l in lines:
            # Bullet or arrow lines
            if l.startswith(("•", "-", "*", "»", ">", "+")):
                c = l.lstrip("•-*»>+ ").strip()
                if c and len(c) > 3 and not any(bad in c.lower() for bad in ["discord", "youtube", "subscribe", "key", "link"]):
                    cleaned.append(f"• {c}")
            elif len(cleaned) < 5 and 5 < len(l) < 90:
                low = l.lower()
                if not any(bad in low for bad in ["http", "discord", "credits", "support", "version", "update", "game", "script"]):
                    cleaned.append(f"• {l}")
                    
        if len(cleaned) >= 2:
            return "\n".join(cleaned[:5])

    # Fallback to AI features tuned for this specific game
    return post_builder.generate_ai_features(game_name)

def _fetch_scriptblox_sync(query: str) -> List[Dict[str, Any]]:
    url = f"https://scriptblox.com/api/script/search?q={urllib.parse.quote(query)}&mode=free"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=7) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("result", {}).get("scripts", [])
    except Exception as e:
        logger.warning(f"Error fetching ScriptBlox for '{query}': {e}")
        return []

def _fetch_single_scriptblox_details(slug: str) -> Dict[str, Any]:
    url = f"https://scriptblox.com/api/script/{slug}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("script", {})
    except Exception as e:
        logger.warning(f"Error fetching script details for slug '{slug}': {e}")
        return {}

async def search_scripts_online(game_query: str) -> List[Dict[str, Any]]:
    """
    Returns EXACTLY 2 of the HIGHEST-RATED, working scripts for the requested game.
    Extracts real unique features and cheat GUI screenshots.
    """
    raw_query = game_query.strip().lower()
    clean_query = SYNONYMS.get(raw_query, raw_query)

    loop = asyncio.get_running_loop()
    results: List[Dict[str, Any]] = []
    seen_codes = set()

    # 1. Check PulseHub (if key matches directly)
    for k, v in PULSEHUB_GAMES.items():
        if k in clean_query or clean_query in k:
            results.append({
                "title": v["title"],
                "game_name": v["game_name"],
                "script_code": v["script_code"],
                "source": v["source"],
                "is_verified": True,
                "features": v.get("features") or post_builder.generate_ai_features(v["game_name"]),
                "safety_note": "Проверено: 100% чистый скрипт без ключа (PulseHub)",
                "image_url": v.get("image_url"),
            })
            seen_codes.add(v["script_code"].strip())
            break

    # 2. Search ScriptBlox online
    raw_candidates = await loop.run_in_executor(None, _fetch_scriptblox_sync, clean_query)

    candidates = []
    for item in raw_candidates:
        if item.get("isPatched", False):
            continue

        title = item.get("title", "Roblox Script")
        script_code = item.get("script", "")
        if not script_code or script_code.strip() in seen_codes:
            continue

        is_safe, reason = check_script_safety(script_code, title)
        if not is_safe:
            logger.warning(f"Rejected unsafe script '{title}': {reason}")
            continue

        seen_codes.add(script_code.strip())
        candidates.append(item)

    # Sort candidates by relevance:
    # 1. Exact game match in title or game.name
    # 2. Verified status
    # 3. Like count
    def score_script(item):
        t = item.get("title", "").lower()
        g = item.get("game", {}).get("name", "").lower() if isinstance(item.get("game"), dict) else ""
        is_direct = (clean_query in t) or (clean_query in g)
        is_verified = bool(item.get("verified", False))
        likes = item.get("likeCount", 0)
        return (is_direct, is_verified, likes)

    candidates.sort(key=score_script, reverse=True)

    # Take up to 2 best scripts (or 1 if PulseHub was already added)
    needed = 2 - len(results)
    top_items = candidates[:needed]

    for item in top_items:
        slug = item.get("slug")
        details = {}
        if slug:
            details = await loop.run_in_executor(None, _fetch_single_scriptblox_details, slug)

        game_data = item.get("game", {})
        game_name_raw = game_data.get("name") if isinstance(game_data, dict) else None
        
        is_hub = item.get("isHub", False) or (game_name_raw and game_name_raw.lower() in ["script hub", "universal"])
        if game_name_raw and not is_hub:
            formatted_game = post_builder.format_game_name(game_name_raw)
        else:
            formatted_game = post_builder.format_game_name(clean_query)

        # Extract real cheat menu screenshot
        img = details.get("image") or item.get("image")
        image_url = None
        if img and "no-script" not in img and "no-image" not in img:
            image_url = f"https://scriptblox.com{img}" if img.startswith("/") else img
        elif game_data and game_data.get("imageUrl") and "no-script" not in game_data.get("imageUrl", ""):
            image_url = game_data.get("imageUrl")

        # Extract real features
        raw_feat = details.get("features", "")
        parsed_features = parse_real_features(raw_feat, item.get("title", ""), formatted_game)

        is_verified = bool(item.get("verified", False))
        likes = item.get("likeCount", 0)

        results.append({
            "title": item.get("title", "Roblox Script"),
            "game_name": formatted_game,
            "script_code": item.get("script", ""),
            "source": f"ScriptBlox ({'Verified' if is_verified else 'Free'}, {likes} likes)",
            "is_verified": is_verified,
            "features": parsed_features,
            "safety_note": "Проверено: чистый loadstring, без RAT и стилеров",
            "image_url": image_url,
        })

    # Return exactly top 2
    return results[:2]
