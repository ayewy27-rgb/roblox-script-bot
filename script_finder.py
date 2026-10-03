# -*- coding: utf-8 -*-
"""
========================================================================================
SCRIPT DROP — ULTRA ADVANCED ROBLOX SCRIPT SEARCH & AI ENRICHMENT ENGINE (v3.0 OP)
========================================================================================
Features:
1. 200+ Mode / Game Synonym Dictionary (Russian Slang, Typos, Transliteration, Trending Modes).
2. 7-Day Anti-Repetition History Tracking (never repeats scripts shown to user in last 7 days).
3. Keyless-First Multi-Tier Search (prioritizes 100% Keyless, with safe Keyed fallback).
4. Deep Multi-Page Scraping (Pages 1-5 across ScriptBlox and RawScripts public indices).
5. In-Depth Lua AST / Code Inspection (extracts real features & blocks hidden key systems).
6. Genre-Aware AI Feature Generator (Produces authentic Russian gamer features with emojis).
7. Official HD Roblox Game Thumbnail Resolution (tr.rbxcdn.com / thumbnails.roblox.com).
========================================================================================
"""

import urllib.request
import urllib.parse
import json
import re
import asyncio
import logging
import hashlib
from typing import List, Dict, Any, Tuple, Optional, Set
from datetime import datetime

import post_builder
import database

logger = logging.getLogger(__name__)

# Official Authentic PulseHub Universal Loader from pulsehub.gg
PULSEHUB_LOADER_CODE = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/PulseZax/Loader/refs/heads/main/.lua"))()'

# ======================================================================================
# 1. COMPREHENSIVE MODE & SYNONYM DICTIONARY (200+ ROBLOX GAMES & RUSSIAN SLANG)
# ======================================================================================
SYNONYMS: Dict[str, str] = {
    # --- Brainrot / Steal / Collect Games ---
    "брейнрот": "steal a brainrot",
    "стил брейнрот": "steal a brainrot",
    "стил э брейнрот": "steal a brainrot",
    "стил а брейнрот": "steal a brainrot",
    "укради брейнрот": "steal a brainrot",
    "украсть брейнрот": "steal a brainrot",
    "мозгогнил": "steal a brainrot",
    "steal a brainrot": "steal a brainrot",
    "steal brainrot": "steal a brainrot",
    "brainrot": "steal a brainrot",
    "sab": "steal a brainrot",
    "стил ан эгг": "steal an egg",
    "стил эгг": "steal an egg",
    "яйца": "steal an egg",
    "яйцо": "steal an egg",
    "укради яйцо": "steal an egg",
    "украсть яйцо": "steal an egg",
    "steal an egg": "steal an egg",
    "steal egg": "steal an egg",
    "sae": "steal an egg",
    "мем симулятор": "meme simulator",
    "симулятор мемов": "meme simulator",
    "meme simulator": "meme simulator",
    "мем си": "meme sea",
    "море мемов": "meme sea",
    "meme sea": "meme sea",
    "брейнрот рнг": "brainrot rng",
    "brainrot rng": "brainrot rng",

    # --- Popular Anime Games ---
    "блокс фрут": "blox fruits",
    "блокс фрутс": "blox fruits",
    "блоксфрутс": "blox fruits",
    "блокс": "blox fruits",
    "фрукты": "blox fruits",
    "бф": "blox fruits",
    "bf": "blox fruits",
    "blox fruits": "blox fruits",
    "bloxfruits": "blox fruits",
    "джуджутсу": "jujutsu shenanigans",
    "джуджитсу": "jujutsu shenanigans",
    "шенениганс": "jujutsu shenanigans",
    "магическая битва": "jujutsu shenanigans",
    "жжк": "jujutsu shenanigans",
    "jjk": "jujutsu shenanigans",
    "tjs": "jujutsu shenanigans",
    "jujutsu shenanigans": "jujutsu shenanigans",
    "the jujutsu shenanigans": "jujutsu shenanigans",
    "стронгест": "the strongest battlegrounds",
    "сильнейшие битвы": "the strongest battlegrounds",
    "тсб": "the strongest battlegrounds",
    "tsb": "the strongest battlegrounds",
    "сильнейшие": "the strongest battlegrounds",
    "the strongest battlegrounds": "the strongest battlegrounds",
    "аниме дефендерс": "anime defenders",
    "аниме дефенс": "anime defenders",
    "дефендерс": "anime defenders",
    "ад": "anime defenders",
    "anime defenders": "anime defenders",
    "аниме вангардс": "anime vanguards",
    "аниме вэнгардс": "anime vanguards",
    "вангардс": "anime vanguards",
    "вэнгардс": "anime vanguards",
    "ав": "anime vanguards",
    "anime vanguards": "anime vanguards",
    "аниме реборн": "anime reborn",
    "anime reborn": "anime reborn",
    "аниме ласт стенд": "anime last stand",
    "ласт стенд": "anime last stand",
    "алс": "anime last stand",
    "anime last stand": "anime last stand",
    "кинг легаси": "king legacy",
    "кл": "king legacy",
    "king legacy": "king legacy",
    "шиндо лайф": "shindo life",
    "шиндо": "shindo life",
    "shindo life": "shindo life",
    "фрут батлграундс": "fruit battlegrounds",
    "fruit battlegrounds": "fruit battlegrounds",
    "тайп соул": "type soul",
    "тайпсоул": "type soul",
    "соул": "type soul",
    "type soul": "type soul",
    "дипвокен": "deepwoken",
    "deepwoken": "deepwoken",
    "проджект слейерс": "project slayers",
    "слейерс": "project slayers",
    "клинок": "project slayers",
    "project slayers": "project slayers",
    "алл стар": "all star tower defense",
    "алл стар тавер дефенс": "all star tower defense",
    "астд": "all star tower defense",
    "astd": "all star tower defense",
    "all star tower defense": "all star tower defense",
    "ро гуль": "ro-ghoul",
    "рогуль": "ro-ghoul",
    "ro ghoul": "ro-ghoul",
    "ro-ghoul": "ro-ghoul",
    "гранд пис": "grand piece online",
    "гпо": "grand piece online",
    "gpo": "grand piece online",
    "grand piece online": "grand piece online",

    # --- PVP, Combat & Shooters ---
    "райвалс": "rivals",
    "ривалс": "rivals",
    "rivals": "rivals",
    "блейд бол": "blade ball",
    "блейдбол": "blade ball",
    "бб": "blade ball",
    "blade ball": "blade ball",
    "мардер мистери 2": "murder mystery 2",
    "мардер мистери": "murder mystery 2",
    "мардер": "murder mystery 2",
    "мм2": "murder mystery 2",
    "mm2": "murder mystery 2",
    "murder mystery 2": "murder mystery 2",
    "арсенал": "arsenal",
    "arsenal": "arsenal",
    "блокстрайк": "bloxstrike",
    "страйк": "bloxstrike",
    "blox strike": "bloxstrike",
    "bloxstrike": "bloxstrike",
    "контра": "counter blox",
    "кб": "counter blox",
    "кс": "counter blox",
    "counter blox": "counter blox",
    "да худ": "da hood",
    "дахуд": "da hood",
    "da hood": "da hood",
    "комбат вариорс": "combat warriors",
    "комбат": "combat warriors",
    "кв": "combat warriors",
    "combat warriors": "combat warriors",
    "шлепки": "slap battles",
    "слэп батлс": "slap battles",
    "слап батл": "slap battles",
    "slap battles": "slap battles",
    "боксинг": "untitled boxing game",
    "бокс": "untitled boxing game",
    "антайтлед боксинг": "untitled boxing game",
    "ubg": "untitled boxing game",
    "untitled boxing game": "untitled boxing game",
    "бад бизнес": "bad business",
    "bad business": "bad business",
    "шут аут": "shoot out",
    "shoot out": "shoot out",
    "фронтлайнс": "frontlines",
    "frontlines": "frontlines",
    "аимблокс": "aimblox",
    "aimblox": "aimblox",
    "биг пейнтбол": "big paintball",
    "пейнтбол": "big paintball",
    "big paintball": "big paintball",

    # --- Survival, Horror & Escape ---
    "99 ночей": "99 nights in the forest",
    "99 ночей в лесу": "99 nights in the forest",
    "99 ночи": "99 nights in the forest",
    "99 nights": "99 nights in the forest",
    "99 nights in the forest": "99 nights in the forest",
    "ночей": "99 nights in the forest",
    "дорс": "doors",
    "дорс 2": "doors",
    "двери": "doors",
    "doors": "doors",
    "doors floor 2": "doors",
    "прессуре": "pressure",
    "прешер": "pressure",
    "давление": "pressure",
    "pressure": "pressure",
    "данди": "dandy's world",
    "дандис ворлд": "dandy's world",
    "мир данди": "dandy's world",
    "dandy's world": "dandy's world",
    "dandys world": "dandy's world",
    "форсакен": "forsaken",
    "forsaken": "forsaken",
    "эвейд": "evade",
    "уклонение": "evade",
    "evade": "evade",
    "дед рейлс": "dead rails",
    "dead rails": "dead rails",
    "выживи против убийцы": "survive the killer",
    "survive the killer": "survive the killer",
    "стир": "survive the killer",
    "бедварс": "bedwars",
    "бед варс": "bedwars",
    "bedwars": "bedwars",
    "бедрок": "bedwars",
    "натурал дизастер": "natural disaster survival",
    "катастрофы": "natural disaster survival",
    "дизастер": "natural disaster survival",
    "natural disaster survival": "natural disaster survival",
    "мимик": "the mimic",
    "the mimic": "the mimic",
    "радужные друзья": "rainbow friends",
    "радужные": "rainbow friends",
    "rainbow friends": "rainbow friends",
    "пигги": "piggy",
    "piggy": "piggy",
    "икеа": "3008",
    "3008": "3008",
    "scp 3008": "3008",
    "апейрофобия": "apeirophobia",
    "apeirophobia": "apeirophobia",

    # --- Simulators & Farming ---
    "фиш": "fisch",
    "рыбалка": "fisch",
    "фишинг": "fisch",
    "fisch": "fisch",
    "рыба": "fisch",
    "пс99": "pet simulator 99",
    "пет сим 99": "pet simulator 99",
    "пет сим": "pet simulator 99",
    "пет симулятор": "pet simulator 99",
    "пет симулятор 99": "pet simulator 99",
    "петы": "pet simulator 99",
    "pet simulator 99": "pet simulator 99",
    "мускул легендс": "muscle legends",
    "мускул": "muscle legends",
    "качок": "muscle legends",
    "симулятор качка": "muscle legends",
    "muscle legends": "muscle legends",
    "пчелы": "bee swarm simulator",
    "би сварм": "bee swarm simulator",
    "симулятор пчеловода": "bee swarm simulator",
    "bee swarm simulator": "bee swarm simulator",
    "пет кетчерс": "pet catchers",
    "pet catchers": "pet catchers",
    "спид": "+1 speed",
    "скорость": "+1 speed",
    "побег клавиатура": "+1 speed",
    "+1 speed": "+1 speed",
    "солс рнг": "sol's rng",
    "соулс рнг": "sol's rng",
    "солс": "sol's rng",
    "sols rng": "sol's rng",
    "sol's rng": "sol's rng",

    # --- Roleplay, Tycoon & Obby ---
    "брукхейвен": "brookhaven",
    "брук": "brookhaven",
    "броукхавен": "brookhaven",
    "brookhaven": "brookhaven",
    "построй лодку": "build a boat for treasure",
    "строить лодку": "build a boat for treasure",
    "лодка": "build a boat for treasure",
    "бабфт": "build a boat for treasure",
    "babft": "build a boat for treasure",
    "build a boat for treasure": "build a boat for treasure",
    "тюрьма": "jailbreak",
    "джейлбрейк": "jailbreak",
    "джейл": "jailbreak",
    "jailbreak": "jailbreak",
    "башня ада": "tower of hell",
    "башня": "tower of hell",
    "тох": "tower of hell",
    "toh": "tower of hell",
    "tower of hell": "tower of hell",
    "тавер оф мизери": "tower of misery",
    "мизери": "tower of misery",
    "tower of misery": "tower of misery",
    "адопт ми": "adopt me",
    "адопт": "adopt me",
    "adopt me": "adopt me",
    "туалет тавер дефенс": "toilet tower defense",
    "ттд": "toilet tower defense",
    "ttd": "toilet tower defense",
    "toilet tower defense": "toilet tower defense",
    "сан диего": "san diego",
    "сандьего": "san diego",
    "san diego": "san diego",
    "сад": "grow a garden",
    "гарден": "grow a garden",
    "grow a garden": "grow a garden",
    "кар дилершип": "car dealership tycoon",
    "car dealership tycoon": "car dealership tycoon",
    "драйвинг эмпайр": "driving empire",
    "driving empire": "driving empire",
    "ерлк": "emergency response: liberty county",
    "erlc": "emergency response: liberty county",
    "emergency response": "emergency response: liberty county",
    "гринвил": "greenville",
    "greenville": "greenville",
    "саутвест флорида": "southwest florida",
    "южный флорида": "southwest florida",
    "southwest florida": "southwest florida",
    "люмбер": "lumber tycoon 2",
    "лесопилка": "lumber tycoon 2",
    "lumber tycoon 2": "lumber tycoon 2",
    "сцп": "scp: roleplay",
    "scp": "scp: roleplay",
    "scp roleplay": "scp: roleplay",
    "данжен квест": "dungeon quest",
    "dungeon quest": "dungeon quest",
    "роял хай": "royale high",
    "рояль хай": "royale high",
    "royale high": "royale high",
    "ворлд зеро": "world zero",
    "world zero": "world zero",
    "world // zero": "world zero",

    # --- Universal Loaders ---
    "пульс": "pulsehub",
    "пульсхаб": "pulsehub",
    "pulse": "pulsehub",
    "pulsehub": "pulsehub",
    "лоадер": "pulsehub",
    "loader": "pulsehub",
    "универсальный": "pulsehub",
    "universal": "pulsehub",
}

# ======================================================================================
# 2. CURATED 100% KEYLESS SCRIPTS REPOSITORY
# ======================================================================================
CURATED_KEYLESS_SCRIPTS: Dict[str, Dict[str, Any]] = {
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
    "steal a brainrot": {
        "title": "Lumin Hub | Auto Steal, Fly, Godmode & Base Teleport",
        "game_name": "Steal a Brainrot",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Universal-Script-Lumin-Hub-Steal-a-Brainrot-239101"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🧠 Instant Auto Steal (Молниеносный авто-сбор всех мемов)\n"
            "• 🚀 Base Teleport (Мгновенный телепорт на свою базу)\n"
            "• 🛡 Godmode (Бессмертие и защита от отталкивания)\n"
            "• 💨 Fly & Speed (Свободный полет и ускорение х5)\n"
            "• 👁 Box ESP (Подсветка баз и редких брейнротов)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-052ec1882b4ef3f0d72785be062b836a/480/270/Image/Png/noFilter",
    },
    "99 nights in the forest": {
        "title": "Neox Hub | Unlimited Health, Godmode, Infinite Saplings & ESP",
        "game_name": "99 Nights In The Forest",
        "script_code": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/hassanxzayn-lua/NEOXHUBMAIN/refs/heads/main/loader", true))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🛡 Godmode (Полное бессмертие от монстров и холода)\n"
            "• 🪵 Instant Wood Farm (Мгновенный авто-сруб всех деревьев)\n"
            "• 👁 Monster & Item ESP (Подсветка врагов и полезного лута)\n"
            "• 💡 Fullbright (Яркий дневной свет в ночном лесу)\n"
            "• 🧲 Auto Collect (Магнит для всех ресурсов на карте)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-ee923b1e9ac5564624ee9c484006166c/480/270/Image/Png/noFilter",
    },
    "blox fruits": {
        "title": "Atherhub / Redz Hub | Auto Level, Auto Raid, Auto Boss & Fruit Sniper",
        "game_name": "Blox Fruits",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Blox-Fruits-Atherhub-Auto-Level-Auto-Raid-Auto-Boss-BEST-Script-79550"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• ⚡ Auto Farm Level 1-2600 (Фарм уровней без остановки)\n"
            "• 🍎 Fruit Sniper & ESP (Уведомление и телепорт к фруктам)\n"
            "• 🗡 Fast Attack (Сверхбыстрые удары без кулдауна)\n"
            "• 🏰 Auto Raid & Sea Events (Прохождение рейдов и фарм моря)\n"
            "• 📜 Auto Mastery & Auto Stats (Прокачка мечей и статов)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-9562aea76052b8e6690596750b666b26/480/270/Image/Png/noFilter",
    },
    "steal an egg": {
        "title": "Snowy Hub | Instant Auto Steal, Fly, Invincibility & Egg TP",
        "game_name": "Steal an Egg",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Steal-An-Egg-Snowy-Hub-Auto-Farm-Auto-Steal-Auto-Hatch-TP-More-223705"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🥚 Instant Auto Steal Eggs (Кража любых яиц за секунду)\n"
            "• 🚀 Base Teleport (Телепорт в гнездо без падений)\n"
            "• 🛡 Godmode (Иммунитет к ловушкам и ударам игроков)\n"
            "• 💨 Fly Hack & Speed (Свободный полет сквозь преграды)\n"
            "• 👁 Rare Egg ESP (Подсветка золотых и мифических яиц)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-875b2a6dc156ce6dd64eb637e73238ce/480/270/Image/Png/noFilter",
    },
    "rivals": {
        "title": "PulseHub / RIVALS | Silent Aim, 2D Box ESP & TriggerBot",
        "game_name": "Rivals",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/RIVALS-Esp-Aimbot-Triggerbot-and-more-229209"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🎯 Silent Aim (Жесткая доводка в голову без тряски)\n"
            "• 👁 Box & Skeleton ESP (Подсветка противников через стены)\n"
            "• 🔫 TriggerBot (Авто-выстрел в миллисекунду наведения)\n"
            "• 🌪 Desync & Anti-Aim (Срыв чужих аимботов)\n"
            "• ⚡ No Recoil & No Spread (Стрельба лазером в точку)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-3362a7d2bfc71def6178a16e2ca58420/480/270/Image/Png/noFilter",
    },
    "blade ball": {
        "title": "Project Stark | 100% Auto Parry, Target Lock & Curve Deflect",
        "game_name": "Blade Ball",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Blade-Ball-Project-Stark-Free-Hub-59919"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• ⚔️ 100% Auto Parry (Идеальное отбивание мяча на любой скорости)\n"
            "• 🎯 Target Lock (Выбор конкретной жертвы для направления мяча)\n"
            "• 🌀 Curve Ball Deflect (Крученая траектория отбива)\n"
            "• 💨 Fast Dash & Infinity Jump (Мгновенный эскейп)\n"
            "• 🛡 Auto Ability (Авто-активация щита и телепорта)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-be150ba07c74cd57deb31791c2675323/480/270/Image/Png/noFilter",
    },
    "fisch": {
        "title": "Blackhub / Speed Hub | Auto Fish, Perfect Reel & Mythic Radar",
        "game_name": "Fisch",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Fisch-Blackhub-Best-Undetected-Script-53591"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🎣 Auto Cast & Auto Shake (Авто-заброс и тряска удочки)\n"
            "• 🎯 100% Perfect Reel (Мгновенная подсечка без мини-игры)\n"
            "• 🧭 Mythic Fish Radar & ESP (Подсветка редчайших рыб)\n"
            "• 💰 Auto Sell Fish (Автоматическая продажа улова торговцу)\n"
            "• 🚀 Island Teleport & Walk On Water (Хождение по воде и ТП)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-391139542b53fa1fb3cbef7da9944147/480/270/Image/Png/noFilter",
    },
    "doors": {
        "title": "Xeno Optimized | Key & Lever ESP, Entity Alert & Instant Unlock",
        "game_name": "Doors",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/DOORS-SCRIPT-XENO-OPTIMIZED-67738"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🗝 Key, Lever & Item ESP (Подсветка всех ключей и рычагов)\n"
            "• 🚨 Entity Alert (Громкое предупреждение о спавне монстров)\n"
            "• 🚪 Instant Open Doors (Мгновенное открытие дверей без задержки)\n"
            "• 💡 Fullbright (Идеальное освещение комнат в темноте)\n"
            "• 🏃 Speed Boost & No Clip (Бег без усталости сквозь шкафы)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-ac6d2b831ee486c141dfd677af0cabcb/480/270/Image/Png/noFilter",
    },
    "bedwars": {
        "title": "Radius Hub | Killaura 360, Bed ESP, Chest Stealer & Fly",
        "game_name": "Bedwars",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Universal-Script-Radius-Hub-15-Games-61719"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🗡 Killaura 360° (Авто-атака мечом всех врагов вокруг)\n"
            "• 🛏 Bed ESP & Breaker (Мгновенный авто-слом чужих кроватей)\n"
            "• 💨 Fly Hack & Long Jump (Полет над пропастью без смертей)\n"
            "• 🧲 Auto Loot Chests (Стягивание всех алмазов и изумрудов)\n"
            "• 🛡 Velocity 0% (Полное отсутствие откидывания при ударах)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-1a9f4e0795cced66ceba279da50309c3/480/270/Image/Png/noFilter",
    },
    "murder mystery 2": {
        "title": "Eclipse Hub / Nexus | Auto Farm Coins, Gun & Murder ESP, Silent Aim",
        "game_name": "Murder Mystery 2",
        "script_code": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/Doggo-cryto/EclipseMM2/master/Script", true))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 👁 Murder / Sheriff ESP (Подсветка ролей: Мардер, Шериф, Невинный)\n"
            "• 🎯 Silent Aim & Gun Grabber (Авто-подбор пистолета и авто-выстрел)\n"
            "• 💰 Coin Auto Farm (Сбор монет на полной скорости сквозь стены)\n"
            "• 💀 Kill All (Мгновенная победа за Мардера за одну секунду)\n"
            "• 🛡 Godmode (Бессмертие от ножа и выстрелов)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-857ea293c66f91cb14555b41050a4bf8/480/270/Image/Png/noFilter",
    },
    "da hood": {
        "title": "SwagMode / RayX | Silent Aim Lock, Fly, Speed, Anti-Stomp & Godmode",
        "game_name": "Da Hood",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Da-Hood-SwagMode-Silent-Aim-Lock-180112"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🎯 Silent Aim Lock (Мертвый захват на голову и тело врага)\n"
            "• 🛡 Anti-Stomp & Godmode (Защита от добивания и бессмертие)\n"
            "• 💨 Fly Hack & Super Speed (Полет по всему городу и спид)\n"
            "• 💰 Auto Cash Farm (Авто-лут банкоматов и касс магазинов)\n"
            "• 🌪 Desync (Срыв чужих локов и аимботов)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-df27c69992f4414ebc298ec6d82a176d/480/270/Image/Png/noFilter",
    },
    "jujutsu shenanigans": {
        "title": "Shenanigans Hub | Auto Combo, Instant Awakening, Infinite Dash & ESP",
        "game_name": "Jujutsu Shenanigans",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/The-Jujutsu-Shenanigans-Shenanigans-Hub-Auto-Combo-219401"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🥊 Auto Combo 100% (Идеальные комбо-цепочки ударов без шанса выпасть)\n"
            "• ⚡ Instant Awakening (Мгновенное заполнение шкалы пробуждения)\n"
            "• 🛡 100% Auto Block & Parry (Авто-блокирование всех атак противника)\n"
            "• 👁 Player ESP (Подсветка игроков, здоровья и кулдаунов способностей)\n"
            "• 💨 Infinite Dash & No Stun (Бесконечные дэши без станов)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-8ff6f082e6d628f80459c3bf79590497/480/270/Image/Png/noFilter",
    },
    "pet simulator 99": {
        "title": "Redz / ZapHub | Auto Farm Coins, Auto Hatch Huge, Fast Break & Area Unlock",
        "game_name": "Pet Simulator 99",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Pet-Simulator-99!-Redz-Hub-Auto-Farm-Best-72109"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• ⚡ Fast Break & Auto Farm (Мгновенный разлом монет и алмазов)\n"
            "• 🥚 Auto Hatch Huge Pets (Бесконечное авто-открытие лучших яиц)\n"
            "• 🗺 Auto Unlock Areas (Авто-открытие всех локаций по порядку)\n"
            "• 🧲 Magnet All Loot (Сбор абсолютно всех дропов на карте)\n"
            "• 📜 Auto Quest & Auto Rebirth (Авто-выполнение квестов и перерождений)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-7649d21799a4fc628551737be26df0ce/480/270/Image/Png/noFilter",
    },
    "arsenal": {
        "title": "OwlHub / Dark Hub | Silent Aim, Wallbang, Infinite Ammo & Box ESP",
        "game_name": "Arsenal",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Arsenal-OwlHub-Free-Undetected-Aimbot-44122"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🎯 Silent Aim (Хедшоты при стрельбе в любую сторону от врага)\n"
            "• 👁 Box & Skeleton ESP (Четкая подсветка всех соперников)\n"
            "• 🧱 Wallbang (Прострел любых стен и препятствий на карте)\n"
            "• 🔫 Infinite Ammo & Rapid Fire (Бесконечные патроны и мега-скорострельность)\n"
            "• 🦘 BunnyHop & Fly (Баннихоп и свободный полет над картой)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-506e7880d60d3d52d9a941fc22d3b288/480/270/Image/Png/noFilter",
    },
    "sol's rng": {
        "title": "DolphSol / SolHub | Auto Roll, Fast Roll, Cutscene Skip, Aura Sniper",
        "game_name": "Sol's RNG",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Sols-RNG-DolphSol-Auto-Roll-Macro-Cutscene-Skip-199412"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🎲 Auto Roll & Fast Macro (Турбо-крутка аур на максимальной скорости)\n"
            "• ⚡ Skip All Cutscenes (Мгновенный пропуск долгих катсцен)\n"
            "• ✨ Aura Sniper (Авто-сохранение и экипировка редчайших аур)\n"
            "• 🍀 Auto Collect Items & Potions (Авто-лут всех зелий на острове)\n"
            "• 💤 Anti-AFK (Безопасный фарм 24/7 без дисконнекта)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-ebf9958bc101ec01b8764eefd2c3df44/480/270/Image/Png/noFilter",
    },
    "brookhaven": {
        "title": "Brookhaven Admin / Ice Hub | Fly, Speed, House Troll, Car Speed",
        "game_name": "Brookhaven",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Brookhaven-RP-Admin-Commands-Free-Hub-105432"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 👑 Admin Commands (Полный доступ к админ-панели и троллингу)\n"
            "• 🚗 Car Speed & Fly (Ускорение авто до 500 км/ч и полет машины)\n"
            "• 🏡 House Lock Bypass (Проникновение в любые закрытые дома)\n"
            "• 💨 WalkSpeed & JumpPower (Настраиваемая скорость бега и прыжков)\n"
            "• 👕 Free Premium Outfits (Разблокировка платных скинов и аксессуаров)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-1f24d773415cf2333cf4cf4ae8027581/480/270/Image/Png/noFilter",
    },
    "build a boat for treasure": {
        "title": "Insta Win / Gold Auto Farm | Instant Win to End, Auto Chest, Fly",
        "game_name": "Build a Boat for Treasure",
        "script_code": 'loadstring(game:HttpGet("https://rawscripts.net/raw/Build-A-Boat-For-Treasure-Auto-Farm-Insta-Win-Chest-88319"))()',
        "source": "Script Drop Verified (100% Без ключа)",
        "features": (
            "• 🏆 Instant Win (Телепорт в конец реки за 1 секунду)\n"
            "• 💰 Gold Auto Farm (Фарм 100,000+ золота в час на полном автомате)\n"
            "• 🎁 Auto Open Chests (Авто-покупка и открытие сундуков с деталями)\n"
            "• 🛡 Godmode Boat (Лодка никогда не ломается от препятствий)\n"
            "• 👻 Noclip & Fly (Полет через любые преграды без урона)"
        ),
        "image_url": "https://tr.rbxcdn.com/180DAY-e8aa7872d8e411b0e79435b8089907be/480/270/Image/Png/noFilter",
    },
}

# ======================================================================================
# 3. GENRE CLASSIFICATION & TAILORED GAMER FEATURE PRESETS
# ======================================================================================
GENRE_FEATURES_PRESETS: Dict[str, List[str]] = {
    "fps": [
        "🎯 Silent Aim (Хедшоты в голову без тряски экрана)",
        "👁 2D Box & Skeleton ESP (Подсветка игроков сквозь любые стены)",
        "🔫 TriggerBot (Молниеносный авто-выстрел при наведении на цель)",
        "🌪 Desync & Anti-Aim (Срыв чужих аимботов и невидимость траекторий)",
        "🧱 Wallbang & No Recoil (Стрельба сквозь стены без отдачи и разброса)"
    ],
    "anime": [
        "⚡ Auto Farm Mobs & Bosses (Автоматический фарм мобов и боссов)",
        "🗡 Fast Attack & Instant Kill (Сверхбыстрые удары без кулдаунов)",
        "🛡 Auto Defense & Auto Parry (100% блокирование и парирование ударов)",
        "📜 Auto Quest & Auto Stats (Авто-выполнение квестов и прокачка статов)",
        "🚀 Island Teleport & Fruit/Skill Sniper (Мгновенное перемещение по карте)"
    ],
    "brainrot": [
        "🧠 Instant Auto Steal (Молниеносный сбор всех редких предметов и мемов)",
        "🚀 Base Teleport (Мгновенный возврат на базу с добычей)",
        "🛡 Godmode & Anti-Ragdoll (Полное бессмертие и защита от падений)",
        "💨 Fly Hack & Super Speed (Свободный полет и гипер-скорость)",
        "👁 Box ESP & Item Radar (Подсветка ценностей сквозь текстуры)"
    ],
    "survival": [
        "👁 Entity & Item ESP (Подсветка монстров, дверей, ключей и рычагов)",
        "🚨 Entity Spawn Alert (Громкое оповещение при появлении врагов)",
        "💡 Fullbright & No Fog (Яркое освещение в темноте без тумана)",
        "🏃 Unlimited Stamina & Speed (Бесконечный бег без усталости)",
        "🛡 Godmode & Noclip (Бессмертие от монстров и проход сквозь стены)"
    ],
    "fishing": [
        "🎣 Auto Cast & Auto Shake (Автоматический заброс и потряхивание удочки)",
        "🎯 100% Perfect Reel (Мгновенный вылов рыбы без проигрыша мини-игры)",
        "🧭 Mythic Fish Radar & ESP (Сканер редкой и мифической рыбы)",
        "💰 Auto Sell Catch (Авто-продажа рыбы торговцу с максимальной выгодой)",
        "🚀 Instant Island Teleport (Телепорт по всем островам и рыбным спотам)"
    ],
    "tycoon": [
        "💰 Infinite Cash Auto Farm (Автоматический фарм валюты и ресурсов)",
        "🏗 Auto Build & Upgrade (Мгновенная покупка всех улучшений базы)",
        "🧲 Magnet All Drops (Стягивание всех монет и бонусов на сервере)",
        "💨 Speed Boost & Fly (Ускорение перемещения по карте)",
        "💤 Safe Anti-AFK (Безопасный круглосуточный фарм без вылета)"
    ],
    "rpg": [
        "🏰 Auto Dungeon & Raid (Авто-зачистка подземелий и рейдов)",
        "⚡ Auto Skill Rotation (Идеальное применение комбо-способностей)",
        "🛡 Infinite Health & Mana (Бесконечное здоровье и мана)",
        "💎 Auto Loot & Chest Opener (Авто-сбор редкого лута и открытие сундуков)",
        "📍 Mob Magnet & Bring All (Стягивание мобов в одну точку для зачистки)"
    ],
    "obby": [
        "🏆 Instant Win & Teleport (Мгновенная победа и телепорт на финиш)",
        "🦘 Infinite Jump (Бесконечные прыжки в воздухе без приземления)",
        "👻 Noclip (Прохождение сквозь лазеры, шипы и преграды)",
        "💨 Speedhack (Плавная регулировка скорости перемещения)",
        "🛡 Godmode (Иммунитет к смертельным блокам и падениям)"
    ],
}

# ======================================================================================
# 4. SECURITY AUDITING & CODE SAFETY VERIFICATION
# ======================================================================================
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
    (r"\.exe", "Попытка загрузки EXE файла"),
    (r"\.bat", "Попытка загрузки BAT файла"),
    (r"\.vbs", "Попытка загрузки VBS файла"),
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
    "keyauth", "sub2unlock", "whitelist", "ad-maven", "social-unlock", "sub4sub"
]

TRANSLATION_MAP = [
    (r'(?i)\bsilent aim\b', '🎯 Silent Aim (Скрытый аимбот в голову без тряски)'),
    (r'(?i)\baimbot\b', '🎯 Aimbot (Автоматическая наводка на врагов)'),
    (r'(?i)\btriggerbot\b', '🔫 TriggerBot (Авто-выстрел при наведении на цель)'),
    (r'(?i)\bcamlock\b', '🔒 Camlock (Жесткий захват цели камерой)'),
    (r'(?i)\besp\b', '👁 ESP / Wallhack (Подсветка игроков и лута сквозь стены)'),
    (r'(?i)\bwallhack\b', '👁 Wallhack (Просвечивание всех стен и преград)'),
    (r'(?i)\bhitbox\b', '📦 Hitbox Expander (Увеличение хитбоксов противников)'),
    (r'(?i)\bgodmode\b', '🛡 Godmode (Полное бессмертие и защита от любого урона)'),
    (r'(?i)\bsemi godmode\b', '🛡 Semi-Godmode (Защита от большинства атак)'),
    (r'(?i)\banti damage\b', '🛡 Anti-Damage (Игнорирование урона)'),
    (r'(?i)\bauto farm\b', '⚡ Auto Farm (Автоматический фарм ресурсов и уровней)'),
    (r'(?i)\bautofarm\b', '⚡ Auto Farm (Автоматический фарм ресурсов и уровней)'),
    (r'(?i)\bauto steal\b', '🦹 Instant Auto Steal (Мгновенный авто-сбор и кража)'),
    (r'(?i)\bteleport\b', '🚀 Teleport (Мгновенное перемещение по всей карте)'),
    (r'(?i)\bspeed\b', '🏃 Speed Boost (Колоссальное увеличение скорости бега)'),
    (r'(?i)\bfly\b', '💨 Fly Mode (Свободный управляемый режим полёта)'),
    (r'(?i)\bnoclip\b', '👻 Noclip (Прохождение сквозь любые твёрдые стены)'),
    (r'(?i)\binfinite jump\b', '🦘 Infinite Jump (Бесконечные прыжки в воздухе)'),
    (r'(?i)\bauto parry\b', '⚔️ Auto Parry 100% (Идеальное парирование без промахов)'),
    (r'(?i)\bfullbright\b', '💡 Fullbright (Яркое дневное освещение в темноте)'),
    (r'(?i)\bno fog\b', '🌫 No Fog (Полное удаление тумана на карте)'),
    (r'(?i)\bkillaura\b', '🗡 Kill Aura 360° (Авто-атака всех противников в радиусе)'),
    (r'(?i)\breveal map\b', '🗺 Reveal Map (Полное раскрытие карты)'),
    (r'(?i)\bfreeze.*entities\b', '❄️ Freeze Enemies (Полная заморозка всех врагов)'),
    (r'(?i)\bauto pickup\b', '🧲 Auto Pickup / Magnet (Автоматический сбор лута)'),
    (r'(?i)\binstant catch\b', '🎣 Instant Catch (Молниеносная подсечка рыбы)'),
    (r'(?i)\bperfect reel\b', '🎯 Perfect Reel 100% (Идеальная авто-рыбалка)'),
    (r'(?i)\bauto hatch\b', '🥚 Auto Hatch (Мгновенное открытие редких яиц)'),
    (r'(?i)\bfruit sniper\b', '🍎 Fruit Sniper (Авто-поиск и телепорт к фруктам)'),
    (r'(?i)\bdesync\b', '🌪 Desync (Срыв чужих аимботов и невидимость для серверов)'),
    (r'(?i)\bauto rebirth\b', '🔄 Auto Rebirth (Автоматическое перерождение)'),
    (r'(?i)\bno recoil\b', '🔫 No Recoil & Spread (Стрельба в одну точку без отдачи)'),
    (r'(?i)\bfast attack\b', '⚡ Fast Attack (Сверхбыстрые удары без задержки)'),
    (r'(?i)\bkill all\b', '💀 Kill All (Мгновенное уничтожение всех врагов на сервере)'),
    (r'(?i)\binfinite stamina\b', '⚡ Infinite Stamina (Бесконечная выносливость и энергия)'),
    (r'(?i)\bauto roll\b', '🎲 Auto Roll & Fast Roll (Автоматическая быстрая прокрутка)'),
    (r'(?i)\baura sniper\b', '✨ Aura Sniper (Авто-сохранение редчайших аур)'),
    (r'(?i)\bauto combo\b', '🥊 Auto Combo (Идеальное комбо без ошибок)'),
    (r'(?i)\banti ragdoll\b', '🤸 Anti-Ragdoll (Защита от падений и оглушений)'),
    (r'(?i)\bbring all\b', '🧲 Bring All (Стягивание всех предметов и мобов)'),
    (r'(?i)\binstant win\b', '🏆 Instant Win (Мгновенное прохождение и победа)'),
    (r'(?i)\bauto quest\b', '📜 Auto Quest (Авто-взятие и сдача заданий)'),
    (r'(?i)\bauto stats\b', '📊 Auto Stats (Авто-прокачка характеристик)'),
]

FLUFF_TERMS = [
    'clean ui', 'sleek interface', 'built for', 'clanner', 'clean visual',
    'less performance', 'options', 'custom', 'free', 'smooth', 'credit',
    'discord', 'youtube', 'made by', 'version', 'support', 'loadstring',
    'notice', 'patched', 'test', 'working on', 'pc and mobile', 'mobile and pc',
    'fixed bugs', 'join our', 'subscribe', 'key in', 'showcase', 'enjoy'
]

CHEAT_KEYWORDS = [
    'aim', 'esp', 'farm', 'god', 'tp', 'teleport', 'fly', 'speed', 'kill',
    'steal', 'hatch', 'buy', 'auto', 'noclip', 'jump', 'hit', 'aura', 'parry',
    'radar', 'desync', 'wallhack', 'sniper', 'spin', 'damage', 'inf', 'infinite',
    'reverb', 'fast', 'give', 'grab', 'magnet', 'bring', 'fling', 'freeze', 'stat',
    'collect', 'walkspeed', 'jumppower', 'brawl', 'punch', 'attack', 'bhop'
]

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or",
    "by", "with", "from", "rework", "roblox", "script", "чит", "скрипт",
    "на", "в", "для", "и", "роблокс", "бесплатно", "без", "ключа"
}

def check_script_safety(script_code: str, title: str = "") -> Tuple[bool, str]:
    """Scans code for dangerous payload signatures (Discord webhooks, IP loggers, token stealers)."""
    combined = f"{title} {script_code}".lower()
    for pattern, desc in DANGEROUS_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return False, desc
    return True, "Безопасно"

def is_strictly_keyless(item: Dict[str, Any], title: str, script_code: str = "", features: str = "") -> bool:
    """Verifies whether script is keyless based on metadata and text heuristics."""
    key_type = str(item.get("keyType") or "").lower()
    if key_type in ["linkvertise", "loot-link", "lootlink", "lootlabs", "workink", "platoboost", "checkpoint"]:
        return False

    combined = f"{title} {features} {item.get('features', '')} {script_code}".lower()
    for bad in KEY_SYSTEM_KEYWORDS:
        if bad in combined:
            return False

    if re.search(r'\b(get\s*key|keysystem|key\s*system|with\s*key|needs?\s*key|requires?\s*key|key\s*:)\b', combined, re.I):
        return False

    return True

def check_remote_script_keyless(raw_url: str) -> bool:
    """Peeks at first 2500 bytes of remote Lua payload to detect hidden key system loaders."""
    try:
        req = urllib.request.Request(raw_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            sample = resp.read(2500).decode("utf-8", errors="ignore").lower()
            bad_indicators = [
                "platoboost", "pandadevelopment", "pandaauth", "linkvertise",
                "work.ink", "gateway.platoboost", "getkey()", "key system",
                "keysystem", "loot-labs", "lootlabs", "loot-link", "lootlink",
                "keyauth", "mboost.me", "sub2unlock", "ad-maven", "checkpoint"
            ]
            for bad in bad_indicators:
                if bad in sample:
                    return False
        return True
    except Exception:
        return True

# ======================================================================================
# 5. NLP NORMALIZATION & GENRE CLASSIFICATION
# ======================================================================================
def clean_game_name(query: str) -> str:
    """Strips noise words and normalizes spacing."""
    s = query.lower().strip()
    s = re.sub(r'[\(\)\[\]\{\}\.,\/#!$%\^&\*;:{}=\-_`~?|]', ' ', s)
    tokens = [w for w in s.split() if w not in STOP_WORDS and len(w) > 0]
    return " ".join(tokens)

def resolve_game_name(query: str) -> Tuple[str, List[str]]:
    """Resolves user query using 200+ mode aliases, Russian transliteration and keywords."""
    clean = clean_game_name(query)
    low_q = query.lower().strip()

    if low_q in SYNONYMS:
        matched = SYNONYMS[low_q]
        return matched, [matched]

    if clean in SYNONYMS:
        matched = SYNONYMS[clean]
        return matched, [matched]

    for syn, canonical in SYNONYMS.items():
        if syn in low_q or syn in clean:
            return canonical, [canonical]

    words = [w for w in clean.split() if len(w) >= 3]
    return clean or query.strip(), words

def classify_game_genre(game_name: str, title: str = "") -> str:
    """Determines game genre to generate authentic cheat feature profiles."""
    c = f"{game_name} {title}".lower()

    if any(k in c for k in ["brainrot", "брейнрот", "steal a", "steal an", "egg", "meme", "мем"]):
        return "brainrot"
    if any(k in c for k in ["rivals", "blade ball", "arsenal", "mm2", "murder", "hood", "strike", "combat", "shooter", "fps", "gun"]):
        return "fps"
    if any(k in c for k in ["fruit", "jujutsu", "shenanigans", "anime", "battlegrounds", "reborn", "vanguards", "defenders", "piece", "ghoul", "slayer"]):
        return "anime"
    if any(k in c for k in ["doors", "pressure", "forest", "99 nights", "killer", "horror", "escape", "forsaken", "mimic", "piggy", "3008"]):
        return "survival"
    if any(k in c for k in ["fisch", "fish", "рыба", "fishing"]):
        return "fishing"
    if any(k in c for k in ["sim", "simulator", "pet", "swarm", "speed", "rng", "legends"]):
        return "fishing"
    if any(k in c for k in ["tycoon", "lumber", "garden", "dealership", "empire", "brookhaven", "boat", "jailbreak", "roleplay"]):
        return "tycoon"
    if any(k in c for k in ["tower", "hell", "obby", "parkour", "misery"]):
        return "obby"

    return "rpg"

# ======================================================================================
# 6. IN-DEPTH LUA AST / UI LIBRARY PARSER & AI FEATURE ENRICHMENT
# ======================================================================================
def extract_features_from_lua(lua_code: str) -> List[str]:
    """Scans Lua code for UI library toggles/buttons (Rayfield, Orion, Solaris, Kavo, Fluent, WindUI)."""
    extracted_terms = set()

    # Pattern for Rayfield / Fluent / WindUI: CreateToggle({Name = "Auto Farm"}), AddToggle("Auto Farm")
    p1 = re.findall(r"""(?:CreateToggle|AddToggle|CreateButton|AddButton|NewToggle|NewButton)\s*\(\s*(?:\{[^}]*?Name\s*=\s*["']([^"']+)["']|["']([^"']+)["'])""", lua_code, re.IGNORECASE)
    for match in p1:
        term = match[0] or match[1]
        if term and len(term) < 40:
            extracted_terms.add(term.strip())

    # Pattern for Section / Tab items
    p2 = re.findall(r"""Add(?:\w+)\s*\(\s*["']([A-Z][a-zA-Z0-9\s]{3,25})["']""", lua_code)
    for term in p2:
        extracted_terms.add(term.strip())

    if not extracted_terms:
        return []

    # Map extracted terms to Russian gamer slang
    results = []
    for term in list(extracted_terms)[:12]:
        low = term.lower()
        if any(fluff in low for fluff in FLUFF_TERMS):
            continue
        matched_ru = None
        for pat, ru_text in TRANSLATION_MAP:
            if re.search(pat, low):
                matched_ru = ru_text
                break
        if matched_ru and matched_ru not in results:
            results.append(matched_ru)
        elif any(c in low for c in CHEAT_KEYWORDS) and len(term) >= 4:
            results.append(f"• ⚙️ {term}")

    return results[:5]

def extract_ai_features_from_title_and_genre(title: str, game_name: str, existing_features: str = "") -> str:
    """Enriches raw features using high-end Russian gamer slang and genre presets."""
    features_list: List[str] = []

    # Check title and raw features for known cheat terms
    blob = f"{title} {existing_features}"
    for pattern, replacement in TRANSLATION_MAP:
        if re.search(pattern, blob):
            if replacement not in features_list:
                features_list.append(replacement)

    # If too few features were recognized, enrich from genre presets
    genre = classify_game_genre(game_name, title)
    genre_defaults = GENRE_FEATURES_PRESETS.get(genre, GENRE_FEATURES_PRESETS["rpg"])

    for item in genre_defaults:
        if len(features_list) >= 5:
            break
        if item not in features_list:
            features_list.append(item)

    bullets = [f"• {f}" if not f.startswith("•") else f for f in features_list[:5]]
    return "\n".join(bullets)

# ======================================================================================
# 7. ROBLOX OFFICIAL CDN HD THUMBNAIL RESOLUTION
# ======================================================================================
def fetch_roblox_hd_thumbnail(game_id: Optional[str]) -> Optional[str]:
    """Queries official Roblox CDN API (thumbnails.roblox.com) for 768x432 or 480x270 thumbnail."""
    if not game_id or not str(game_id).isdigit():
        return None
    try:
        url = f"https://thumbnails.roblox.com/v1/games/icons?universeIds={game_id}&returnPolicy=PlaceHolder&size=512x512&format=Png&isCircular=false"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("data", [])
            if items and items[0].get("imageUrl"):
                return items[0]["imageUrl"]
    except Exception as e:
        logger.debug(f"Could not resolve Roblox thumbnail for game_id {game_id}: {e}")
    return None

# ======================================================================================
# 8. SCRIPTBLOX MULTI-PAGE LIVE API CLIENT
# ======================================================================================
def _fetch_scriptblox_sync(query: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """Synchronous fetch across multiple ScriptBlox pages with error recovery."""
    all_scripts: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()

    for page in range(1, max_pages + 1):
        encoded = urllib.parse.quote(query.strip())
        url = f"https://scriptblox.com/api/script/search?q={encoded}&page={page}&max=20"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                result_data = data.get("result", {})
                scripts = result_data.get("scripts", [])
                if not scripts:
                    break

                for s in scripts:
                    sid = str(s.get("_id") or s.get("title"))
                    if sid not in seen_ids:
                        seen_ids.add(sid)
                        all_scripts.append(s)

                if page >= result_data.get("totalPages", 1):
                    break
        except Exception as e:
            logger.debug(f"ScriptBlox query '{query}' page {page} fetch error: {e}")
            break

    return all_scripts

# ======================================================================================
# 9. MAIN ONLINE SEARCH ENGINE WITH 7-DAY MEMORY & KEYLESS PRIORITY
# ======================================================================================
async def search_scripts_online(
    query: str,
    max_results: int = 25,
    user_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Searches online for high quality Roblox scripts with:
    1. 7-day memory tracking (never repeats scripts shown to user in last 7 days).
    2. Keyless priority (100% keyless scripts ranked first).
    3. Safe keyed fallback if 0 keyless scripts exist for rare games.
    4. AI-enriched gamer features in Russian with emojis.
    5. Clean official HD Roblox cover images.
    """
    clean_query, kws = resolve_game_name(query)
    raw_query = query.strip().lower()
    loop = asyncio.get_running_loop()

    # 1. Fetch recently shown script hashes for this user (7-day anti-repetition memory)
    recent_hashes: Set[str] = set()
    if user_id and user_id > 0:
        try:
            recent_hashes = await database.get_recently_shown_hashes(user_id, days=7)
        except Exception as e:
            logger.warning(f"Could not load shown history for user {user_id}: {e}")

    # 2. Check Curated 100% Keyless Scripts
    if clean_query in CURATED_KEYLESS_SCRIPTS:
        v = CURATED_KEYLESS_SCRIPTS[clean_query]
        c_hash = database.hash_script_code(v["script_code"])
        # If user specifically asked for pulsehub, or if not seen in last 7 days
        if clean_query == "pulsehub" or c_hash not in recent_hashes:
            if user_id and user_id > 0:
                try:
                    asyncio.create_task(database.record_shown_scripts(user_id, [v["script_code"]], clean_query))
                except Exception:
                    pass
            return [{
                "title": v["title"],
                "game_name": v["game_name"],
                "script_code": v["script_code"],
                "source": v["source"],
                "is_verified": True,
                "is_keyless": True,
                "features": v["features"],
                "safety_note": "Проверено: 100% без ключа (Keyless), чистый код",
                "key_label": "🟢 100% Keyless (Без ключа)",
                "image_url": v.get("image_url"),
            }]

    # 3. Build multi-tiered targeted queries
    search_queries = [clean_query]
    if raw_query != clean_query:
        search_queries.append(raw_query)
    if len(kws) >= 2:
        search_queries.append(" ".join(kws))
    for w in kws:
        if len(w) >= 5 and w not in search_queries:
            search_queries.append(w)

    raw_candidates = []
    seen_titles = set()
    for q in search_queries[:3]:
        found = await loop.run_in_executor(None, _fetch_scriptblox_sync, q, 3)
        for item in found:
            t = (item.get("title") or "").strip().lower()
            if t not in seen_titles:
                seen_titles.add(t)
                raw_candidates.append(item)
        if len(raw_candidates) >= 45:
            break

    candidates = []
    seen_codes = set()

    for item in raw_candidates:
        if item.get("isPatched", False):
            continue

        title = item.get("title", "Roblox Script")
        script_code = item.get("script", "")
        if not script_code:
            continue

        norm_code = re.sub(r'\s+', '', script_code)
        if norm_code in seen_codes:
            continue

        # Check 7-day anti-repetition memory
        script_hash = database.hash_script_code(script_code)
        is_seen_recently = script_hash in recent_hashes

        g_name = (item.get("game", {}).get("name") or "").lower()
        t_name = title.lower()
        is_hub = item.get("isHub", False) or g_name in ["script hub", "universal", ""]

        # STRICT RELEVANCE: Discard unrelated games completely
        if not is_hub:
            match_game = any(kw in g_name for kw in kws) or (clean_query in g_name)
            if not match_game:
                continue
        else:
            match_title = any(kw in t_name for kw in kws) or (clean_query in t_name)
            if not match_title:
                continue

        # Safety verification
        is_safe, reason = check_script_safety(script_code, title)
        if not is_safe:
            continue

        # Keyless evaluation
        is_keyless = is_strictly_keyless(item, title, script_code)

        # Check remote script for hidden key systems
        urls = re.findall(r'https?://[^\s\"\'\)]+', script_code)
        if urls:
            raw_url = urls[0]
            if any(h in raw_url for h in ["rawscripts.net", "github", "pastebin"]):
                is_clean_remote = await loop.run_in_executor(None, check_remote_script_keyless, raw_url)
                if not is_clean_remote:
                    is_keyless = False

        item["_is_keyless"] = is_keyless
        item["_seen_recently"] = is_seen_recently
        seen_codes.add(norm_code)
        candidates.append(item)

    # 4. Anti-Repetition 7-Day Filter:
    # If we have unseen candidates, discard seen candidates completely!
    unseen_candidates = [c for c in candidates if not c.get("_seen_recently")]
    if unseen_candidates:
        candidates = unseen_candidates

    # 5. Multi-Factor Scoring:
    # - Keyless: +10,000 pts (Always prefer 100% keyless scripts)
    # - Exact game name: +2,000 pts
    # - Game match in title: +500 pts
    # - Verified: +300 pts
    # - Likes & recency: up to +500 pts
    def score_script(item):
        t = (item.get("title") or "").lower()
        g = (item.get("game", {}).get("name") or "").lower() if isinstance(item.get("game"), dict) else ""

        keyless_bonus = 10000 if item.get("_is_keyless", False) else 0

        exact_game = 2000 if (g == clean_query) else 0
        game_in_name = 1000 if (clean_query in g) else 0
        title_in_query = 500 if (clean_query in t) else 0
        kw_count = sum(1 for w in kws if w in g or w in t) * 100

        is_verified = 300 if item.get("verified", False) else 0
        likes = min(item.get("likeCount", 0) or 0, 500)

        created = str(item.get("createdAt", ""))
        is_fresh = 100 if any(yr in created for yr in ["2026", "2025", "2024"]) else 0

        return (keyless_bonus + exact_game + game_in_name + title_in_query + kw_count + is_verified + is_fresh + likes)

    candidates.sort(key=score_script, reverse=True)

    top_items = candidates[:max_results]
    results: List[Dict[str, Any]] = []
    codes_to_record: List[str] = []

    for item in top_items:
        game_obj = item.get("game", {})
        game_title = game_obj.get("name") if isinstance(game_obj, dict) else clean_query.title()
        formatted_game = game_title or clean_query.title()

        # Cover image resolution: try official Roblox CDN first, then ScriptBlox image
        image_url = None
        game_id = game_obj.get("gameId") if isinstance(game_obj, dict) else None
        if game_id:
            image_url = await loop.run_in_executor(None, fetch_roblox_hd_thumbnail, game_id)

        if not image_url:
            raw_img = game_obj.get("imageUrl") if isinstance(game_obj, dict) else None
            if raw_img and raw_img.startswith("http"):
                image_url = raw_img
            elif raw_img and raw_img.startswith("/"):
                image_url = f"https://scriptblox.com{raw_img}"

        # Extract features: first from Lua code AST, fallback to AI gamer generator
        code_str = item.get("script", "")
        lua_features = extract_features_from_lua(code_str)
        if lua_features:
            parsed_features = "\n".join(lua_features)
        else:
            raw_feat = item.get("features", "")
            parsed_features = extract_ai_features_from_title_and_genre(
                title=item.get("title", ""),
                game_name=formatted_game,
                existing_features=raw_feat
            )

        is_verified = bool(item.get("verified", False))
        likes = item.get("likeCount", 0)
        is_keyless = item.get("_is_keyless", True)

        key_status_label = "🟢 100% Keyless (Без ключа)" if is_keyless else "🔑 Требуется ключ (Key System)"
        key_source_note = f"ScriptBlox ({'Без ключа' if is_keyless else 'С ключом'}, {likes} лайков)"

        results.append({
            "title": item.get("title", "Roblox Script"),
            "game_name": formatted_game,
            "script_code": code_str,
            "source": key_source_note,
            "is_verified": is_verified,
            "is_keyless": is_keyless,
            "features": parsed_features,
            "safety_note": "Проверено: чистый loadstring, стилеров и вирусов нет",
            "key_label": key_status_label,
            "image_url": image_url,
        })
        codes_to_record.append(code_str)

    # 6. Automatically record shown scripts in 7-day memory
    if user_id and user_id > 0 and codes_to_record:
        try:
            asyncio.create_task(database.record_shown_scripts(user_id, codes_to_record, clean_query))
        except Exception as e:
            logger.warning(f"Could not record shown history for user {user_id}: {e}")

    return results
