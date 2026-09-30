import re
import html
from typing import Optional, Tuple, List

def format_game_name(raw_name: str) -> str:
    """Formats game name with Title Case, cleans bracketed tags and emojis, handles known acronyms."""
    # Remove bracketed update tags like [✨BONUS], [UPDATE 20], [EVENT], [NEW!], etc.
    cleaned = re.sub(r'\[.*?\]', '', raw_name)
    cleaned = re.sub(r'\(.*?update.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(.*?event.*?\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[^\w\s\-\.\']', '', cleaned)
    cleaned = cleaned.strip()
    if not cleaned:
        cleaned = raw_name.strip()

    words = cleaned.split()
    formatted_words = []
    
    known_acronyms = {
        "esp": "ESP",
        "fps": "FPS",
        "psx": "PSX",
        "ps99": "Pet Simulator 99",
        "tps": "TPS",
        "r6": "R6",
        "r15": "R15",
        "pvp": "PvP",
        "pve": "PvE",
        "npc": "NPC",
        "gui": "GUI",
        "hub": "Hub",
        "mm2": "Murder Mystery 2",
        "ttd": "Toilet Tower Defense",
        "bf": "Blox Fruits",
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

# --- AI GAME KNOWLEDGE BASE & DESCRIPTION GENERATOR ---
KNOWN_GAMES_FEATURES = {
    "blox fruits": (
        "• Auto Farm Level & Quests (Авто-фарм уровня и заданий)\n"
        "• Auto Raid & Boss Farm (Авто-рейды и фарм боссов)\n"
        "• Fruit Sniper & Fruit ESP (Поиск и авто-подбор фруктов)\n"
        "• Mastery Farm (Прокачка мечей, пушек и стилей боя)\n"
        "• Fast Attack & Godmode (Мгновенная атака без задержки)"
    ),
    "blade ball": (
        "• Auto Parry 100% (Идеальное авто-парирование без промахов)\n"
        "• Manual Target Lock (Фокус и авто-наведение на цель)\n"
        "• Ball ESP & Velocity Tracker (Траектория и скорость мяча)\n"
        "• Auto Clash Spam (Мгновенная победа в клэш-дуэлях)\n"
        "• Infinite Curve Deflect (Крученый отбив мяча)"
    ),
    "steal an egg": (
        "• Instant Auto Steal (Мгновенная кража яиц у всех игроков)\n"
        "• Egg Teleport & Base ESP (Подсветка баз и редких яиц)\n"
        "• Auto Fuse & Auto Open (Автоматическое объединение яиц)\n"
        "• Speed Boost & Fly (Увеличенная скорость и режим полёта)\n"
        "• Godmode / Safe Zone (Полная защита от других игроков)"
    ),
    "murder mystery 2": (
        "• Murderer & Sheriff ESP (Подсветка ролей, дистанции и оружия)\n"
        "• Silent Aim & Auto Shoot (Скрытый аимбот по маньяку)\n"
        "• Auto Collect Coins (Молниеносный сбор монет по всей карте)\n"
        "• Teleport to Gun (Мгновенный подбор выпавшего пистолета)\n"
        "• Speed, Fly & Infinite Jump (Скорость и свободный полёт)"
    ),
    "rivals": (
        "• Silent Aim (Скрытый аимбот в голову без дерганья камеры)\n"
        "• 2D Box & Skeleton ESP (ВХ сквозь стены с отображением HP)\n"
        "• No Recoil & No Spread (Стрельба без отдачи в одну точку)\n"
        "• Auto Shoot / TriggerBot (Авто-выстрел при наведении на врага)\n"
        "• Infinite Stamina & BunnyHop (Бесконечный бег и распрыжка)"
    ),
    "fisch": (
        "• Auto Fish / Instant Catch (Мгновенная авто-ловля рыбы)\n"
        "• Perfect Reel 100% (Идеальная авто-подсечка без срывов)\n"
        "• Fish ESP & Rarity Filter (Подсветка легендарной и мифической рыбы)\n"
        "• Teleport to Islands & Sellers (Быстрое перемещение к торговцам)\n"
        "• Infinite Oxygen & Fly (Бесконечный кислород под водой)"
    ),
    "doors": (
        "• Key, Lever & Item ESP (Подсветка всех ключей, рычагов и лута)\n"
        "• Entity Warning (Звуковое и визуальное оповещение о монстрах)\n"
        "• Auto Unlock / Instant Open (Мгновенное открытие дверей)\n"
        "• Fullbright & Speed (Яркое освещение в темноте и скорость)\n"
        "• Godmode against Screech & Rush (Защита от монстров)"
    ),
    "bedwars": (
        "• Killaura / Attack Aura (Авто-атака всех противников в радиусе)\n"
        "• Bed ESP & Chest Stealer (Подсветка кроватей и авто-лут сундуков)\n"
        "• Scaffold / Fly (Автоматическое строительство блоков под собой)\n"
        "• Velocity / Anti-Knockback (Полное отсутствие отдачи при ударах)\n"
        "• Infinite Jump & Sprint (Бесконечные прыжки и спринт)"
    ),
    "da hood": (
        "• Silent Aim & Camlock (Точнейший аимбот с упреждением)\n"
        "• Target & Armor ESP (ВХ на игроков, броню и деньги)\n"
        "• Auto Stomp & Auto Reload (Авто-добив и быстрая перезарядка)\n"
        "• Anti-Lock / Resolver (Защита от чужих аимботов)\n"
        "• Fly & Teleport to Bank/ATM (Мгновенный телепорт к сейфам)"
    ),
    "pet simulator 99": (
        "• Auto Farm Coins & Diamonds (Авто-фарм монет и гемов)\n"
        "• Auto Hatch Best Eggs (Авто-открытие лучших яиц)\n"
        "• Auto Quest & Ranks (Автоматическое выполнение квестов)\n"
        "• Pet Sniper / Trading ESP (Поиск выгодных питомцев)\n"
        "• Speed Boost & Auto Collect (Мгновенный сбор лута)"
    ),
    "brookhaven": (
        "• Unlock All Passes & Houses (Разблокировка платных домов)\n"
        "• Speed, Fly & Vehicle Tuning (Тюнинг машин, полёт и скорость)\n"
        "• Player Teleport & Troll GUI (Телепортация к игрокам)\n"
        "• Avatar Animations & Emotes (Все анимации и эмодзи)"
    ),
    "jujutsu shenanigans": (
        "• Auto Combo & Skill Spam (Авто-комбо способностей без задержки)\n"
        "• Auto Block & Counter (Идеальное блокирование ударов)\n"
        "• Teleport Behind Target (Мгновенный телепорт за спину врага)\n"
        "• Infinite Awakening / Ult (Бесконечный режим пробуждения)\n"
        "• ESP Players & HP Bar (Подсветка здоровья и энергии игроков)"
    ),
    "forsaken": (
        "• Auto Generator (Автоматический ремонт генераторов)\n"
        "• Invincible / Godmode (Полная неуязвимость к атакам)\n"
        "• Infinite Stamina (Бесконечная выносливость и спринт)\n"
        "• ESP Killer & Survivor (ВХ на маньяка и выживших)\n"
        "• Instant Heal & Speed (Мгновенное лечение и скорость)"
    ),
}

def generate_ai_features(game_name: str) -> str:
    """AI generator that produces accurate, high-quality features for any Roblox game."""
    clean = game_name.strip().lower()
    
    # Check direct match
    for k, v in KNOWN_GAMES_FEATURES.items():
        if k in clean or clean in k:
            return v

    # Keyword based heuristic generator
    if any(w in clean for w in ["tycoon", "тайкун"]):
        return (
            "• Auto Collect Cash (Автоматический сбор денег с дропперов)\n"
            "• Auto Buy / Instant Build (Авто-покупка всех улучшений)\n"
            "• Speed & Fly (Увеличенная скорость передвижения и полёт)\n"
            "• Infinite Money Glitch (Максимальная скорость накопления)\n"
            "• Base ESP & Shield (Подсветка врагов и защита базы)"
        )
    elif any(w in clean for w in ["sim", "simulator", "симулятор"]):
        return (
            "• Auto Click / Auto Farm (Автоматический кликер и фарм ресурсов)\n"
            "• Auto Rebirth (Авто-перерождение при достижении цели)\n"
            "• Auto Hatch Eggs (Автоматическое открытие лучших яиц)\n"
            "• Speed Boost & Teleport (Мгновенное перемещение по локациям)\n"
            "• VIP / Gamepass Bypass (Разблокировка бонусов игры)"
        )
    elif any(w in clean for w in ["shooter", "gun", "fps", "strike", "war", "стрелялк"]):
        return (
            "• Silent Aim (Скрытый аимбот прямо в голову врага)\n"
            "• Wallhack & Box ESP (Подсветка игроков через любые стены)\n"
            "• No Recoil & No Spread (Идеально точная стрельба без отдачи)\n"
            "• Infinite Ammo & Rapid Fire (Бесконечные патроны и скорострельность)\n"
            "• Speed & BunnyHop (Увеличенная скорость и прыжки)"
        )
    elif any(w in clean for w in ["horror", "terror", "escape", "хоррор", "побег"]):
        return (
            "• Monster & Enemy ESP (Подсветка монстров и опасных зон)\n"
            "• Item & Key ESP (Отображение всех ключей и нужных предметов)\n"
            "• Fullbright Mode (Идеальная видимость в полной темноте)\n"
            "• Speed Boost & No Clip (Прохождение сквозь препятствия)\n"
            "• Godmode (Полная неуязвимость к атакам)"
        )
    elif any(w in clean for w in ["battle", "fight", "punch", "бой", "битва"]):
        return (
            "• Auto Attack & Combo (Мгновенные серии ударов по противникам)\n"
            "• Auto Parry / Auto Dodge (Автоматическое уклонение и блок)\n"
            "• Teleport Behind Target (Телепортация за спину цели)\n"
            "• Godmode & Infinite Stamina (Бессмертие и бесконечная выносливость)\n"
            "• Player ESP & Distance (Подсветка игроков и дистанции)"
        )
        
    return DEFAULT_FEATURES

def format_features(raw_features: str) -> str:
    """Formats features list into a neat bulleted list with emojis."""
    if not raw_features or raw_features.strip().lower() in ["по дефолту", "дефолт", "default", "-", "1", "ии", "ai"]:
        return DEFAULT_FEATURES
    
    items = re.split(r'[,;\n]+', raw_features)
    formatted = []
    
    replacements = {
        "есп": "ESP (ВХ / Подсветка игроков и предметов)",
        "esp": "ESP (ВХ / Подсветка игроков и предметов)",
        "аим": "Aimbot (Точный скрытый аимбот)",
        "aim": "Aimbot (Точный скрытый аимбот)",
        "автофарм": "Auto Farm (Автоматический фарм)",
        "авто фарм": "Auto Farm (Автоматический фарм)",
        "autofarm": "Auto Farm (Автоматический фарм)",
        "спид": "Speed (Увеличение скорости ходьбы)",
        "флай": "Fly (Свободный режим полёта)",
        "тп": "Teleport (Мгновенная телепортация)",
        "годмод": "God Mode (Полная неуязвимость / Бессмертие)",
        "инфинит": "Infinite Jump (Бесконечный прыжок)",
        "норекоил": "No Recoil (Стрельба без отдачи)",
        "пари": "Auto Parry (Автоматическое парирование)",
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
        f"🛡 <b>Проверка на вирусы:</b> 🟢 <i>Чистый код (без RAT / стилеров)</i>\n"
        f"📌 <b>Статус:</b> 🟢 <i>Работает / Undetected</i>\n"
        f"📱 <b>Поддержка:</b> {executors}\n\n"
        f"👇 <b>Нажмите на кнопку ниже, чтобы получить скрипт:</b>"
    )
    return post

def build_user_delivery_message(game_name: str, script_code: Optional[str] = None) -> str:
    """Generates the response message when user requests a script (matches Screenshot 2)."""
    if script_code is None:
        actual_code = game_name
        title = "Roblox"
    else:
        title = format_game_name(game_name)
        actual_code = script_code
        
    escaped_code = html.escape(actual_code)
    return (
        f"👋 <b>Привет! Вот держи готовый скрипт для {title}:</b>\n\n"
        f'<pre><code class="language-lua">{escaped_code}</code></pre>\n\n'
        f"💡 <i>Нажмите на код выше, чтобы скопировать его в буфер обмена.</i>\n\n"
        f"🛡 <b>Безопасность:</b> 🟢 <i>Проверено: чистый loadstring, вирусов и стилеров нет</i>\n\n"
        f"🚀 <b>Удачи в игре!</b>"
    )

def build_changelog_cyber(bot_username: str) -> str:
    """Style 1: Cyber / Neon 1.1 (Sharp, stylish, from the admin)."""
    return (
        "⚡ <b>ОБНОВЛЕНИЕ 1.1 | SCRIPT DROP</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>На связи админ канала. Выкатываю первое обновление 1.1!</i>\n\n"
        "🔥 <b>ЧТО ИЗМЕНИЛОСЬ В ВЕРСИИ 1.1:</b>\n\n"
        "🛡 <b>1. Проверка на вирусы и стилеры</b>\n"
        "• Все скрипты фильтруются перед публикацией.\n"
        "• Отсекаются скрытые вебхуки, стиллеры куки и аккаунтов.\n"
        "• В канал попадает только чистый безопасный код.\n\n"
        "⚡ <b>2. Быстрые скрипты без зависаний (No Key)</b>\n"
        "• Официальные лоадеры без ключей и бесконечной загрузки.\n\n"
        "📱 <b>3. Свежая Delta Executor в закрепе</b>\n"
        "• Актуальный APK для Android закреплён в канале.\n\n"
        "📊 <b>4. Ежедневные опросы в 12:00</b>\n"
        "• Голосуйте за следующую игру прямо в ленте в 1 клик!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 <b>Получить скрипт:</b> жмите кнопку под постом нужной игры в канале!"
    )

def build_changelog_hype(bot_username: str) -> str:
    """Style 2: Hype / Community 1.1 (Direct from admin, energetic)."""
    return (
        "🔥 <b>ОБНОВЛЕНИЕ 1.1 ОТ АДМИНА!</b> 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Парни, всем привет! На связи админ канала. Собрал для вас обновление 1.1 — теперь всё работает чётко!\n\n"
        "🚀 <b>ЧТО НОВОГО:</b>\n\n"
        "🛡 <b>Проверка на вирусы и стилеры!</b>\n"
        "Никаких вебхуков, грабберов и стилеров куки. Каждый скрипт проверен — ваши аккаунты в безопасности!\n\n"
        "⚡ <b>Никаких зависаний («бесконечной загрузки»)!</b>\n"
        "Поставил официальные быстрые лоадеры без ключей — нажал, вставил в Дельту и сразу играешь!\n\n"
        "📱 <b>Delta Executor всегда под рукой!</b>\n"
        "Свежий APK закреплён в шапке канала — скачал за секунду и погнал тащить.\n\n"
        "📊 <b>Опросы каждый день в 12:00!</b>\n"
        "Голосуйте в 1 тап за игру, на которую хотите следующий чит!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 Жмите кнопку под постом игры в канале — бот @{bot_username} выдаст готовый код!"
    )

def build_changelog_minimal(bot_username: str) -> str:
    """Style 3: Clear & Honest 1.1 (Clean, concise, honest)."""
    return (
        "💎 <b>ОБНОВЛЕНИЕ 1.1 | SCRIPT DROP</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "От админа: краткий отчёт о том, что изменилось и как теперь всё устроено.\n\n"
        "<b>Главные изменения:</b>\n\n"
        "🛡 <b>Проверка на вирусы:</b>\n"
        "Все скрипты проверяются на стилеры данных, Discord-вебхуки и вредоносный код. Вы получаете только чистый loadstring.\n\n"
        "⚡ <b>Исправлены зависания:</b>\n"
        "Убраны багованные скрипты, которые бесконечно грузились. Добавлены стабильные лоадеры без систем ключей.\n\n"
        "📱 <b>Инжектор Delta:</b>\n"
        "Актуальная версия APK для телефона закреплена вверху канала.\n\n"
        "📊 <b>Опросы в канале:</b>\n"
        "Выбирайте игру для следующего релиза каждый день в 12:00.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Скрипты выдаются через бота: @{bot_username}</i>\n"
        "<i>Выбирайте игру в ленте канала и жмите «Получить скрипт»!</i>"
    )

def build_changelog_developer(bot_username: str) -> str:
    """Style 4: Detailed Breakdown 1.1 (Clear explanation of how everything works)."""
    return (
        "🛠 <b>ЧТО НОВОГО В ОБНОВЛЕНИИ 1.1</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Автор обновления:</b> Админ канала\n"
        "<b>Версия:</b> 1.1 Stable\n\n"
        "<b>СПИСОК УЛУЧШЕНИЙ:</b>\n"
        "• <b>[Антивирус / Защита]</b> Внедрена проверка скриптов: отсекаются любые стилеры паролей, IP-логгеры и скрытые вебхуки.\n"
        "• <b>[Стабильность]</b> Устранена бесконечная загрузка — скрипты запускаются сразу и без рекламы.\n"
        "• <b>[Дельта]</b> Закреплена последняя рабочая версия Delta Executor для Android.\n"
        "• <b>[Голосования]</b> Ежедневный опрос в 12:00: подписчики сами выбирают игру для следующего дропа.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📖 <b>КАК ЭТО РАБОТАЕТ:</b>\n"
        "1. Переходите в канал @script_drop\n"
        "2. Нажимаете «🚀 Получить скрипт» под постом\n"
        f"3. Бот @{bot_username} выдаёт проверенный код для вставки в чит."
    )

CHANGELOG_STYLES = {
    "cyber": {
        "name": "⚡ Кибер 1.1",
        "full_name": "⚡ Кибер / Неон 1.1",
        "builder": build_changelog_cyber,
    },
    "hype": {
        "name": "🔥 Хайп 1.1",
        "full_name": "🔥 Хайповый от админа 1.1",
        "builder": build_changelog_hype,
    },
    "minimal": {
        "name": "💎 Простой 1.1",
        "full_name": "💎 Простой и честный 1.1",
        "builder": build_changelog_minimal,
    },
    "dev": {
        "name": "🛠 Разбор 1.1",
        "full_name": "🛠 Подробный разбор 1.1",
        "builder": build_changelog_developer,
    },
}

def get_changelog_text(style: str, bot_username: str) -> str:
    """Returns the changelog formatted in the requested visual style."""
    entry = CHANGELOG_STYLES.get(style) or CHANGELOG_STYLES["cyber"]
    return entry["builder"](bot_username)

def build_changelog_post_text(bot_username: str) -> str:
    """Default backward-compatible changelog generator."""
    return build_changelog_cyber(bot_username)

def get_daily_poll_data() -> Tuple[str, List[str]]:
    """Returns question and options for the daily interactive poll in the channel."""
    question = "🔥 На какую игру выложить следующий скрипт?"
    options = [
        "🍇 Blox Fruits",
        "⚔️ Blade Ball",
        "🥚 Steal an Egg",
        "🎯 Rivals",
        "🔪 Murder Mystery 2",
        "🛏️ BedWars",
        "🚪 Doors",
        "🔫 Da Hood",
        "📦 Другая (напиши боту)",
    ]
    return question, options
