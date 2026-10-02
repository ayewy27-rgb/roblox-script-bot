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
    "99 nights in the forest": (
        "• ESP (ВХ на монстров, выживших, лагерь и лут)\n"
        "• Unlimited Health / Godmode (Бессмертие и защита от любого урона)\n"
        "• Infinite Saplings & Auto Farm (Бесконечные саженцы и авто-фарм)\n"
        "• Auto Eat & Food Selection (Авто-еда и выбор припасов)\n"
        "• Fly, Noclip, Speed & Teleport (Полёт сквозь стены и быстрый ТП)"
    ),
    "99 ночей": (
        "• ESP (ВХ на монстров, выживших, лагерь и лут)\n"
        "• Unlimited Health / Godmode (Бессмертие и защита от любого урона)\n"
        "• Infinite Saplings & Auto Farm (Бесконечные саженцы и авто-фарм)\n"
        "• Auto Eat & Food Selection (Авто-еда и выбор припасов)\n"
        "• Fly, Noclip, Speed & Teleport (Полёт сквозь стены и быстрый ТП)"
    ),
    "the strongest battlegrounds": (
        "• Auto Combo & Skill Spam (Авто-комбо способностей без задержки)\n"
        "• Auto Block & Counter (Идеальное блокирование ударов)\n"
        "• Teleport Behind Target (Мгновенный телепорт за спину врага)\n"
        "• Infinite Awakening / Ult (Бесконечный режим пробуждения)\n"
        "• ESP Players & HP Bar (Подсветка здоровья и энергии игроков)"
    ),
    "tsb": (
        "• Auto Combo & Skill Spam (Авто-комбо способностей без задержки)\n"
        "• Auto Block & Counter (Идеальное блокирование ударов)\n"
        "• Teleport Behind Target (Мгновенный телепорт за спину врага)\n"
        "• Infinite Awakening / Ult (Бесконечный режим пробуждения)\n"
        "• ESP Players & HP Bar (Подсветка здоровья и энергии игроков)"
    ),
    "arsenal": (
        "• Silent Aim (Скрытый аимбот в голову сквозь преграды)\n"
        "• Box & Skeleton ESP (Полный ВХ на всех врагов)\n"
        "• Instant Kill & Rapid Fire (Мгновенный выстрел без отдачи)\n"
        "• Infinite Ammo (Бесконечные патроны)\n"
        "• Speed & BunnyHop (Быстрое перемещение и распрыжка)"
    ),
    "counter blox": (
        "• Silent Aim (Скрытая авто-наводка в голову)\n"
        "• Wallbang & Penetration (Прострел любых стен)\n"
        "• Skin Changer (Все скины на оружие и ножи бесплатно)\n"
        "• 2D Box & Skeleton ESP (ВХ на всех противников)\n"
        "• No Recoil & Rapid Fire (Стрельба без отдачи)"
    ),
    "evade": (
        "• Bot & Nextbot ESP (Отображение ботов и дистанции до них)\n"
        "• Auto Revive Teammates (Мгновенное поднятие союзников)\n"
        "• Auto Drink Cola / Speed (Бесконечное ускорение и распрыжка)\n"
        "• Godmode against Bots (Защита от урона некстботов)\n"
        "• Teleport to Safe Zone (Быстрый ТП в безопасную зону)"
    ),
    "slap battles": (
        "• Slap Aura 360° (Авто-пощечины всем вокруг без промаха)\n"
        "• Anti-Void (Защита от падения в пустоту)\n"
        "• Godmode / Safe Island (Неуязвимость от чужих перчаток)\n"
        "• Glove & Badge Auto Farm (Автоматическое открытие перчаток)\n"
        "• Speed & Infinite Jump (Быстрое перемещение)"
    ),
    "bee swarm simulator": (
        "• Auto Field & Pollen Farm (Авто-сбор пыльцы на лучших полях)\n"
        "• Auto Convert Honey (Автоматическая переработка мёда в улье)\n"
        "• Auto Kill Monsters & Bosses (Авто-убийство жуков и боссов)\n"
        "• Speed & Infinite Jump (Мгновенное передвижение)\n"
        "• Token & Treat Sniper (Авто-подбор всех токенов)"
    ),
    "tower of hell": (
        "• Instant Win / Teleport to Top (Мгновенный телепорт на вершину башни)\n"
        "• Godmode / Anti-Laser (Защита от лазеров и смертельных зон)\n"
        "• Fly & Infinite Jump (Свободный полёт и прыжки в воздухе)\n"
        "• Remove Killparts (Полное удаление опасных блоков)\n"
        "• Free Items / Unlock All (Разблокировка всех эффектов)"
    ),
    "build a boat for treasure": (
        "• Instant Win / Treasure TP (Мгновенная победа и фарм золота)\n"
        "• Auto Buy Chests (Авто-покупка сундуков с деталями)\n"
        "• Fly & Noclip Mode (Полёт по всей карте сквозь препятствия)\n"
        "• Infinite Blocks Glitch (Бесконечные материалы)\n"
        "• Godmode (Полная неуязвимость лодки и персонажа)"
    ),
    "muscle legends": (
        "• Auto Strength (Мгновенный авто-клик и кач силы)\n"
        "• Auto Rebirth (Автоматическое перерождение)\n"
        "• Auto Brawl / Kill All (Авто-атака всех игроков на арене)\n"
        "• Fast Punch (Удар без задержки)\n"
        "• Gem & Pet Auto Farm (Авто-фарм кристаллов и лучших питомцев)"
    ),
    "dandy's world": (
        "• Auto Complete Machines (Мгновенная починка машин)\n"
        "• Twisteds / Monster ESP (ВХ на монстров и дистанцию)\n"
        "• Infinite Stamina (Бесконечный бег без усталости)\n"
        "• Item & Capsule ESP (Подсветка капсул и предметов)\n"
        "• Speed Boost & Safe TP (Увеличенная скорость и безопасный ТП)"
    ),
    "pressure": (
        "• Entity & Monster Alert (Предупреждение о появлении монстров)\n"
        "• Keycard & Door ESP (Подсветка карточек доступа и проходов)\n"
        "• Fullbright & No Fog (Яркое подводное освещение без тумана)\n"
        "• Auto Unlock / Fast Interaction (Мгновенное открытие дверей)\n"
        "• Speed & Infinite Breath (Ускорение и бесконечный кислород)"
    ),
    "survive the killer": (
        "• Killer & Survivor ESP (Подсветка маньяка и игроков)\n"
        "• Auto Revive & Fast Escape (Мгновенное спасение и выход)\n"
        "• Speed & Fly (Высокая скорость передвижения)\n"
        "• Auto Loot Chests (Авто-сбор всех сундуков на карте)\n"
        "• Godmode / Invisibility (Невидимость для убийцы)"
    ),
    "bloxstrike": (
        "• Silent Aim (Скрытая авто-наводка в голову)\n"
        "• Wallbang (Прострел любых стен и укрытий)\n"
        "• Skin Changer (Все скины на оружие и ножи бесплатно)\n"
        "• 2D Box & Skeleton ESP (ВХ на всех противников)\n"
        "• No Recoil & Rapid Fire (Стрельба без отдачи)"
    ),
    "san diego": (
        "• Smuggle Autofarm (Авто-фарм контрабанды)\n"
        "• Truck & Boat Autofarm (Авто-фарм на грузовиках и лодках)\n"
        "• Police Auto-Detect & ESP (Оповещение о полиции и ВХ)\n"
        "• Speed & Fly (Увеличенная скорость транспорта)\n"
        "• Infinite Fuel & Nitro (Бесконечное топливо)"
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
    """Style 1: Cyber / Neon Hotfix (Sharp, stylish, from the admin)."""
    return (
        "⚡ <b>ХОТФИКС 1.1.1 | ВСЁ ЗАФИКСИЛИ!</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>На связи админ канала. Срочный хотфикс: обновили бота по вашим отзывам!</i>\n\n"
        "🔥 <b>ЧТО ИЗМЕНИЛОСЬ ДЛЯ ВАС:</b>\n\n"
        "🔑 <b>1. Строго БЕЗ КЛЮЧЕЙ (100% Keyless)</b>\n"
        "• Больше никаких Linkvertise, рекламы и выпрашивания ключей.\n"
        "• Все читы запускаются сразу в 1 клик без чекпоинтов.\n\n"
        "💡 <b>2. Можно предложить игру боту</b>\n"
        "• Проголосовали в опросе за «Другая (напиши боту)»?\n"
        f"• Теперь можно просто написать название игры боту (@{bot_username}) — и мы выложим готовый скрипт в канал!\n\n"
        "📋 <b>3. Вернули кнопку «Скопировать скрипт»</b>\n"
        "• Кнопка снова под каждым скриптом — код копируется в буфер за 1 тап.\n\n"
        "📊 <b>4. Починили ежедневный опрос</b>\n"
        "• Баг с голосованием в канале устранён, всё работает стабильно.\n\n"
        "🛡 <b>5. Чистый код без вирусов</b>\n"
        "• 0 стилеров, 0 скрытых ссылок — полная безопасность.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Забирайте готовые скрипты:</b> @{bot_username}"
    )

def build_changelog_hype(bot_username: str) -> str:
    """Style 2: Hype / Community Hotfix (Direct from admin, energetic)."""
    return (
        "🔥 <b>СРОЧНЫЙ ХОТФИКС ОТ АДМИНА!</b> 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Парни, всем салют! Админ на связи. Оперативно пофиксил всё, о чём вы просили — забирайте обнову!\n\n"
        "🚀 <b>ЧТО НОВОГО ДЛЯ ВАС:</b>\n\n"
        "🔑 <b>Только скрипты БЕЗ КЛЮЧЕЙ!</b>\n"
        "Никаких ссылок на получение ключа, капч и рекламы. Вставил в чит — и сразу играешь!\n\n"
        "💡 <b>Кнопка «Предложить игру / скрипт»!</b>\n"
        "Если в канале нет вашей любимой игры или проголосовали за «Другая» — просто напишите боту, и я найду и выложу готовый чит!\n\n"
        "📋 <b>Вернул кнопку копирования!</b>\n"
        "Кнопка «Скопировать скрипт» снова на месте — один клик и код у вас в буфере.\n\n"
        "📊 <b>Починил опросы в канале!</b>\n"
        "Голосовалка за следующую игру теперь отправляется без ошибок каждый день.\n\n"
        "🛡 <b>Проверка на вирусы на 100%!</b>\n"
        "Все читы проверены, аккаунты в полной безопасности.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Жмите «Получить скрипт» под постом нужной игры и забирайте готовый код в @{bot_username}!"
    )

def build_changelog_minimal(bot_username: str) -> str:
    """Style 3: Clear & Honest Hotfix (Clean, concise, honest)."""
    return (
        "💎 <b>ХОТФИКС 1.1.1 | SCRIPT DROP</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "От админа: коротко о том, что исправили для подписчиков.\n\n"
        "<b>Список изменений:</b>\n\n"
        "🔑 <b>Скрипты без ключей:</b>\n"
        "Убраны любые скрипты с ключами. Только чистый Keyless, работающий сразу.\n\n"
        "💡 <b>Предложить свою игру:</b>\n"
        "В боте появился раздел «Предложить скрипт / игру» для ваших запросов.\n\n"
        "📋 <b>Кнопка копирования:</b>\n"
        "Под каждым скриптом возвращена удобная кнопка «Скопировать скрипт».\n\n"
        "📊 <b>Исправление опросов:</b>\n"
        "Устранена ошибка при отправке ежедневных опросов в канал.\n\n"
        "🛡 <b>Безопасность:</b>\n"
        "Все читы отфильтрованы от вредоносного кода и стилеров.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Бот выдачи скриптов: @{bot_username}</i>"
    )

def build_changelog_developer(bot_username: str) -> str:
    """Style 4: Detailed Breakdown Hotfix (Clear explanation)."""
    return (
        "🛠 <b>ОТЧЁТ ОБ ИСПРАВЛЕНИЯХ (ХОТФИКС 1.1.1)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Автор:</b> Админ канала\n"
        "<b>Версия:</b> Hotfix 1.1.1\n\n"
        "<b>ЧТО БЫЛО СДЕЛАНО ДЛЯ ПОДПИСЧИКОВ:</b>\n"
        "• <b>[Keyless Only]</b> Все скрипты работают без систем ключей, без Linkvertise и без рекламы.\n"
        "• <b>[Запросы игроков]</b> Добавлен раздел «💡 Предложить скрипт»: вы можете запросить чит на любую игру прямо в боте.\n"
        "• <b>[Интерфейс]</b> Восстановлена кнопка «📋 Скопировать скрипт» (быстрое копирование в буфер обмена).\n"
        "• <b>[Опросы канала]</b> Исправлен сбой при публикации опросов в канал @script_drop.\n"
        "• <b>[Безопасность]</b> Подтверждена чистота всех скриптов (без стилеров и RAT).\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Бот:</b> @{bot_username} — выбирайте игру в ленте и жмите «Получить скрипт»!"
    )

CHANGELOG_STYLES = {
    "cyber": {
        "name": "⚡ Кибер Хотфикс",
        "full_name": "⚡ Кибер / Неон (Хотфикс)",
        "builder": build_changelog_cyber,
    },
    "hype": {
        "name": "🔥 Хайп Хотфикс",
        "full_name": "🔥 Хайповый от админа (Хотфикс)",
        "builder": build_changelog_hype,
    },
    "minimal": {
        "name": "💎 Простой Хотфикс",
        "full_name": "💎 Простой и честный (Хотфикс)",
        "builder": build_changelog_minimal,
    },
    "dev": {
        "name": "🛠 Разбор Хотфикс",
        "full_name": "🛠 Подробный разбор (Хотфикс)",
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
