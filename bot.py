import os
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CopyTextButton,
    WebAppInfo,
    FSInputFile,
    CallbackQuery,
    Message,
)
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

import config
import database
import post_builder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# FSM States
class PostCreation(StatesGroup):
    waiting_for_game = State()
    waiting_for_features = State()
    waiting_for_executors = State()
    waiting_for_script = State()

class ChannelSetup(StatesGroup):
    waiting_for_channel = State()

# Initialize Bot and Dispatcher
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())

# Helpers
async def is_admin(user_id: int) -> bool:
    """Checks if user is an admin or if no admin is set yet."""
    saved_admin = await database.get_setting("primary_admin_id")
    if saved_admin and saved_admin.isdigit():
        if int(saved_admin) == user_id:
            return True
    if user_id in config.ADMIN_IDS:
        return True
    if not config.ADMIN_IDS and not saved_admin:
        return True
    return False

async def check_user_subscription(user_id: int, channel: str) -> bool:
    """Strictly checks if user is subscribed to the channel."""
    if not channel:
        return True
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in [
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        ]:
            return True
        return False
    except TelegramBadRequest as e:
        err_msg = str(e).lower()
        if "participant_id_invalid" in err_msg or "user not found" in err_msg:
            return False
        logger.error(f"TelegramBadRequest in subscription check: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in subscription check: {e}")
        return False

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать пост со скриптом", callback_data="admin_create_post")],
            [InlineKeyboardButton(text="📢 Привязать Telegram-канал", callback_data="admin_set_channel")],
            [InlineKeyboardButton(text="📋 Список скриптов", callback_data="admin_list_scripts")],
        ]
    )

def get_webapp_url() -> str:
    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBAPP_URL") or getattr(config, "WEBAPP_URL", "")
    if not url or "vercel.app" in url:
        return "https://roblox-script-bot.onrender.com"
    return url

def build_script_delivery_keyboard(script_code: str, channel_url: str) -> InlineKeyboardMarkup:
    """Creates the exact buttons requested: Copy, Channel, and Open Mini App."""
    buttons = [
        [InlineKeyboardButton(text="Скопировать / Copy", copy_text=CopyTextButton(text=script_code))],
    ]
    row2 = []
    if channel_url:
        row2.append(InlineKeyboardButton(text="⚡ Больше скриптов", url=channel_url))
    app_url = get_webapp_url()
    if app_url:
        row2.append(InlineKeyboardButton(text="📱 Открыть Приложение", web_app=WebAppInfo(url=app_url)))
    if row2:
        buttons.append(row2)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- USER HANDLERS ---

@dp.message(CommandStart())
async def handle_start(message: Message, command: CommandObject):
    user_id = message.from_user.id if message.from_user else 0
    args = command.args
    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    channel_clean = channel.replace("@", "") if channel else "script_drop"
    channel_url = f"https://t.me/{channel_clean}"

    # Check if this is a deep link for a specific script
    if args:
        script_key = args.strip()
        script = await database.get_script(script_key)
        
        if not script:
            await message.answer("⚠️ <b>Скрипт не найден</b> или срок его действия истёк.")
            return

        # Check subscription
        is_sub = await check_user_subscription(user_id, channel)
        if not is_sub:
            sub_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_url)],
                    [InlineKeyboardButton(text="🔄 Проверить подписку", callback_data=f"check_sub:{script_key}")],
                ]
            )
            await message.answer(
                "🔒 <b>Для получения скрипта необходимо подписаться на наш канал:</b>\n\n"
                f"📢 Канал: <b>@{channel_clean}</b>\n\n"
                "После подписки нажмите кнопку <b>«Проверить подписку»</b> 👇",
                reply_markup=sub_kb,
            )
            return

        # User is subscribed -> send the exact format
        delivery_text = post_builder.build_user_delivery_message(script["script_code"])
        delivery_kb = build_script_delivery_keyboard(script["script_code"], channel_url)
        await message.answer(delivery_text, reply_markup=delivery_kb)
        return

    # Regular /start without parameters
    is_sub = await check_user_subscription(user_id, channel)
    is_user_admin = await is_admin(user_id)

    if not is_sub and not is_user_admin:
        sub_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_url)],
                [InlineKeyboardButton(text="🔄 Проверить подписку", callback_data="check_sub:welcome")],
            ]
        )
        await message.answer(
            "🔒 <b>Добро пожаловать в Script Drop! ⚡</b>\n\n"
            "Чтобы пользоваться ботом и открывать скрипты, подпишитесь на наш канал:\n"
            f"📢 <b>@{channel_clean}</b>\n\n"
            "После подписки нажмите кнопку ниже 👇",
            reply_markup=sub_kb,
        )
        return

    welcome_text = (
        "👋 <b>Привет! Добро пожаловать в Roblox Script Bot! ⚡</b>\n\n"
        "Здесь ты можешь получать актуальные и проверенные скрипты для Roblox.\n\n"
        "📌 <i>Все свежие релизы публикуются в нашем канале. "
        "Переходи, выбирай нужную игру и жми «Получить скрипт»!</i>"
    )
    
    keyboard_buttons = []
    first_row = []
    if channel_url:
        first_row.append(InlineKeyboardButton(text="🚀 Перейти в канал", url=channel_url))
    app_url = get_webapp_url()
    if app_url:
        first_row.append(InlineKeyboardButton(text="📱 Открыть Приложение", web_app=WebAppInfo(url=app_url)))
    if first_row:
        keyboard_buttons.append(first_row)
    
    if is_user_admin:
        keyboard_buttons.append([InlineKeyboardButton(text="⚙️ Панель управления", callback_data="open_admin_panel")])
        
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons) if keyboard_buttons else None

    if config.BANNER_PATH.exists():
        photo = FSInputFile(config.BANNER_PATH)
        await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=reply_markup)
    else:
        await message.answer(welcome_text, reply_markup=reply_markup)


@dp.callback_query(F.data.startswith("check_sub:"))
async def handle_check_subscription(call: CallbackQuery):
    user_id = call.from_user.id
    target = call.data.split(":")[1]
    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    channel_clean = channel.replace("@", "") if channel else "script_drop"
    channel_url = f"https://t.me/{channel_clean}"

    is_sub = await check_user_subscription(user_id, channel)
    if not is_sub:
        await call.answer("❌ Вы ещё не подписались на канал! Пожалуйста, сначала подпишитесь на @" + channel_clean, show_alert=True)
        return

    await call.answer("✅ Подписка подтверждена!", show_alert=False)
    try:
        await call.message.delete()
    except Exception:
        pass

    if target == "welcome":
        welcome_text = (
            "👋 <b>Привет! Добро пожаловать в Roblox Script Bot! ⚡</b>\n\n"
            "Здесь ты можешь получать актуальные и проверенные скрипты для Roblox.\n\n"
            "📌 <i>Все свежие релизы публикуются в нашем канале. "
            "Переходи, выбирай нужную игру и жми «Получить скрипт»!</i>"
        )
        buttons = []
        app_url = get_webapp_url()
        row1 = [InlineKeyboardButton(text="🚀 Перейти в канал", url=channel_url)]
        if app_url:
            row1.append(InlineKeyboardButton(text="📱 Открыть Приложение", web_app=WebAppInfo(url=app_url)))
        buttons.append(row1)
        if await is_admin(user_id):
            buttons.append([InlineKeyboardButton(text="⚙️ Панель управления", callback_data="open_admin_panel")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        if config.BANNER_PATH.exists():
            photo = FSInputFile(config.BANNER_PATH)
            await call.message.answer_photo(photo=photo, caption=welcome_text, reply_markup=reply_markup)
        else:
            await call.message.answer(welcome_text, reply_markup=reply_markup)
        return

    # Deliver script
    script = await database.get_script(target)
    if not script:
        await call.message.answer("⚠️ Скрипт не найден или был удалён.")
        return

    delivery_text = post_builder.build_user_delivery_message(script["script_code"])
    delivery_kb = build_script_delivery_keyboard(script["script_code"], channel_url)
    await call.message.answer(delivery_text, reply_markup=delivery_kb)


# --- ADMIN HANDLERS ---

@dp.message(Command("admin"))
async def handle_admin(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    saved_admin = await database.get_setting("primary_admin_id")
    
    if not saved_admin and not config.ADMIN_IDS:
        await database.set_setting("primary_admin_id", str(user_id))
        await message.answer(f"👑 <b>Вы успешно назначены главным администратором бота!</b> (Ваш ID: <code>{user_id}</code>)")

    if not await is_admin(user_id):
        await message.answer("⛔ У вас нет доступа к панели администратора.")
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    channel_display = f"<code>{channel}</code>" if channel else "<i>Не привязан</i>"

    text = (
        "👑 <b>Панель администратора RobloxScript</b>\n\n"
        f"📢 Текущий канал для постов: {channel_display}\n\n"
        "Выберите действие в меню ниже:"
    )
    await message.answer(text, reply_markup=get_admin_menu_keyboard())

@dp.callback_query(F.data == "open_admin_panel")
async def callback_admin_panel(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return
    await call.message.edit_reply_markup(reply_markup=None)
    await handle_admin(call.message)
    await call.answer()

# --- FSM: POST CREATION (WITH EXECUTORS SELECTION) ---

@dp.callback_query(F.data == "admin_create_post")
async def start_create_post(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    await state.set_state(PostCreation.waiting_for_game)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])
    
    await call.message.answer(
        "🎮 <b>Шаг 1 из 4: Название игры</b>\n\n"
        "Напишите название игры (например: <code>steal an egg</code> или <code>blade ball</code>).\n"
        "<i>Бот автоматически исправит регистр и оформит название красиво!</i>",
        reply_markup=cancel_kb,
    )
    await call.answer()

@dp.message(PostCreation.waiting_for_game)
async def process_game_name(message: Message, state: FSMContext):
    raw_name = message.text.strip()
    if not raw_name:
        await message.answer("⚠️ Пожалуйста, введите название текстом.")
        return

    formatted_name = post_builder.format_game_name(raw_name)
    await state.update_data(game_name=formatted_name)
    await state.set_state(PostCreation.waiting_for_features)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ По умолчанию (ESP, AutoFarm, Speed, TP)", callback_data="use_default_features")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
        ]
    )

    await message.answer(
        f"✅ Игра определена: <b>{formatted_name}</b>\n\n"
        "🛠 <b>Шаг 2 из 4: Функционал скрипта</b>\n\n"
        "Напишите функции через запятую (например: <code>есп, авто фарм, скорость, телепорт</code>)\n"
        "Или нажмите кнопку ниже, чтобы использовать стандартный набор:",
        reply_markup=kb,
    )

@dp.callback_query(PostCreation.waiting_for_features, F.data == "use_default_features")
async def process_default_features(call: CallbackQuery, state: FSMContext):
    await state.update_data(features=post_builder.DEFAULT_FEATURES)
    await prompt_for_executors(call.message, state)
    await call.answer()

@dp.message(PostCreation.waiting_for_features)
async def process_custom_features(message: Message, state: FSMContext):
    custom_features = message.text.strip()
    formatted = post_builder.format_features(custom_features)
    await state.update_data(features=formatted)
    await prompt_for_executors(message, state)

async def prompt_for_executors(message: Message, state: FSMContext):
    await state.set_state(PostCreation.waiting_for_executors)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💻+📱 Все (PC + Mobile: Delta, Arceus X, Fluxus, Codex, Solara)", callback_data="exec_all")],
            [InlineKeyboardButton(text="📱 Только Мобильные (Delta, Arceus X, Fluxus, Codex)", callback_data="exec_mobile")],
            [InlineKeyboardButton(text="💻 Только ПК (Solara, Wave, Celery)", callback_data="exec_pc")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
        ]
    )
    await message.answer(
        "📱 <b>Шаг 3 из 4: На каких экзекуторах работает скрипт?</b>\n\n"
        "Выберите готовый вариант ниже или отправьте текстом свой список поддерживаемых инжекторов:",
        reply_markup=kb,
    )

@dp.callback_query(PostCreation.waiting_for_executors, F.data.startswith("exec_"))
async def process_executor_choice(call: CallbackQuery, state: FSMContext):
    choice = call.data
    mapping = {
        "exec_all": "ПК и Мобильные (Delta, Arceus X, Fluxus, Codex, Solara)",
        "exec_mobile": "Только Мобильные (Delta, Arceus X, Fluxus, Codex)",
        "exec_pc": "Только ПК (Solara, Wave, Celery)",
    }
    chosen_text = mapping.get(choice, post_builder.DEFAULT_EXECUTORS)
    await state.update_data(executors=chosen_text)
    await state.set_state(PostCreation.waiting_for_script)
    await call.message.edit_reply_markup(reply_markup=None)

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])
    await call.message.answer(
        f"✅ Поддержка: <b>{chosen_text}</b>\n\n"
        "📜 <b>Шаг 4 из 4: Ссылка или код скрипта</b>\n\n"
        "Отправьте команду запуска (loadstring) или ссылку, например:\n"
        "<code>loadstring(game:HttpGet(\"https://raw.githubusercontent.com/...\"))()</code>",
        reply_markup=cancel_kb,
    )
    await call.answer()

@dp.message(PostCreation.waiting_for_executors)
async def process_custom_executors(message: Message, state: FSMContext):
    custom = message.text.strip()
    await state.update_data(executors=custom)
    await state.set_state(PostCreation.waiting_for_script)

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])
    await message.answer(
        f"✅ Поддержка: <b>{custom}</b>\n\n"
        "📜 <b>Шаг 4 из 4: Ссылка или код скрипта</b>\n\n"
        "Отправьте команду запуска (loadstring) или ссылку, например:\n"
        "<code>loadstring(game:HttpGet(\"https://raw.githubusercontent.com/...\"))()</code>",
        reply_markup=cancel_kb,
    )

@dp.message(PostCreation.waiting_for_script)
async def process_script_code(message: Message, state: FSMContext):
    script_code = message.text.strip()
    if not script_code:
        await message.answer("⚠️ Пожалуйста, отправьте код или ссылку на скрипт.")
        return

    data = await state.get_data()
    game_name = data.get("game_name", "Roblox Game")
    features = data.get("features", post_builder.DEFAULT_FEATURES)
    executors = data.get("executors", post_builder.DEFAULT_EXECUTORS)

    # Save to SQLite Database
    script_key = await database.add_script(
        game_name=game_name,
        features=features,
        script_code=script_code,
        executors=executors,
    )
    await state.clear()

    # Generate Channel Post text
    channel_post_text = post_builder.build_channel_post(game_name, features, executors)
    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    deep_link = f"https://t.me/{bot_user}?start={script_key}"

    # Preview keyboard
    action_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Получить скрипт (Ссылка)", url=deep_link)],
            [InlineKeyboardButton(text="📢 Опубликовать в канал", callback_data=f"publish_post:{script_key}")],
            [InlineKeyboardButton(text="👑 В меню админа", callback_data="open_admin_panel")],
        ]
    )

    await message.answer("🎉 <b>Скрипт успешно сохранён в базе данных!</b>\nВот как выглядит готовый пост для канала:")

    # Send post preview with banner
    if config.BANNER_PATH.exists():
        photo = FSInputFile(config.BANNER_PATH)
        await message.answer_photo(
            photo=photo,
            caption=channel_post_text,
            reply_markup=action_kb,
        )
    else:
        await message.answer(channel_post_text, reply_markup=action_kb)

# --- PUBLISHING TO CHANNEL ---

@dp.callback_query(F.data.startswith("publish_post:"))
async def publish_to_channel(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    script_key = call.data.split(":")[1]
    script = await database.get_script(script_key)
    if not script:
        await call.answer("⚠️ Скрипт не найден!", show_alert=True)
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    if not channel:
        await call.answer("⚠️ Канал ещё не привязан! Сначала привяжите канал в меню админа.", show_alert=True)
        return

    executors = script.get("executors", post_builder.DEFAULT_EXECUTORS)
    post_text = post_builder.build_channel_post(script["game_name"], script["features"], executors)
    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    deep_link = f"https://t.me/{bot_user}?start={script_key}"

    post_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Получить скрипт", url=deep_link)]
        ]
    )

    try:
        if config.BANNER_PATH.exists():
            photo = FSInputFile(config.BANNER_PATH)
            await bot.send_photo(
                chat_id=channel,
                photo=photo,
                caption=post_text,
                reply_markup=post_kb,
            )
        else:
            await bot.send_message(
                chat_id=channel,
                text=post_text,
                reply_markup=post_kb,
            )
        await call.answer("✅ Пост успешно опубликован в канал!", show_alert=True)
    except Exception as e:
        logger.error(f"Failed to post to channel: {e}")
        await call.answer(
            f"❌ Ошибка публикации: {e}\n\nУбедитесь, что бот добавлен в канал администратором с правом публикации сообщений!",
            show_alert=True,
        )

# --- CHANNEL SETUP ---

@dp.callback_query(F.data == "admin_set_channel")
async def start_channel_setup(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    await state.set_state(ChannelSetup.waiting_for_channel)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])
    
    await call.message.answer(
        "📢 <b>Привязка Telegram-канала</b>\n\n"
        "1. Добавьте бота <b>@" + (config.BOT_USERNAME) + "</b> в свой канал как <b>Администратора</b> (с правами на публикацию сообщений).\n"
        "2. Отправьте сюда юзернейм канала (например: <code>@script_drop</code>) или перешлите любой пост из него сюда:",
        reply_markup=cancel_kb,
    )
    await call.answer()

@dp.message(ChannelSetup.waiting_for_channel)
async def process_channel_input(message: Message, state: FSMContext):
    channel_identifier = None
    
    if message.forward_from_chat and message.forward_from_chat.type == "channel":
        channel_identifier = str(message.forward_from_chat.id)
    elif message.text:
        text = message.text.strip()
        if text.startswith("@") or text.startswith("-100") or text.isdigit():
            channel_identifier = text
            
    if not channel_identifier:
        await message.answer("⚠️ Не удалось распознать канал. Отправьте юзернейм в формате <code>@channel_name</code>.")
        return

    await database.set_setting("channel_id", channel_identifier)
    await state.clear()
    
    await message.answer(
        f"✅ Канал успешно привязан: <code>{channel_identifier}</code>!\n"
        "Теперь при создании постов вы сможете сразу публиковать их одной кнопкой.",
        reply_markup=get_admin_menu_keyboard(),
    )

# --- SCRIPTS LIST ---

@dp.callback_query(F.data == "admin_list_scripts")
async def list_scripts_handler(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    scripts = await database.get_all_scripts(limit=10)
    if not scripts:
        await call.answer("База скриптов пока пуста!", show_alert=True)
        return

    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME

    text_lines = ["📋 <b>Последние 10 скриптов:</b>\n"]
    for s in scripts:
        link = f"https://t.me/{bot_user}?start={s['script_key']}"
        text_lines.append(
            f"🔹 <b>{s['game_name']}</b> (Ключ: <code>{s['script_key']}</code>)\n"
            f"📱 Поддержка: <i>{s.get('executors', 'Все')}</i>\n"
            f"🔗 <a href=\"{link}\">Ссылка на скрипт</a>\n"
        )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад в меню", callback_data="open_admin_panel")]]
    )

    await call.message.answer("\n".join(text_lines), reply_markup=kb, disable_web_page_preview=True)
    await call.answer()

# --- CANCEL FSM ---

@dp.callback_query(F.data == "cancel_fsm")
async def cancel_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Действие отменено.")
    await call.answer()

# --- WEB SERVER FOR MINI APP API ---

async def webapp_html_handler(request):
    html_file = config.WEBAPP_DIR / "index.html"
    if html_file.exists():
        return web.FileResponse(html_file)
    return web.Response(text="Mini App HTML not found", status=404)

async def api_scripts_handler(request):
    scripts = await database.get_all_scripts(limit=50)
    return web.json_response(scripts)

async def api_check_sub_handler(request):
    try:
        user_id = int(request.query.get("user_id", 0))
    except (ValueError, TypeError):
        user_id = 0
    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    is_sub = await check_user_subscription(user_id, channel)
    return web.json_response({"subscribed": is_sub})

def create_web_app():
    app = web.Application()
    app.router.add_get("/", webapp_html_handler)
    app.router.add_get("/api/scripts", api_scripts_handler)
    app.router.add_get("/api/check_sub", api_check_sub_handler)
    return app

# --- MAIN ---

async def main():
    logger.info("Initializing database...")
    await database.init_db()

    # Start web server for Web App (supports HuggingFace Spaces and local)
    port = int(os.getenv("PORT", 7860))
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web App server started on http://0.0.0.0:{port}")

    logger.info("Starting bot polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
