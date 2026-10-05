"""
PROMO SCENARIO GENERATOR FOR TIKTOK & YOUTUBE SHORTS (ROBLOX SCRIPT CHANNELS)
Generates high-retention viral 12-second video scripts, voiceover texts, and CapCut editing guides.
Usage:
    python promo_generator.py "Steal an Egg"
"""

import sys
import re
from typing import Dict, Any, List

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import post_builder

HOOK_TEMPLATES = [
    "Админы {game} в шоке! Я нашёл приватный скрипт без ключа, который разносит весь сервер!",
    "Ты до сих пор фармишь в {game} руками? Держи лучший рабочий чит без ключей и вирусов!",
    "Этот скрипт на {game} удаляют со всех сайтов! Забирай, пока разработчики не пофиксили!",
    "Нашёл самый имбовый хаб на {game}, о котором никто не знает! 100% без ключей!",
]

def generate_promo(game_name: str, bot_username: str = "AsceRobloxScript_bot", channel_tag: str = "@script_drop") -> Dict[str, Any]:
    """Generates complete viral video package for TikTok/Shorts based on game name."""
    clean_game = post_builder.format_game_name(game_name)
    features_text = post_builder.generate_ai_features(clean_game)

    # Extract 3 punchy features
    feat_lines = [re.sub(r'^[•\-\s]+', '', f).strip() for f in features_text.split('\n') if f.strip()]
    top_feats = []
    for f in feat_lines[:3]:
        # simplify for voice
        m = re.match(r'^(.*?)\s*\((.*?)\)', f)
        if m:
            ru_desc = m.group(2)
            top_feats.append(ru_desc)
        else:
            top_feats.append(f)

    feats_voice = ", ".join(top_feats) if top_feats else "моментальный авто-фарм, телепорт и спидхак"
    first_feat_upper = top_feats[0].upper() if top_feats else "АВТО-ФАРМ"

    # Precise Voiceover segments by timing cycles
    cycle1_voice = f"Ты до сих пор фармишь в {clean_game} руками?"
    cycle2_voice = f"Я нашёл лучший приватный чит без ключа! Здесь есть {feats_voice}."
    cycle3_voice = f"Работает на телефонах и ПК без вылетов и бана."
    cycle4_voice = f"Скрипт уже выложил в свой телеграм {channel_tag}. Ссылка в шапке профиля, забирай!"

    # Full unified text for CapCut Text-to-Speech in 1 click
    voiceover_text = f"{cycle1_voice} {cycle2_voice} {cycle3_voice} {cycle4_voice}"

    # On-screen header with Glow effect
    onscreen_text = f"СКРИПТ БЕЗ КЛЮЧА НА {clean_game.upper()}! 🤫"

    # Tags
    slug = re.sub(r'[^a-zA-Z0-9]', '', clean_game.lower())
    tags = f"#roblox #{slug} #robloxscripts #deltaexecutor #robloxscript #keyless #scriptdrop"

    cycles = [
        {
            "cycle": 1,
            "timing": "00:00 – 00:03 (3 сек)",
            "stage": "Хук (Захват зрителя)",
            "gameplay": f"Бежишь или прыгаешь в {clean_game}. Быстрый поворот камеры.",
            "glow_text": onscreen_text,
            "voice": cycle1_voice,
        },
        {
            "cycle": 2,
            "timing": "00:03 – 00:07 (4 сек)",
            "stage": "Демонстрация чита (Вау-эффект)",
            "gameplay": f"Открываешь меню чита, кликаешь кнопку ({feats_voice}), фарм/сбор идёт на бешеной скорости.",
            "glow_text": f"🔥 {first_feat_upper} БЕЗ КЛЮЧА",
            "voice": cycle2_voice,
        },
        {
            "cycle": 3,
            "timing": "00:07 – 00:10 (3 сек)",
            "stage": "Надёжность и оптимизация",
            "gameplay": "Показываешь плавный геймплей без лагов и без крашей.",
            "glow_text": "⚡ 100% БЕЗ БАНА И ВЫЛЕТОВ",
            "voice": cycle3_voice,
        },
        {
            "cycle": 4,
            "timing": "00:10 – 00:13 (3 сек)",
            "stage": "Призыв к действию (Байт в ТГ)",
            "gameplay": f"Скриншот твоего ТГ-канала {channel_tag} со стрелкой на профиль TikTok/Shorts.",
            "glow_text": "⬇️ ССЫЛКА В ШАПКЕ ПРОФИЛЯ",
            "voice": cycle4_voice,
        },
    ]

    return {
        "game_name": clean_game,
        "onscreen_text": onscreen_text,
        "voiceover_text": voiceover_text,
        "duration": "12-13 секунд",
        "cycles": cycles,
        "capcut_settings": {
            "voice": "Русский → «Энергичный парень» (или «Диктор»)",
            "captions": "Автосубтитры → Шаблон «Glow / Свечение»",
            "music": "Тихий фонк на фоне (громкость -18 dB)",
        },
        "tags": tags
    }

def print_promo_card(promo: Dict[str, Any]):
    print("=" * 60)
    print(f"🎬 ГОТОВЫЙ СЦЕНАРИЙ SHORTS / TIKTOK: {promo['game_name'].upper()}")
    print("=" * 60)
    print(f"⏱ Хронометраж: {promo['duration']}")
    print(f"🔤 Главный Glow-текст: {promo['onscreen_text']}\n")
    print("🎙 ПОЛНЫЙ ТЕКСТ ДЛЯ ОЗВУЧКИ В CAPCUT (скопируй в «Текст в речь»):")
    print(f"«{promo['voiceover_text']}»\n")
    print("🎬 ПОСЕКУНДНЫЕ ТАЙМЦИКЛЫ МОНТАЖА:")
    for c in promo["cycles"]:
        print(f"\n📍 {c['timing']} | {c['stage']}")
        print(f"   🎮 Что снимать в игре: {c['gameplay']}")
        print(f"   🔤 Glow-надпись: {c['glow_text']}")
        print(f"   🗣 Голос озвучки: «{c['voice']}»")
    print("\n⚙️ НАСТРОЙКИ CAPCUT:")
    for k, v in promo["capcut_settings"].items():
        print(f"  • {k}: {v}")
    print(f"\n🏷 Хештеги: {promo['tags']}")
    print("=" * 60)

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Steal an Egg"
    res = generate_promo(query)
    print_promo_card(res)
