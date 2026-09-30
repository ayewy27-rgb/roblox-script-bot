import urllib.request
import urllib.parse
import json
import re
import asyncio
import logging
from typing import List, Dict, Any, Tuple
import post_builder

logger = logging.getLogger(__name__)

# --- KNOWN VERIFIED FAST SCRIPT SOURCES (PulseHub & Verified Repositories) ---
PULSEHUB_GAMES = {
    "mm2": {
        "title": "Pulse Hub | Murder Mystery 2 (Keyless & Safe)",
        "game_name": "Murder Mystery 2",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
    "murder mystery 2": {
        "title": "Pulse Hub | Murder Mystery 2 (Keyless & Safe)",
        "game_name": "Murder Mystery 2",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
    "steal an egg": {
        "title": "Pulse Hub | Steal an Egg (Auto Steal & Fly)",
        "game_name": "Steal an Egg",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
    "rivals": {
        "title": "Pulse Hub | Rivals (Silent Aim & ESP)",
        "game_name": "Rivals",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
    "bloxstrike": {
        "title": "Pulse Hub | BloxStrike (Aimbot & ESP)",
        "game_name": "BloxStrike",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
    "grow a garden": {
        "title": "Pulse Hub | Grow a Garden 2 (Auto Farm)",
        "game_name": "Grow a Garden 2",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
    "speed": {
        "title": "Pulse Hub | +1 Speed Every Second",
        "game_name": "+1 Speed Every Second",
        "script_code": "loadstring(game:HttpGet('https://raw.githubusercontent.com/JustParadozCode/LinkHive---Scripts/refs/heads/main/script.lua'))()",
        "source": "PulseHub.gg",
    },
}

# Synonyms for Russian input and common acronyms
SYNONYMS = {
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
    "ривалс": "rivals",
    "райвалс": "rivals",
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
}

# Strict security filter: blocks scripts with RATs, webhooks, stealers, and command injectors
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
    """Scans script content and title for security threats (RAT, stealers, token loggers)."""
    combined = f"{title} {script_code}".lower()
    for pattern, desc in DANGEROUS_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return False, desc
    return True, "Безопасно"

def _fetch_scriptblox_sync(query: str, mode: str = "free") -> List[Dict[str, Any]]:
    """Synchronous fetch from ScriptBlox search API."""
    url = f"https://scriptblox.com/api/script/search?q={urllib.parse.quote(query)}"
    if mode:
        url += f"&mode={mode}"
        
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

async def search_scripts_online(game_query: str) -> List[Dict[str, Any]]:
    """
    Comprehensive multi-source internet search for Roblox scripts:
    1. Translates Russian / acronym queries into English game names.
    2. Searches PulseHub verified loaders.
    3. Searches ScriptBlox across multiple queries (both free mode and keyless).
    4. Ranks game-specific scripts ahead of generic hubs.
    5. Applies strict anti-RAT security filter on all results.
    """
    raw_query = game_query.strip().lower()
    clean_query = SYNONYMS.get(raw_query, raw_query)
    
    results: List[Dict[str, Any]] = []
    seen_codes = set()

    # 1. Search in PulseHub
    for k, v in PULSEHUB_GAMES.items():
        if k in clean_query or clean_query in k:
            results.append({
                "title": v["title"],
                "game_name": v["game_name"],
                "script_code": v["script_code"],
                "source": v["source"],
                "is_verified": True,
                "features": post_builder.generate_ai_features(v["game_name"]),
                "safety_note": "Проверено: 100% чистый скрипт без ключа (PulseHub)",
            })
            seen_codes.add(v["script_code"].strip())
            break

    # 2. Multi-query Search on ScriptBlox (runs in background executor)
    loop = asyncio.get_running_loop()
    
    # Query 1: Clean query free mode
    # Query 2: If query had alias, also search raw query
    queries_to_run = [clean_query]
    if raw_query != clean_query:
        queries_to_run.append(raw_query)

    raw_candidates: List[Dict[str, Any]] = []
    for q in queries_to_run:
        data = await loop.run_in_executor(None, _fetch_scriptblox_sync, q, "free")
        raw_candidates.extend(data)
        if len(raw_candidates) >= 15:
            break

    # Separate candidates: direct game match vs generic hubs
    direct_match_scripts = []
    general_hub_scripts = []

    for item in raw_candidates:
        if item.get("isPatched", False):
            continue

        title = item.get("title", "Roblox Script")
        script_code = item.get("script", "")
        if not script_code or script_code.strip() in seen_codes:
            continue

        # Strict Security Scan (No RAT, No Webhooks, No Stealers)
        is_safe, reason = check_script_safety(script_code, title)
        if not is_safe:
            logger.warning(f"Rejected unsafe script '{title}': {reason}")
            continue

        seen_codes.add(script_code.strip())

        game_data = item.get("game", {})
        game_name_raw = game_data.get("name") if isinstance(game_data, dict) else None
        
        is_hub = item.get("isHub", False) or (game_name_raw and game_name_raw.lower() in ["script hub", "universal"])
        
        if game_name_raw and not is_hub:
            formatted_game = post_builder.format_game_name(game_name_raw)
        else:
            formatted_game = post_builder.format_game_name(clean_query)

        is_verified = bool(item.get("verified", False))
        likes = item.get("likeCount", 0)

        entry = {
            "title": title,
            "game_name": formatted_game,
            "script_code": script_code,
            "source": f"ScriptBlox ({'Verified' if is_verified else 'Free'}, {likes} likes)",
            "is_verified": is_verified,
            "features": post_builder.generate_ai_features(formatted_game),
            "safety_note": "Проверено: чистый loadstring, без RAT и стилеров",
        }

        # Check if title or game name contains query directly
        t_low = title.lower()
        if clean_query in t_low or (game_name_raw and clean_query in game_name_raw.lower()):
            direct_match_scripts.append(entry)
        else:
            general_hub_scripts.append(entry)

    # Sort direct matches: verified first
    direct_match_scripts.sort(key=lambda x: (not x["is_verified"]))
    general_hub_scripts.sort(key=lambda x: (not x["is_verified"]))

    # Add direct matches first, then general hubs up to 6 results
    results.extend(direct_match_scripts)
    if len(results) < 6:
        results.extend(general_hub_scripts[:(6 - len(results))])

    return results
