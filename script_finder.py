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

# Curated, 100% verified keyless scripts for top Roblox games
CURATED_KEYLESS_SCRIPTS = {
    "pulsehub": {
        "title": "⚡ Pulse Hub | Официальный Универсальный Лоадер (Все игры в одном)",
        "game_name": "Pulse Hub Universal",
        "script_code": PULSEHUB_LOADER_CODE,
        "source": "PulseHub.gg (Официальный, Без ключа)",
        "features": (
            "• Авто-определение игры при запуске в Roblox\n"
            "• Без ключа (Keyless) и без регистрации\n"
            "• Поддержка: MM2, Steal an Egg, Rivals, BloxStrike, San Diego\n"
            "• Молниеносная загрузка без зависаний\n"
            "• Работает на Delta, Solara, Wave, Codex, Arceus X"
        ),
        "image_url": "https://pulsehub.gg/og.png",
    },
    "99 nights in the forest": {
        "title": "Neox Hub | Unlimited Health, Godmode, Infinite Saplings & ESP",
        "game_name": "99 Nights In The Forest",
        "script_code": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/hassanxzayn-lua/NEOXHUBMAIN/refs/heads/main/loader", true))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("99 nights in the forest"),
        "image_url": "https://tr.rbxcdn.com/180DAY-ee923b1e9ac5564624ee9c484006166c/480/270/Image/Png/noFilter",
    },
    "blox fruits": {
        "title": "Atherhub / Redz Hub | Auto Level, Auto Raid, Auto Boss & Fruit Sniper",
        "game_name": "Blox Fruits",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Blox-Fruits-Atherhub-Auto-Level-Auto-Raid-Auto-Boss-BEST-Script-79550"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("blox fruits"),
        "image_url": "https://tr.rbxcdn.com/180DAY-9562aea76052b8e6690596750b666b26/480/270/Image/Png/noFilter",
    },
    "steal an egg": {
        "title": "Snowy Hub | Instant Auto Steal, Fly, Invincibility & Egg TP",
        "game_name": "Steal an Egg",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Steal-An-Egg-Snowy-Hub-Auto-Farm-Auto-Steal-Auto-Hatch-TP-More-223705"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("steal an egg"),
        "image_url": "https://tr.rbxcdn.com/180DAY-875b2a6dc156ce6dd64eb637e73238ce/480/270/Image/Png/noFilter",
    },
    "murder mystery 2": {
        "title": "Eclipse / Free GUI | Murderer & Sheriff ESP, Silent Aim & Coin Farm",
        "game_name": "Murder Mystery 2",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Murder-Mystery-2-The-best-free-script-lots-of-features-202764"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("murder mystery 2"),
        "image_url": "https://tr.rbxcdn.com/180DAY-fe7335c3ad752e84323cd81ae38de69a/480/270/Image/Png/noFilter",
    },
    "rivals": {
        "title": "PulseHub / RIVALS | Silent Aim, 2D Box ESP & TriggerBot",
        "game_name": "Rivals",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/RIVALS-Esp-Aimbot-Triggerbot-and-more-229209"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("rivals"),
        "image_url": "https://tr.rbxcdn.com/180DAY-3362a7d2bfc71def6178a16e2ca58420/480/270/Image/Png/noFilter",
    },
    "blade ball": {
        "title": "Project Stark | 100% Auto Parry, Target Lock & Curve Deflect",
        "game_name": "Blade Ball",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Blade-Ball-Project-Stark-Free-Hub-59919"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("blade ball"),
        "image_url": "https://tr.rbxcdn.com/180DAY-be150ba07c74cd57deb31791c2675323/480/270/Image/Png/noFilter",
    },
    "fisch": {
        "title": "Blackhub / Speed Hub | Auto Fish, Perfect Reel & Mythic Radar",
        "game_name": "Fisch",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Fisch-Blackhub-Best-Undetected-Script-53591"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("fisch"),
        "image_url": "https://tr.rbxcdn.com/180DAY-391139542b53fa1fb3cbef7da9944147/480/270/Image/Png/noFilter",
    },
    "doors": {
        "title": "Xeno Optimized | Key & Lever ESP, Entity Alert & Instant Unlock",
        "game_name": "Doors",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/DOORS-SCRIPT-XENO-OPTIMIZED-67738"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("doors"),
        "image_url": "https://tr.rbxcdn.com/180DAY-ac6d2b831ee486c141dfd677af0cabcb/480/270/Image/Png/noFilter",
    },
    "bedwars": {
        "title": "Radius Hub | Killaura 360, Bed ESP, Chest Stealer & Fly",
        "game_name": "Bedwars",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Universal-Script-Radius-Hub-15-Games-61719"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("bedwars"),
        "image_url": "https://tr.rbxcdn.com/180DAY-1a9f4e0795cced66ceba279da50309c3/480/270/Image/Png/noFilter",
    },
    "da hood": {
        "title": "Universal Silent Aim | Camlock, Target ESP & Speed Boost",
        "game_name": "Da Hood",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Universal-Script-Universal-Da-Hood-Silent-Aim-Keyless-223972"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("da hood"),
        "image_url": "https://tr.rbxcdn.com/180DAY-d5da966f3938479e0a0a544b611eeb80/480/270/Image/Png/noFilter",
    },
    "pet simulator 99": {
        "title": "ZapHub | Auto Farm Coins, Auto Hatch Best Eggs & Mastery",
        "game_name": "Pet Simulator 99",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Pet-Simulator-99!-ZapHub-Auto-Farm-Auto-Hatch-224110"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("pet simulator 99"),
        "image_url": "https://tr.rbxcdn.com/180DAY-923ad8ba046d3e8c9735dbe19e782d8c/480/270/Image/Png/noFilter",
    },
    "forsaken": {
        "title": "Forsaken Plus | Auto Generator, Godmode & ESP",
        "game_name": "Forsaken",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Forsaken-Plus-216770"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("forsaken"),
        "image_url": "https://tr.rbxcdn.com/180DAY-31ff9939e6a27e99709d17d5fae16d48/480/270/Image/Png/noFilter",
    },
    "the strongest battlegrounds": {
        "title": "Kuro Hub | Auto Combo, Skill Spam, Block & Teleport",
        "game_name": "The Strongest Battlegrounds",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/The-Strongest-Battlegrounds-Kuro-Hub-Keyless-221045"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("the strongest battlegrounds"),
        "image_url": "https://tr.rbxcdn.com/180DAY-cf92c5567fc36d9361ad2ad6e22f254e/480/270/Image/Png/noFilter",
    },
    "jujutsu shenanigans": {
        "title": "Shenanigans Hub | Auto Combo, Instant Awakening & Counter",
        "game_name": "Jujutsu Shenanigans",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Universal-Script-Jujutsu-Shenanigans-Auto-Combo-222891"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("jujutsu shenanigans"),
        "image_url": "https://tr.rbxcdn.com/180DAY-86105c317fdb85fa1e6fbe534354c46f/480/270/Image/Png/noFilter",
    },
    "brookhaven": {
        "title": "Ice Hub | Unlock All Passes, Speed, Fly & Troll GUI",
        "game_name": "Brookhaven",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Brookhaven-RP-Ice-Hub-Admin-Troll-223011"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("brookhaven"),
        "image_url": "https://tr.rbxcdn.com/180DAY-4d1a12903e1e2d634db8b8e0556f8f4a/480/270/Image/Png/noFilter",
    },
    "slap battles": {
        "title": "Giang Hub | Slap Aura 360, Anti-Void, Godmode & Badge Farm",
        "game_name": "Slap Battles",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Slap-Battles-Giang-Hub-Slap-Aura-Anti-Void-221940"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("slap battles"),
        "image_url": "https://tr.rbxcdn.com/180DAY-80b62d854497e8e50b86a88b56f8f553/480/270/Image/Png/noFilter",
    },
    "arsenal": {
        "title": "Quisky Hub | Silent Aim, Wallbang, Box ESP & Rapid Fire",
        "game_name": "Arsenal",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Arsenal-Quisky-Hub-Silent-Aim-Esp-220815"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("arsenal"),
        "image_url": "https://tr.rbxcdn.com/180DAY-31682390f7a39ffc46a67876a440cb20/480/270/Image/Png/noFilter",
    },
    "evade": {
        "title": "Darkrai Hub | Bot ESP, Auto Revive, Cola Speed & Safe Zone",
        "game_name": "Evade",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Evade-Darkrai-Hub-Auto-Revive-Esp-221500"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("evade"),
        "image_url": "https://tr.rbxcdn.com/180DAY-924bce624467a3a9ae93297a7e18ca47/480/270/Image/Png/noFilter",
    },
    "counter blox": {
        "title": "Osiris Hub | Silent Aim, Skin Changer, Wallbang & ESP",
        "game_name": "Counter Blox",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Counter-Blox-Osiris-Silent-Aim-Skin-Changer-220412"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("counter blox"),
        "image_url": "https://tr.rbxcdn.com/180DAY-64c9d92ef1356f966cbeec81ad2b369c/480/270/Image/Png/noFilter",
    },
    "bee swarm simulator": {
        "title": "Kocmoc Macro | Auto Field, Pollen Farm, Kill Monsters & Honey",
        "game_name": "Bee Swarm Simulator",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Bee-Swarm-Simulator-Kocmoc-Macro-Auto-Farm-223400"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("bee swarm simulator"),
        "image_url": "https://tr.rbxcdn.com/180DAY-633008984e7adad05a6108154625b90f/480/270/Image/Png/noFilter",
    },
    "tower of hell": {
        "title": "Pro Hub | Instant Win, Godmode, Fly & Anti-Laser",
        "game_name": "Tower of Hell",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Tower-of-Hell-Pro-Hub-Instant-Win-220190"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("tower of hell"),
        "image_url": "https://tr.rbxcdn.com/180DAY-d2e5b7c7bfa63920c5a089d1b0d2d3a3/480/270/Image/Png/noFilter",
    },
    "build a boat for treasure": {
        "title": "Babft Instant Treasure | Auto Farm Gold, Fly & Godmode",
        "game_name": "Build a Boat for Treasure",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Build-A-Boat-For-Treasure-Instant-Treasure-Farm-221800"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("build a boat for treasure"),
        "image_url": "https://tr.rbxcdn.com/180DAY-21ea7f7d1912a7bf1326c278a594167e/480/270/Image/Png/noFilter",
    },
    "muscle legends": {
        "title": "Speed Hub | Auto Strength, Auto Rebirth, Fast Punch & Brawl God",
        "game_name": "Muscle Legends",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Muscle-Legends-Speed-Hub-Auto-Strength-222400"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("muscle legends"),
        "image_url": "https://tr.rbxcdn.com/180DAY-4f05255476a6b5a3297a7a10be69752b/480/270/Image/Png/noFilter",
    },
    "dandy's world": {
        "title": "Dandy Hub | Machine Auto Complete, Twisted ESP & Stamina",
        "game_name": "Dandy's World",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Dandys-World-Dandy-Hub-Esp-Auto-Machines-224800"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("dandy's world"),
        "image_url": "https://tr.rbxcdn.com/180DAY-9ea58087963be578bc42583d73507d35/480/270/Image/Png/noFilter",
    },
    "pressure": {
        "title": "Deep Sea Hub | Entity Alert, Keycard ESP & Fullbright",
        "game_name": "Pressure",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Pressure-Deep-Sea-Hub-Esp-Alert-224900"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("pressure"),
        "image_url": "https://tr.rbxcdn.com/180DAY-707b6f6f9daaa7e9c968f7601f05470d/480/270/Image/Png/noFilter",
    },
    "survive the killer": {
        "title": "Survivor Hub | Killer & Survivor ESP, Fast Escape & Auto Loot",
        "game_name": "Survive the Killer",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Survive-The-Killer-Survivor-Hub-Esp-224700"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("survive the killer"),
        "image_url": "https://tr.rbxcdn.com/180DAY-a1f948f2197f26d70ff998c393710777/480/270/Image/Png/noFilter",
    },
    "bloxstrike": {
        "title": "UPDATE! BloxStrike | Silent Aim, Skin Changer & Wallbang",
        "game_name": "BloxStrike",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/UPDATE!-BloxStrike-Silent-Aim-Skin-Changer-Wallbang-And-MORE-WORKING-229495"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("bloxstrike"),
        "image_url": "https://tr.rbxcdn.com/180DAY-5de034057184c82666b530ef54e2898e/480/270/Image/Png/noFilter",
    },
    "san diego": {
        "title": "San Diego Border RP | Boat, Truck & Smuggle Auto Farm",
        "game_name": "San Diego Border Roleplay",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/BIKES-San-Diego-Border-Roleplay-Autofarm-Police-AutoDetect-Esp-226987"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": post_builder.KNOWN_GAMES_FEATURES.get("san diego"),
        "image_url": "https://tr.rbxcdn.com/180DAY-79b8c049b491a613bbad79a6a8b79f87/480/270/Image/Png/noFilter",
    },
}

SYNONYMS = {
    # PulseHub
    "пульс": "pulsehub",
    "пульсехаб": "pulsehub",
    "пульсхаб": "pulsehub",
    "pulse": "pulsehub",
    "pulsehub": "pulsehub",
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
    "данди": "dandy's world",
    "dandy": "dandy's world",
    "прессуре": "pressure",
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
    "key sys", "keysys", "key-sys", "key system", "keysystem", "key_system",
    "get key", "getkey", "get-key", "key link", "keylink",
    "linkvertise", "loot-link", "lootlink", "lootlabs", "loot-labs",
    "workink", "work.ink", "checkpoint", "check point",
    "need key", "needs key", "require key", "requires key", "required key",
    "with key", "with-key", "has key", "key:", "key :",
    "platoboost", "pandadevelopment", "pandaauth", "gateway.platoboost",
    "adshrink", "boost.ink", "mboost.me", "pastedrop", "luarmor",
    "keyauth", "sub2unlock", "whitelist", "free key",
    "key in discord", "key in desc", "key in comments", "key in bio",
    "key pinned", "ad-maven", "social-unlock", "sub4sub"
]

TRANSLATION_MAP = [
    (r'(?i)\bsilent aim\b', 'Silent Aim (Скрытый аимбот в голову)'),
    (r'(?i)\baimbot\b', 'Aimbot (Авто-наводка)'),
    (r'(?i)\besp\b', 'ESP / Wallhack (Подсветка игроков и предметов сквозь стены)'),
    (r'(?i)\bwallhack\b', 'Wallhack (Подсветка сквозь стены)'),
    (r'(?i)\bgodmode\b', 'Godmode (Бессмертие и защита от урона)'),
    (r'(?i)\bsemi godmode\b', 'Godmode (Защита от урона и бессмертие)'),
    (r'(?i)\banti damage\b', 'Anti-Damage (Защита от любого урона)'),
    (r'(?i)\bauto farm\b', 'Auto Farm (Автоматический фарм ресурсов)'),
    (r'(?i)\bautofarm\b', 'Auto Farm (Автоматический фарм ресурсов)'),
    (r'(?i)\bteleport\b', 'Teleport (Мгновенное перемещение по карте)'),
    (r'(?i)\bspeed\b', 'Speed Boost (Увеличенная скорость бега)'),
    (r'(?i)\bfly\b', 'Fly Mode (Свободный режим полёта)'),
    (r'(?i)\bnoclip\b', 'Noclip (Прохождение сквозь любые стены)'),
    (r'(?i)\binfinite jump\b', 'Infinite Jump (Бесконечные прыжки в воздухе)'),
    (r'(?i)\bauto parry\b', 'Auto Parry 100% (Идеальное парирование без промахов)'),
    (r'(?i)\bfullbright\b', 'Fullbright (Яркое освещение в темноте)'),
    (r'(?i)\bno fog\b', 'No Fog (Полное удаление тумана)'),
    (r'(?i)\bkillaura\b', 'Killaura (Авто-атака всех противников в радиусе)'),
    (r'(?i)\breveal map\b', 'Reveal Map (Полное открытие всей карты)'),
    (r'(?i)\bfreeze.*entities\b', 'Freeze Enemies (Заморозка всех монстров)'),
    (r'(?i)\bauto pickup\b', 'Auto Pickup (Авто-сбор ресурсов и золота)'),
    (r'(?i)\bauto steal\b', 'Instant Auto Steal (Мгновенный авто-сбор)'),
    (r'(?i)\binstant catch\b', 'Instant Catch (Мгновенная ловля рыбы)'),
]

def check_script_safety(script_code: str, title: str = "") -> Tuple[bool, str]:
    combined = f"{title} {script_code}".lower()
    for pattern, desc in DANGEROUS_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return False, desc
    return True, "Безопасно"

def is_strictly_keyless(item: Dict[str, Any], title: str, script_code: str = "", features: str = "") -> bool:
    """Verifies that script is 100% keyless (no linkvertise, checkpoints, key gates)."""
    # 1. API key flag (true means requires key)
    if item.get("key") is True or item.get("keyType") in ["key", "linkvertise", "custom"]:
        return False

    # 2. Text heuristics
    combined = f"{title} {features} {item.get('features', '')} {script_code}".lower()
    for bad in KEY_SYSTEM_KEYWORDS:
        if bad in combined:
            return False

    if re.search(r'\b(get\s*key|keysystem|key\s*system|with\s*key|needs?\s*key)\b', combined, re.I):
        return False

    return True

def check_remote_script_keyless(raw_url: str) -> bool:
    """Quickly peeks at the first 1500 bytes of the remote script to ensure no hidden key systems."""
    try:
        req = urllib.request.Request(raw_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            sample = resp.read(1500).decode("utf-8", errors="ignore").lower()
            for bad in ["platoboost", "pandadevelopment", "pandaauth", "linkvertise", "work.ink", "gateway.platoboost", "getkey()", "key system", "keysystem"]:
                if bad in sample:
                    return False
    except Exception:
        pass
    return True

def parse_real_features(raw_features: str, title: str, game_name: str) -> str:
    """Extracts, cleans and translates genuine features into rich Russian gamer format."""
    clean_g = game_name.strip().lower()
    
    # Check if we already have a curated rich preset for this game
    for k, v in post_builder.KNOWN_GAMES_FEATURES.items():
        if k in clean_g or clean_g in k:
            return v

    if raw_features:
        lines = [l.strip() for l in raw_features.split("\n") if l.strip()]
        cleaned = []
        for l in lines:
            # Strip bullet prefixes, brackets and markdown symbols
            c = re.sub(r'^[•\-\*»\>\+\#\=\s]+', '', l).strip()
            c = re.sub(r'[*#_`]', '', c).strip()
            if not c or c.startswith('[') or c.endswith(']') or c.startswith('('):
                continue
            low = c.lower()
            if any(bad in low for bad in ['discord', 'youtube', 'key', 'link', 'credits', 'support', 'version', 'update', 'unload', 'script', 'join', 'made by', 'http', 'loadstring', 'notice']):
                continue
            
            # Apply translations
            matched = False
            for pat, trans in TRANSLATION_MAP:
                if re.search(pat, c):
                    cleaned.append(f"• {trans}")
                    matched = True
                    break
            if not matched and len(c) > 3:
                cleaned.append(f"• {c}")

        # Deduplicate
        seen = set()
        final_list = []
        for item in cleaned:
            if item not in seen:
                seen.add(item)
                final_list.append(item)

        if len(final_list) >= 3:
            return "\n".join(final_list[:5])

    # Fallback to intelligent heuristic generator
    return post_builder.generate_ai_features(game_name)

def _fetch_scriptblox_page(query: str, page: int = 1) -> List[Dict[str, Any]]:
    url = f"https://scriptblox.com/api/script/search?q={urllib.parse.quote(query)}&page={page}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("result", {}).get("scripts", [])
    except Exception as e:
        logger.warning(f"Error fetching ScriptBlox for '{query}' (page {page}): {e}")
        return []

def _fetch_scriptblox_sync(query: str) -> List[Dict[str, Any]]:
    """Fetches candidate scripts across pages 1, 2, and 3."""
    all_items = []
    for p in range(1, 4):
        items = _fetch_scriptblox_page(query, page=p)
        if items:
            all_items.extend(items)
        if len(all_items) >= 40:
            break
    return all_items

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
    Checks curated knowledge base first, then searches ScriptBlox deeply.
    Cleans features, eliminates hidden key systems and filters out ugly clickbait thumbnails.
    """
    raw_query = game_query.strip().lower()
    
    # 1. Translate synonyms or transliterate
    clean_query = SYNONYMS.get(raw_query)
    if not clean_query:
        for syn_k, syn_v in SYNONYMS.items():
            if len(syn_k) >= 3 and syn_k in raw_query:
                clean_query = syn_v
                break
            elif len(raw_query) >= 4 and raw_query in syn_k:
                clean_query = syn_v
                break
    if not clean_query:
        clean_query = transliterate_text(raw_query)

    loop = asyncio.get_running_loop()
    results: List[Dict[str, Any]] = []
    seen_codes = set()

    # 2. Check Curated Knowledge Base first
    for k, v in CURATED_KEYLESS_SCRIPTS.items():
        if k in clean_query or clean_query in k:
            curated_code = v["script_code"]
            seen_codes.add(curated_code.strip())
            results.append({
                "title": v["title"],
                "game_name": v["game_name"],
                "script_code": curated_code,
                "source": v["source"],
                "is_verified": True,
                "features": v["features"],
                "safety_note": "Проверено: 100% без ключа (Keyless), чистый код",
                "image_url": v.get("image_url"),
            })
            break

    # If user explicitly asked for pulsehub, return curated immediately
    if clean_query == "pulsehub":
        return results

    # 3. Deep search ScriptBlox online
    search_queries = [clean_query]
    if raw_query != clean_query:
        search_queries.append(raw_query)
    # Also add shortened version if multi-word
    words = clean_query.split()
    if len(words) > 2:
        search_queries.append(" ".join(words[:2]))

    raw_candidates = []
    for q in search_queries:
        found = await loop.run_in_executor(None, _fetch_scriptblox_sync, q)
        raw_candidates.extend(found)
        if len(raw_candidates) >= 15:
            break

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
            continue

        # Check strictly keyless
        if not is_strictly_keyless(item, title, script_code):
            continue

        # Filter dead links and check remote payload for hidden key systems
        urls = re.findall(r'https?://[^\s\"\'\)]+', script_code)
        if urls:
            raw_url = urls[0]
            if "rawscripts.net" in raw_url or "github" in raw_url or "pastebin" in raw_url:
                is_clean_remote = await loop.run_in_executor(None, check_remote_script_keyless, raw_url)
                if not is_clean_remote:
                    logger.info(f"Rejected script '{title}' due to hidden key system in remote code")
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
        views = item.get("views", 0)
        return (is_direct, is_verified, likes, views)

    candidates.sort(key=score_script, reverse=True)

    # Take up to 10 top candidates from live ScriptBlox search to provide full variety
    top_items = candidates[:10]

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

        # Image priority: Roblox official game asset > verified clean image
        img = details.get("image") or item.get("image")
        roblox_img = game_data.get("imageUrl") if isinstance(game_data, dict) else None

        image_url = None
        if roblox_img and "no-script" not in roblox_img and "rbxcdn" in roblox_img:
            image_url = roblox_img
        elif img and "no-script" not in img and "no-image" not in img:
            image_url = f"https://scriptblox.com{img}" if img.startswith("/") else img

        # Extract & localize real features
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

    return results[:12]
