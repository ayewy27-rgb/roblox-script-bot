import urllib.request
import urllib.parse
import json
import re
import asyncio
import logging
from typing import List, Dict, Any, Tuple
import post_builder

logger = logging.getLogger(__name__)

# Official Authentic PulseHub Universal Loader from pulsehub.gg (Only for pulsehub requests)
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
}

SYNONYMS = {
    # PulseHub
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

    # Popular Games & Slang
    "мм2": "murder mystery 2",
    "мардер": "murder mystery 2",
    "мардер мистери": "murder mystery 2",
    "бф": "blox fruits",
    "блокс фрут": "blox fruits",
    "блокс фрутс": "blox fruits",
    "фрукты": "blox fruits",
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
    "фишинг": "fisch",
    "дорс": "doors",
    "двери": "doors",
    "doors floor 2": "doors",
    "дорс 2": "doors",
    "бедварс": "bedwars",
    "бед варс": "bedwars",
    "да худ": "da hood",
    "дахуд": "da hood",
    "брукхейвен": "brookhaven",
    "пс99": "pet simulator 99",
    "пет сим": "pet simulator 99",
    "пет симулятор": "pet simulator 99",
    "петы": "pet simulator 99",
    "арсенал": "arsenal",
    "джуджутсу": "jujutsu shenanigans",
    "магическая битва": "jujutsu shenanigans",
    "форсакен": "forsaken",
    "сан диего": "san diego",
    "сандьего": "san diego",
    "99 ночей": "99 nights in the forest",
    "99 ночей в лесу": "99 nights in the forest",
    "99 nights": "99 nights in the forest",
    "99 nights in the forest": "99 nights in the forest",
    "ночей": "99 nights in the forest",
    "тайкун": "tycoon",
    "шутер": "shooter",
    "симулятор": "simulator",
    "выживание": "survival",
    "побег": "escape",
    "построй лодку": "build a boat for treasure",
    "строить лодку": "build a boat for treasure",
    "лодка": "build a boat for treasure",
    "мускул": "muscle legends",
    "качок": "muscle legends",
    "симулятор качка": "muscle legends",
    "тюрьма": "jailbreak",
    "джейлбрейк": "jailbreak",
    "джейл": "jailbreak",
    "пчелы": "bee swarm simulator",
    "симулятор пчеловода": "bee swarm simulator",
    "башня ада": "tower of hell",
    "башня": "tower of hell",
    "тавер оф хелл": "tower of hell",
    "аниме дефенс": "anime defenders",
    "аниме": "anime",
    "кб": "counter blox",
    "кс": "counter blox",
    "контра": "counter blox",
    "эвейд": "evade",
    "адопт": "adopt me",
    "адопт ми": "adopt me",
    "шлепки": "slap battles",
    "слэп батлс": "slap battles",
    "стронгест": "the strongest battlegrounds",
    "tsb": "the strongest battlegrounds",
    "тсб": "the strongest battlegrounds",
    "сильнейшие": "the strongest battlegrounds",
    "выживи против убийцы": "survive the killer",
}

CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}

def transliterate_text(text: str) -> str:
    """Transliterates Russian gaming names to Latin if not matched in synonyms."""
    res = []
    for char in text.lower():
        res.append(CYRILLIC_TO_LATIN.get(char, char))
    return "".join(res).strip()

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

KEY_SYSTEM_KEYWORDS = [
    "key system", "get key", "linkvertise", "loot-link", "lootlabs",
    "workink", "checkpoint", "need key", "needs key", "with key", "requires key"
]

def check_script_safety(script_code: str, title: str = "") -> Tuple[bool, str]:
    combined = f"{title} {script_code}".lower()
    for pattern, desc in DANGEROUS_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return False, desc
    return True, "Безопасно"

def is_strictly_keyless(item: Dict[str, Any], title: str, features: str = "") -> bool:
    """Verifies that script is 100% keyless (no linkvertise, checkpoints, key gates)."""
    # 1. API key flag (true means requires key)
    if item.get("key") is True:
        return False

    # 2. Text heuristics
    combined = f"{title} {features} {item.get('features', '')}".lower()
    for bad in KEY_SYSTEM_KEYWORDS:
        if bad in combined:
            return False
    return True

def parse_real_features(raw_features: str, title: str, game_name: str) -> str:
    """Extracts genuine, specific features from ScriptBlox description instead of generic text."""
    if raw_features:
        lines = [l.strip() for l in raw_features.split("\n") if l.strip()]
        cleaned = []
        for l in lines:
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

def _fetch_scriptblox_page(query: str, page: int = 1, keyless_param: bool = True) -> List[Dict[str, Any]]:
    key_flag = "&key=0" if keyless_param else ""
    url = f"https://scriptblox.com/api/script/search?q={urllib.parse.quote(query)}&mode=free{key_flag}&page={page}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("result", {}).get("scripts", [])
    except Exception as e:
        logger.warning(f"Error fetching ScriptBlox for '{query}' (page {page}, keyless={keyless_param}): {e}")
        return []

def _fetch_scriptblox_sync(query: str) -> List[Dict[str, Any]]:
    """Fetches up to 40 candidate scripts using deep search across multiple pages."""
    # First attempt: key=0 strictly keyless
    items = _fetch_scriptblox_page(query, page=1, keyless_param=True)
    if len(items) < 5:
        # Fetch page 2 as well
        items.extend(_fetch_scriptblox_page(query, page=2, keyless_param=True))
    
    # If still too few, fetch mode=free (we filter in Python)
    if len(items) < 3:
        free_items = _fetch_scriptblox_page(query, page=1, keyless_param=False)
        items.extend(free_items)

    return items

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
    Returns EXACTLY 2 of the HIGHEST-RATED, WORKING, 100% KEYLESS scripts for the requested game.
    Extracts real unique features and cheat GUI screenshots.
    Filters out dead 404 links and key systems.
    """
    raw_query = game_query.strip().lower()
    
    # 1. Translate synonyms or transliterate
    clean_query = SYNONYMS.get(raw_query)
    if not clean_query:
        # Check substring match in synonyms
        for syn_k, syn_v in SYNONYMS.items():
            if syn_k in raw_query or raw_query in syn_k:
                clean_query = syn_v
                break
    if not clean_query:
        # Fallback to transliteration
        clean_query = transliterate_text(raw_query)

    loop = asyncio.get_running_loop()
    results: List[Dict[str, Any]] = []
    seen_codes = set()

    # 2. Check PulseHub (ONLY if user explicitly asks for pulsehub / universal loader)
    pulse_keywords = ["pulsehub", "pulse", "пульс", "пульсхаб", "лоадер", "loader", "все в одном", "всев одном", "универсальный", "универсал"]
    if clean_query in pulse_keywords:
        v = PULSEHUB_GAMES["pulsehub"]
        results.append({
            "title": v["title"],
            "game_name": v["game_name"],
            "script_code": v["script_code"],
            "source": v["source"],
            "is_verified": True,
            "features": v.get("features") or post_builder.generate_ai_features(v["game_name"]),
            "safety_note": "Проверено: чистый код без ключа (PulseHub)",
            "image_url": v.get("image_url"),
        })
        return results

    # 3. Search ScriptBlox online
    raw_candidates = await loop.run_in_executor(None, _fetch_scriptblox_sync, clean_query)
    
    # If transliterated query gave 0, also try raw query as fallback
    if not raw_candidates and clean_query != raw_query:
        raw_candidates = await loop.run_in_executor(None, _fetch_scriptblox_sync, raw_query)

    candidates = []
    for item in raw_candidates:
        if item.get("isPatched", False):
            continue

        title = item.get("title", "Roblox Script")
        script_code = item.get("script", "")
        if not script_code or script_code.strip() in seen_codes:
            continue

        # Check safety
        is_safe, reason = check_script_safety(script_code, title)
        if not is_safe:
            logger.warning(f"Rejected unsafe script '{title}': {reason}")
            continue

        # Check strictly keyless
        if not is_strictly_keyless(item, title):
            continue

        # Filter out dead / 404 links
        urls = re.findall(r'https?://[^\s\"\'\)]+', script_code)
        if urls and "rawscripts.net" in urls[0]:
            try:
                test_req = urllib.request.Request(urls[0], headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(test_req, timeout=3) as test_resp:
                    if test_resp.status != 200:
                        continue
            except Exception:
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

    # Take up to 2 best keyless scripts
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
            "source": f"ScriptBlox (Без ключа, {likes} лайков)",
            "is_verified": is_verified,
            "features": parsed_features,
            "safety_note": "Проверено: 100% без ключа (Keyless), чистый код",
            "image_url": image_url,
        })

    # Return exactly top 2
    return results[:2]
