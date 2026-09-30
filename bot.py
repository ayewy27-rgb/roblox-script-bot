import os
import asyncio
import logging
import sys
import re
from datetime import datetime, timezone, timedelta
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
import aiohttp
from aiohttp import web

import config
import database
import post_builder
import script_finder

# Timezone GMT+5
TZ_GMT5 = timezone(timedelta(hours=5))

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

class DeltaUpload(StatesGroup):
    waiting_for_apk = State()

class AdminScriptSearch(StatesGroup):
    waiting_for_game_query = State()

# Initialize Bot and Dispatcher
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())

# Permanent Master Admin (@olarbebe)
PRIMARY_ADMIN_ID = 5891418490

# Helpers
async def is_admin(user_id: int) -> bool:
    """Checks if user is an admin."""
    if user_id == PRIMARY_ADMIN_ID:
        return True
    if user_id in config.ADMIN_IDS:
        return True
    saved_admin = await database.get_setting("primary_admin_id")
    if saved_admin and saved_admin.isdigit() and int(saved_admin) == user_id:
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

def get_webapp_url() -> str:
    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBAPP_URL") or getattr(config, "WEBAPP_URL", "")
    if not url or "vercel.app" in url:
        return "https://roblox-script-bot.onrender.com"
    return url

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Поиск скриптов по базам (PulseHub / Blox)", callback_data="admin_search_scripts")],
            [InlineKeyboardButton(text="➕ Создать пост со скриптом", callback_data="admin_create_post")],
            [InlineKeyboardButton(text="📱 Обновить Delta APK (Автодельта)", callback_data="admin_upload_delta")],
            [InlineKeyboardButton(text="📊 Ежедневный опрос в канал (12:00)", callback_data="admin_autopost_menu")],
            [InlineKeyboardButton(text="📢 Опубликовать Changelog в канал", callback_data="admin_post_changelog")],
            [InlineKeyboardButton(text="📌 Опубликовать шапку канала", callback_data="admin_post_header")],
            [InlineKeyboardButton(text="📢 Привязать Telegram-канал", callback_data="admin_set_channel")],
            [InlineKeyboardButton(text="📋 Список скриптов", callback_data="admin_list_scripts")],
        ]
    )

def build_script_delivery_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📢 Наш канал со скриптами ↗", url=channel_url or "https://t.me/script_drop")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def deliver_script_to_user(chat_id: int, script: dict, channel_url: str):
    """Delivers script to user exactly matching Screenshot 2 (banner + lua code + channel link)."""
    delivery_text = post_builder.build_user_delivery_message(
        game_name=script.get("game_name", "Roblox"),
        script_code=script.get("script_code", "")
    )
    delivery_kb = build_script_delivery_keyboard(channel_url)
    
    delivery_banner = getattr(config, "BANNER_DELIVERY", None)
    banner_to_use = delivery_banner if (delivery_banner and delivery_banner.exists()) else config.BANNER_PATH
    
    if banner_to_use.exists():
        photo = FSInputFile(banner_to_use)
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=delivery_text,
            reply_markup=delivery_kb,
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=delivery_text,
            reply_markup=delivery_kb,
        )



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

        # Record user received this script in history
        await database.record_user_received(user_id, script_key)

        # Deliver script (matches Screenshot 2)
        await deliver_script_to_user(message.chat.id, script, channel_url)
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
        "👋 <b>Привет! Добро пожаловать в Script Drop! ⚡</b>\n\n"
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

    welcome_banner = getattr(config, "BANNER_WELCOME", None)
    banner_file = welcome_banner if (welcome_banner and welcome_banner.exists()) else config.BANNER_PATH

    if banner_file.exists():
        photo = FSInputFile(banner_file)
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
            "👋 <b>Привет! Добро пожаловать в Script Drop! ⚡</b>\n\n"
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
        
        welcome_banner = getattr(config, "BANNER_WELCOME", None)
        banner_file = welcome_banner if (welcome_banner and welcome_banner.exists()) else config.BANNER_PATH
        if banner_file.exists():
            photo = FSInputFile(banner_file)
            await call.message.answer_photo(photo=photo, caption=welcome_text, reply_markup=reply_markup)
        else:
            await call.message.answer(welcome_text, reply_markup=reply_markup)
        return

    # Deliver script
    script = await database.get_script(target)
    if not script:
        await call.message.answer("⚠️ Скрипт не найден или был удалён.")
        return

    await database.record_user_received(user_id, target)
    await deliver_script_to_user(call.message.chat.id, script, channel_url)



# --- ADMIN HANDLERS ---

async def send_admin_panel(chat_id: int, user_id: int):
    """Sends the admin control panel to authorized admins."""
    if not await is_admin(user_id):
        await bot.send_message(chat_id=chat_id, text="⛔ У вас нет доступа к панели администратора.")
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    channel_display = f"<code>{channel}</code>" if channel else "<i>Не привязан</i>"
    kb = get_admin_menu_keyboard()

    text = (
        "👑 <b>Панель администратора Script Drop</b>\n\n"
        f"📢 Текущий канал для постов: {channel_display}\n\n"
        "Выберите действие в меню ниже:"
    )
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=kb)

@dp.message(Command("admin"))
async def handle_admin(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    await send_admin_panel(chat_id=message.chat.id, user_id=user_id)

@dp.callback_query(F.data == "open_admin_panel")
async def callback_admin_panel(call: CallbackQuery):
    user_id = call.from_user.id
    if not await is_admin(user_id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return
    await send_admin_panel(chat_id=call.message.chat.id, user_id=user_id)
    await call.answer()

# --- FSM: MANUAL POST CREATION ---

@dp.callback_query(F.data == "admin_create_post")
async def start_create_post(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    await state.set_state(PostCreation.waiting_for_game)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])
    
    await call.message.answer(
        "🎮 <b>Шаг 1 из 4: Название игры</b>\n\n"
        "Напишите название игры (например: <code>steal an egg</code> или <code>blade ball</code>):",
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
            [InlineKeyboardButton(text="🤖 Сгенерировать функционал (ИИ)", callback_data="use_ai_features")],
            [InlineKeyboardButton(text="⚡ По умолчанию (ESP, AutoFarm, Speed, TP)", callback_data="use_default_features")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
        ]
    )

    await message.answer(
        f"✅ Игра определена: <b>{formatted_name}</b>\n\n"
        "🛠 <b>Шаг 2 из 4: Функционал скрипта</b>\n\n"
        "Напишите функции через запятую или нажмите кнопку ниже (ИИ подберёт лучший функционал):",
        reply_markup=kb,
    )

@dp.callback_query(PostCreation.waiting_for_features, F.data == "use_ai_features")
async def process_ai_features(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    game_name = data.get("game_name", "Roblox")
    ai_features = post_builder.generate_ai_features(game_name)
    await state.update_data(features=ai_features)
    await prompt_for_executors(call.message, state)
    await call.answer("🤖 Функционал сгенерирован ИИ!")

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
        "📱 <b>Шаг 3 из 4: На каких экзекуторах работает скрипт?</b>",
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
        "Отправьте команду запуска (loadstring) или ссылку:",
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
        "📜 <b>Шаг 4 из 4: Ссылка или код скрипта</b>:",
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

    script_key = await database.add_script(
        game_name=game_name,
        features=features,
        script_code=script_code,
        executors=executors,
    )
    await state.clear()

    channel_post_text = post_builder.build_channel_post(game_name, features, executors)
    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    deep_link = f"https://t.me/{bot_user}?start={script_key}"

    action_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Получить скрипт (Ссылка)", url=deep_link)],
            [InlineKeyboardButton(text="📢 Опубликовать в канал", callback_data=f"publish_post:{script_key}")],
            [InlineKeyboardButton(text="👑 В меню админа", callback_data="open_admin_panel")],
        ]
    )

    await message.answer("🎉 <b>Скрипт успешно сохранён в базе данных!</b>")

    if config.BANNER_PATH.exists():
        photo = FSInputFile(config.BANNER_PATH)
        await message.answer_photo(photo=photo, caption=channel_post_text, reply_markup=action_kb)
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
        await call.answer("⚠️ Канал ещё не привязан!", show_alert=True)
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
            sent = await bot.send_photo(chat_id=channel, photo=photo, caption=post_text, reply_markup=post_kb)
        else:
            sent = await bot.send_message(chat_id=channel, text=post_text, reply_markup=post_kb)
        await database.update_script_channel_post(script_key, sent.message_id)
        await call.answer("✅ Пост успешно опубликован в канал!", show_alert=True)
    except Exception as e:
        logger.error(f"Failed to post to channel: {e}")
        await call.answer(f"❌ Ошибка публикации: {e}", show_alert=True)

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
        "Отправьте юзернейм канала (например: <code>@script_drop</code>):",
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
    kb = get_admin_menu_keyboard()
    await message.answer(f"✅ Канал успешно привязан: <code>{channel_identifier}</code>!", reply_markup=kb)

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

    text_lines = ["📋 <b>Последние скрипты:</b>\n"]
    for s in scripts:
        link = f"https://t.me/{bot_user}?start={s['script_key']}"
        text_lines.append(
            f"🔹 <b>{s['game_name']}</b> (Ключ: <code>{s['script_key']}</code>)\n"
            f"🔗 <a href=\"{link}\">Ссылка</a>\n"
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


# --- AUTO DELTA EXECUTOR (APK AUTO-UPDATER) ---

def extract_delta_version(file_name: str) -> str:
    """Extracts version like v2.648, 2.648, v2_648 from filename."""
    match = re.search(r'[vV]?(\d+[\.\-_]\d+(?:[\.\-_]\d+)?)', file_name)
    if match:
        v = match.group(1).replace('_', '.').replace('-', '.')
        return f"v{v}" if not v.startswith('v') else v
    return "Последняя версия (Latest)"

@dp.callback_query(F.data == "admin_upload_delta")
async def start_delta_upload(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    await state.set_state(DeltaUpload.waiting_for_apk)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])

    await call.message.answer(
        "📱 <b>Загрузка новой версии Delta Executor (Автодельта)</b>\n\n"
        "Отправьте мне файл <code>.apk</code> новой версии (например: <code>Delta_v2.648.apk</code>).\n\n"
        "🤖 <b>Что сделает бот автоматически:</b>\n"
        "1. Распознает версию из названия файла\n"
        "2. Удалит предыдущий закреплённый пост с Дельтой в канале\n"
        "3. Опубликует файл APK с инструкцией по установке\n"
        "4. Закрепит новую версию в канале @script_drop!",
        reply_markup=cancel_kb,
    )
    await call.answer()

@dp.message(F.document)
async def handle_document_upload(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    doc = message.document
    file_name = doc.file_name or "Delta.apk"
    is_apk = file_name.lower().endswith(".apk") or "delta" in file_name.lower()

    curr_state = await state.get_state()
    if not is_apk and curr_state != DeltaUpload.waiting_for_apk:
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    if not channel:
        await message.answer("⚠️ Канал ещё не привязан! Сначала привяжите канал в /admin.")
        return

    version = extract_delta_version(file_name)
    channel_clean = channel.replace("@", "")
    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME

    status_msg = await message.answer(f"⏳ <b>Публикация Delta {version} в канал @{channel_clean}...</b>")

    # 1. Delete or unpin previous Delta message if exists
    old_msg_id = await database.get_setting("last_delta_message_id")
    if old_msg_id and old_msg_id.isdigit():
        try:
            await bot.delete_message(chat_id=channel, message_id=int(old_msg_id))
            logger.info(f"Deleted old Delta post {old_msg_id} from {channel}")
        except Exception as e:
            logger.warning(f"Could not delete old Delta post {old_msg_id}: {e}")
            try:
                await bot.unpin_chat_message(chat_id=channel, message_id=int(old_msg_id))
            except Exception:
                pass

    caption = (
        f"📱 <b>DELTA EXECUTOR | ПОСЛЕДНЯЯ ВЕРСИЯ ДЛЯ ТЕЛЕФОНА</b> 📱\n\n"
        f"⚡ <b>Версия:</b> <code>{version}</code>\n"
        f"🤖 <b>Платформа:</b> Android (Телефон / Планшет)\n"
        f"🛡 <b>Статус:</b> 🟢 <i>Работает / Undetected</i>\n\n"
        f"📝 <b>Инструкция по установке:</b>\n"
        f"1️⃣ Скачайте файл <code>{file_name}</code> выше\n"
        f"2️⃣ Установите APK на телефон (если пишет «Файл может быть опасным» — нажмите «Всё равно установить», это ложное срабатывание антивируса на любой игровой чит)\n"
        f"3️⃣ Запустите установленный Roblox и зайдите в нужную игру\n"
        f"4️⃣ Копируйте скрипты из нашего канала @{channel_clean} через бота @{bot_user} и вставляйте в консоль Delta!\n\n"
        f"🚀 <b>Приятной игры без банов!</b>"
    )

    delta_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Получить скрипты для игр", url=f"https://t.me/{bot_user}")],
            [InlineKeyboardButton(text="📢 Наш канал со скриптами", url=f"https://t.me/{channel_clean}")],
        ]
    )

    try:
        sent_file = await bot.send_document(
            chat_id=channel,
            document=doc.file_id,
            caption=caption,
            reply_markup=delta_kb,
        )

        try:
            await bot.pin_chat_message(chat_id=channel, message_id=sent_file.message_id, disable_notification=False)
        except Exception as e:
            logger.warning(f"Failed to pin Delta message: {e}")

        await database.set_setting("last_delta_message_id", str(sent_file.message_id))
        await database.set_setting("last_delta_version", version)

        await status_msg.edit_text(
            f"✅ <b>Delta Executor успешно обновлена и закреплена!</b>\n\n"
            f"⚡ Версия: <code>{version}</code>\n"
            f"📌 Опубликована в канале: <b>@{channel_clean}</b>\n"
            f"🗑 Предыдущий пост с Дельтой автоматически удалён."
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error publishing Delta APK: {e}")
        await status_msg.edit_text(
            f"❌ <b>Ошибка при публикации APK в канал:</b>\n<code>{e}</code>\n\n"
            "Убедитесь, что бот является администратором канала с правами на публикацию и закрепление сообщений."
        )


# --- CHANNEL HEADER (PINNED NAVIGATION POST) ---

def build_channel_header_text(bot_username: str) -> str:
    return (
        "⚡ <b>ДОБРО ПОЖАЛОВАТЬ В SCRIPT DROP!</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 <i>Самый проверенный и безопасный источник скриптов для Roblox.</i>\n\n"
        "🛡 <b>БЕЗ ВИРУСОВ, СТИЛЕРОВ И РЕКЛАМЫ:</b>\n"
        "Все скрипты проверяются администрацией перед публикацией. "
        "Только открытые и чистые loadstring-скрипты.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 <b>КАК ПОЛУЧИТЬ СКРИПТ:</b>\n"
        "1️⃣ Выберите нужную игру в постах канала\n"
        "2️⃣ Нажмите под постом кнопку <b>«🚀 Получить скрипт»</b>\n"
        f"3️⃣ Наш бот @{bot_username} мгновенно выдаст код с кнопкой копирования!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 <b>ЧЕМ ЗАПУСКАТЬ (ИНЖЕКТОРЫ):</b>\n"
        "• <b>Телефон (Android):</b> Delta Executor — свежая версия всегда закреплена выше в канале! Также работают: Codex, Arceus X, Fluxus.\n"
        "• <b>Компьютер (PC):</b> Solara, Wave, Codex PC, Xeno.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔍 <b>ПОИСК СКРИПТОВ ЧЕРЕЗ БОТА:</b>\n"
        f"Напишите нашему боту @{bot_username} название игры (например: <code>Blade Ball</code>, <code>Blox Fruits</code>, <code>Rivals</code>) — он найдёт последний рабочий скрипт!\n\n"
        "📌 <b>ОСНОВНЫЕ ТЕГИ КАНАЛА:</b>\n"
        "#BloxFruits  #BladeBall  #StealAnEgg\n"
        "#Rivals  #MM2  #BedWars  #DaHood\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Бот выдачи:</b> @{bot_username}\n"
        "👑 <b>Владелец:</b> @olarbebe\n\n"
        "⭐ <i>Включите уведомления, чтобы не пропускать обновления скриптов после апдейтов Roblox!</i>"
    )

@dp.callback_query(F.data == "admin_post_header")
async def prompt_post_header(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Опубликовать и закрепить", callback_data="do_post_header")],
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="open_admin_panel")],
        ]
    )
    await call.message.answer(
        "📌 <b>Публикация официальной шапки в канал</b>\n\n"
        "Бот отправит оформленный пост-навигацию со всеми правилами, ссылками на бот/Mini App и инструкциями, и закрепит его в канале.\n\n"
        "Опубликовать сейчас?",
        reply_markup=kb,
    )
    await call.answer()

@dp.callback_query(F.data == "do_post_header")
async def execute_post_header(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    if not channel:
        await call.answer("⚠️ Канал ещё не привязан!", show_alert=True)
        return

    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    channel_clean = channel.replace("@", "")
    header_text = build_channel_header_text(bot_user)

    header_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Открыть бота со скриптами ↗", url=f"https://t.me/{bot_user}")],
            [InlineKeyboardButton(text="📱 Каталог скриптов в боте ↗", url=f"https://t.me/{bot_user}")],
        ]
    )

    try:
        if config.BANNER_PATH.exists():
            photo = FSInputFile(config.BANNER_PATH)
            sent = await bot.send_photo(chat_id=channel, photo=photo, caption=header_text, reply_markup=header_kb)
        else:
            sent = await bot.send_message(chat_id=channel, text=header_text, reply_markup=header_kb)

        try:
            await bot.pin_chat_message(chat_id=channel, message_id=sent.message_id, disable_notification=False)
        except Exception as e:
            logger.warning(f"Could not pin header: {e}")

        await database.set_setting("last_header_message_id", str(sent.message_id))
        await call.message.answer(f"🎉 <b>Шапка канала успешно опубликована и закреплена в @{channel_clean}!</b>")
        await call.answer("✅ Готово!")
    except Exception as e:
        logger.error(f"Error posting header: {e}")
        await call.message.answer(f"❌ <b>Ошибка при публикации шапки:</b>\n<code>{e}</code>")
        await call.answer("Ошибка")



# --- ADMIN SCRIPT SEARCH (PULSEHUB & SCRIPTBLOX SAFE FINDER) ---

_SEARCH_CACHE = {}

@dp.callback_query(F.data == "admin_search_scripts")
async def start_admin_search_scripts(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    await state.set_state(AdminScriptSearch.waiting_for_game_query)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")]])

    await call.message.answer(
        "🔍 <b>Поиск скриптов по открытым базам (PulseHub & ScriptBlox)</b>\n\n"
        "Напишите название игры на английском или русском (например: <code>mm2</code>, <code>steal an egg</code>, <code>rivals</code>, <code>blade ball</code>, <code>blox fruits</code>):\n\n"
        "🛡 <i>Все найденные скрипты автоматически проверяются на безопасность (блокируются вебхуки, стилеры и RAT).</i>",
        reply_markup=cancel_kb,
    )
    await call.answer()

@dp.message(AdminScriptSearch.waiting_for_game_query)
async def process_admin_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("⚠️ Пожалуйста, введите название текстом.")
        return

    status_msg = await message.answer(f"⏳ <b>Ищу проверенные скрипты для «{query}» в PulseHub и ScriptBlox...</b>")
    
    results = await script_finder.search_scripts_online(query)
    try:
        await status_msg.delete()
    except Exception:
        pass

    if not results:
        cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Попробовать другой запрос", callback_data="admin_search_scripts")],
            [InlineKeyboardButton(text="👑 В меню админа", callback_data="open_admin_panel")],
        ])
        await message.answer(
            f"❌ <b>По запросу «{query}» безопасных скриптов не найдено.</b>\n\n"
            "Попробуйте написать другое название или добавьте скрипт вручную через «➕ Создать пост со скриптом».",
            reply_markup=cancel_kb,
        )
        await state.clear()
        return

    user_id = message.from_user.id
    _SEARCH_CACHE[user_id] = results
    await state.clear()

    await message.answer(f"🎉 <b>Найдено рабочих скриптов: {len(results)}</b>\nВыберите действие под любым из них:")

    import html as html_lib
    for idx, item in enumerate(results[:4]):
        preview_code = item['script_code']
        if len(preview_code) > 120:
            preview_display = preview_code[:115] + "..."
        else:
            preview_display = preview_code

        card_text = (
            f"🎮 <b>Игра:</b> {item['game_name']}\n"
            f"📝 <b>Скрипт:</b> {item['title']}\n"
            f"🌐 <b>Источник:</b> {item['source']}\n"
            f"🛡 <b>Безопасность:</b> 🟢 <i>{item['safety_note']}</i>\n\n"
            f"🛠 <b>Функционал (ИИ анализ):</b>\n"
            f"{item['features']}\n\n"
            f"📜 <b>Код:</b>\n<code>{html_lib.escape(preview_display)}</code>"
        )

        card_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📢 Опубликовать в канал в 1 клик", callback_data=f"pub_found:{idx}")],
                [InlineKeyboardButton(text="💾 Только сохранить в базу", callback_data=f"save_found:{idx}")],
            ]
        )
        await message.answer(card_text, reply_markup=card_kb)


@dp.callback_query(F.data.startswith("pub_found:"))
async def callback_publish_found(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    idx = int(call.data.split(":")[1])
    user_id = call.from_user.id
    cached_list = _SEARCH_CACHE.get(user_id, [])

    if idx >= len(cached_list):
        await call.answer("⚠️ Срок действия поиска истёк. Повторите поиск.", show_alert=True)
        return

    item = cached_list[idx]
    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    if not channel:
        await call.answer("⚠️ Канал ещё не привязан!", show_alert=True)
        return

    # 1. Save to database
    script_key = await database.add_script(
        game_name=item["game_name"],
        features=item["features"],
        script_code=item["script_code"],
        executors=post_builder.DEFAULT_EXECUTORS,
    )

    # 2. Build channel post
    post_text = post_builder.build_channel_post(
        game_name=item["game_name"],
        features=item["features"],
        executors=post_builder.DEFAULT_EXECUTORS,
    )
    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    deep_link = f"https://t.me/{bot_user}?start={script_key}"

    post_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Получить скрипт", url=deep_link)]
        ]
    )

    # 3. Publish to channel
    try:
        if config.BANNER_PATH.exists():
            photo = FSInputFile(config.BANNER_PATH)
            sent = await bot.send_photo(chat_id=channel, photo=photo, caption=post_text, reply_markup=post_kb)
        else:
            sent = await bot.send_message(chat_id=channel, text=post_text, reply_markup=post_kb)

        await database.update_script_channel_post(script_key, sent.message_id)
        channel_clean = channel.replace("@", "")
        post_url = f"https://t.me/{channel_clean}/{sent.message_id}"

        confirm_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Посмотреть пост в канале", url=post_url)],
                [InlineKeyboardButton(text="👑 В меню админа", callback_data="open_admin_panel")],
            ]
        )
        await call.message.answer(
            f"🎉 <b>Скрипт «{item['game_name']}» успешно опубликован в @{channel_clean}!</b>\n\n"
            f"Ключ: <code>{script_key}</code>\n"
            f"Ссылка на пост: <a href=\"{post_url}\">{post_url}</a>",
            reply_markup=confirm_kb,
            disable_web_page_preview=True,
        )
        await call.answer("✅ Опубликовано!")
    except Exception as e:
        logger.error(f"Error publishing found script: {e}")
        await call.message.answer(f"❌ Ошибка публикации: {e}")
        await call.answer("Ошибка")


@dp.callback_query(F.data.startswith("save_found:"))
async def callback_save_found(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    idx = int(call.data.split(":")[1])
    user_id = call.from_user.id
    cached_list = _SEARCH_CACHE.get(user_id, [])

    if idx >= len(cached_list):
        await call.answer("⚠️ Срок действия поиска истёк. Повторите поиск.", show_alert=True)
        return

    item = cached_list[idx]
    script_key = await database.add_script(
        game_name=item["game_name"],
        features=item["features"],
        script_code=item["script_code"],
        executors=post_builder.DEFAULT_EXECUTORS,
    )

    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    deep_link = f"https://t.me/{bot_user}?start={script_key}"

    await call.message.answer(
        f"✅ <b>Скрипт «{item['game_name']}» сохранён в базе!</b>\n\n"
        f"Ключ: <code>{script_key}</code>\n"
        f"Ссылка для выдачи: {deep_link}"
    )
    await call.answer("Сохранено!")


# --- CHANGELOG PUBLISHER ---

@dp.callback_query(F.data == "admin_post_changelog")
async def prompt_post_changelog(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    changelog_text = post_builder.build_changelog_post_text(bot_user)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Опубликовать и закрепить в канале", callback_data="do_post_changelog")],
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="open_admin_panel")],
        ]
    )

    preview_banner = getattr(config, "BANNER_UPDATE", None)
    banner_to_use = preview_banner if (preview_banner and preview_banner.exists()) else config.BANNER_PATH

    if banner_to_use.exists():
        photo = FSInputFile(banner_to_use)
        await call.message.answer_photo(
            photo=photo,
            caption=f"📢 <b>Предпросмотр поста с обновлением:</b>\n\n{changelog_text}",
            reply_markup=kb,
        )
    else:
        await call.message.answer(
            f"📢 <b>Предпросмотр поста с обновлением:</b>\n\n{changelog_text}",
            reply_markup=kb,
        )
    await call.answer()


@dp.callback_query(F.data == "do_post_changelog")
async def execute_post_changelog(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    if not channel:
        await call.answer("⚠️ Канал ещё не привязан!", show_alert=True)
        return

    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME
    channel_clean = channel.replace("@", "")
    changelog_text = post_builder.build_changelog_post_text(bot_user)

    changelog_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Открыть бота со скриптами ↗", url=f"https://t.me/{bot_user}")],
            [InlineKeyboardButton(text="📱 Открыть Mini App каталог ↗", url=f"https://t.me/{bot_user}")],
        ]
    )

    update_banner = getattr(config, "BANNER_UPDATE", None)
    banner_to_use = update_banner if (update_banner and update_banner.exists()) else config.BANNER_PATH

    try:
        if banner_to_use.exists():
            photo = FSInputFile(banner_to_use)
            sent = await bot.send_photo(chat_id=channel, photo=photo, caption=changelog_text, reply_markup=changelog_kb)
        else:
            sent = await bot.send_message(chat_id=channel, text=changelog_text, reply_markup=changelog_kb)

        try:
            await bot.pin_chat_message(chat_id=channel, message_id=sent.message_id, disable_notification=False)
        except Exception as e:
            logger.warning(f"Could not pin changelog: {e}")

        await database.set_setting("last_changelog_message_id", str(sent.message_id))
        await call.message.answer(f"🎉 <b>Changelog 2.0 успешно опубликован и закреплен в @{channel_clean}!</b>")
        await call.answer("✅ Готово!")
    except Exception as e:
        logger.error(f"Error posting changelog: {e}")
        await call.message.answer(f"❌ <b>Ошибка при публикации Changelog:</b>\n<code>{e}</code>")
        await call.answer("Ошибка")


# --- USER SEARCH HANDLER ---


@dp.message(F.text)
async def handle_user_search(message: Message, state: FSMContext):
    # Ignore if in an FSM state or command
    if await state.get_state():
        return
    text = message.text.strip()
    if text.startswith("/"):
        return

    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    channel_clean = channel.replace("@", "") if channel else "script_drop"
    bot_info = await bot.get_me()
    bot_user = bot_info.username or config.BOT_USERNAME

    results = await database.search_scripts(text, limit=5)
    if not results:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📢 Искать в канале @script_drop", url=f"https://t.me/{channel_clean}")],
                [InlineKeyboardButton(text="📱 Открыть каталог", web_app=WebAppInfo(url=get_webapp_url()))],
            ]
        )
        await message.answer(
            f"🔍 По запросу «<b>{text}</b>» скриптов пока нет.\n\n"
            f"Попробуйте написать название игры на английском (например: <code>Blox Fruits</code>, <code>Blade Ball</code>, <code>Steal an Egg</code>) или посмотрите свежие релизы в нашем канале! 👇",
            reply_markup=kb,
        )
        return

    # Take the latest matching script
    latest = results[0]
    game_name = latest["game_name"]
    script_key = latest["script_key"]
    features = latest.get("features", "")
    executors = latest.get("executors", post_builder.DEFAULT_EXECUTORS)
    channel_msg_id = latest.get("channel_message_id")

    msg_text = (
        f"🔍 <b>Найден скрипт для игры: {game_name}</b> ⚡\n\n"
        f"🛠 <b>Функционал последнего релиза:</b>\n"
        f"{features}\n\n"
        f"📱 <b>Поддержка:</b> {executors}\n"
        f"📌 <b>Статус:</b> 🟢 <i>Работает / Undetected</i>\n\n"
        f"👇 <b>Выберите действие:</b>"
    )

    kb_buttons = []
    if channel_msg_id:
        post_url = f"https://t.me/{channel_clean}/{channel_msg_id}"
        kb_buttons.append([InlineKeyboardButton(text="🚀 Перейти к посту в канале ↗", url=post_url)])

    deep_link = f"https://t.me/{bot_user}?start={script_key}"
    kb_buttons.append([InlineKeyboardButton(text="⚡ Получить скрипт в боте", url=deep_link)])

    if not channel_msg_id:
        kb_buttons.append([InlineKeyboardButton(text="📢 Наш канал со скриптами ↗", url=f"https://t.me/{channel_clean}")])

    await message.answer(msg_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))

# --- DAILY INTERACTIVE POLL (12:00 GMT+5) ---

async def publish_daily_poll(force: bool = False) -> bool:
    """Publishes the daily interactive poll to the channel so subscribers can vote without comments."""
    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    if not channel:
        logger.warning("Daily poll skipped: channel is not set.")
        return False

    today_str = datetime.now(TZ_GMT5).strftime("%Y-%m-%d")
    last_poll_date = await database.get_setting("last_daily_poll_date")
    if not force and last_poll_date == today_str:
        logger.info("Daily poll already published today.")
        return False

    question, options = post_builder.get_daily_poll_data()

    try:
        sent_poll = await bot.send_poll(
            chat_id=channel,
            question=question,
            options=options,
            is_anonymous=True,
            allows_multiple_answers=False,
        )
        await database.set_setting("last_daily_poll_date", today_str)
        logger.info(f"Daily poll published to {channel} for {today_str} (msg_id={sent_poll.message_id}).")
        return True
    except Exception as e:
        logger.error(f"Failed to publish daily poll: {e}")
        return False

async def daily_autopost_scheduler():
    """Background loop that publishes daily interactive poll at 12:00 GMT+5."""
    logger.info("Daily autopost poll scheduler (12:00 GMT+5) started.")
    while True:
        try:
            now_gmt5 = datetime.now(TZ_GMT5)
            target = now_gmt5.replace(hour=12, minute=0, second=0, microsecond=0)
            if now_gmt5 >= target:
                target += timedelta(days=1)
                
            wait_seconds = (target - now_gmt5).total_seconds()
            logger.info(f"Next daily poll scheduled for {target.strftime('%Y-%m-%d %H:%M:%S')} GMT+5 (in {int(wait_seconds)}s)")
            
            await asyncio.sleep(wait_seconds)

            enabled = await database.get_setting("daily_autopost_enabled", "true")
            if enabled.lower() == "true":
                await publish_daily_poll(force=False)
                
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Daily autopost scheduler stopped.")
            break
        except Exception as e:
            logger.error(f"Error in daily_autopost_scheduler: {e}")
            await asyncio.sleep(30)

@dp.callback_query(F.data == "admin_autopost_menu")
async def callback_admin_autopost(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    enabled = await database.get_setting("daily_autopost_enabled", "true")
    is_on = enabled.lower() == "true"
    status_emoji = "🟢 Включен" if is_on else "🔴 Выключен"
    toggle_text = "🔴 Выключить авто-опрос" if is_on else "🟢 Включить авто-опрос"

    last_date = await database.get_setting("last_daily_poll_date", "Ещё не было")
    now_str = datetime.now(TZ_GMT5).strftime("%H:%M:%S")

    text = (
        "📊 <b>Ежедневный опрос «На какую игру выложить следующий скрипт?»</b>\n\n"
        f"📌 Статус: <b>{status_emoji}</b>\n"
        f"🕒 Время отправки: <b>каждый день в 12:00 (GMT+5)</b>\n"
        f"📅 Текущее время на сервере: <b>{now_str} (GMT+5)</b>\n"
        f"📝 Последняя отправка: <code>{last_date}</code>\n\n"
        "Бот ежедневно публикует официальный Telegram-опрос прямо в канал, где подписчики могут в один клик проголосовать за любимую игру (комментарии не требуются)!"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Опубликовать опрос в канал сейчас", callback_data="autopost_test_now")],
            [InlineKeyboardButton(text=toggle_text, callback_data="autopost_toggle")],
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="open_admin_panel")],
        ]
    )

    await call.message.answer(text, reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data == "autopost_toggle")
async def callback_autopost_toggle(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    enabled = await database.get_setting("daily_autopost_enabled", "true")
    new_val = "false" if enabled.lower() == "true" else "true"
    await database.set_setting("daily_autopost_enabled", new_val)

    await call.answer("Настройки обновлены!")
    await callback_admin_autopost(call)

@dp.callback_query(F.data == "autopost_test_now")
async def callback_autopost_test_now(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    success = await publish_daily_poll(force=True)
    if success:
        channel = await database.get_setting("channel_id", config.CHANNEL_ID)
        await call.message.answer(f"🎉 <b>Официальный опрос успешно опубликован в канале {channel}!</b>")
        await call.answer("✅ Опрос опубликован!")
    else:
        await call.message.answer("❌ <b>Не удалось отправить опрос.</b> Проверьте, привязан ли канал и есть ли у бота права на публикацию.")
        await call.answer("Ошибка")


# --- WEB SERVER FOR MINI APP API ---

async def webapp_html_handler(request):
    html_file = config.WEBAPP_DIR / "index.html"
    if html_file.exists():
        return web.FileResponse(html_file)
    return web.Response(text="Mini App HTML not found", status=404)

async def api_scripts_handler(request):
    try:
        user_id = int(request.query.get("user_id", 0))
    except (ValueError, TypeError):
        user_id = 0
    # Returns only real scripts received by this user (or real published scripts)
    scripts = await database.get_user_scripts(user_id)
    return web.json_response(scripts)

async def api_check_sub_handler(request):
    try:
        user_id = int(request.query.get("user_id", 0))
    except (ValueError, TypeError):
        user_id = 0
    channel = await database.get_setting("channel_id", config.CHANNEL_ID)
    is_sub = await check_user_subscription(user_id, channel)
    return web.json_response({"subscribed": is_sub})

async def api_top_scripts_handler(request):
    scripts = await database.get_all_scripts(limit=20)
    return web.json_response(scripts)

def create_web_app():
    app = web.Application()
    app.router.add_get("/", webapp_html_handler)
    app.router.add_get("/api/scripts", api_scripts_handler)
    app.router.add_get("/api/top_scripts", api_top_scripts_handler)
    app.router.add_get("/api/check_sub", api_check_sub_handler)
    return app

async def keep_alive_pinger():
    """Periodically pings the external web app URL every 8 minutes so Render never falls asleep."""
    logger.info("Keep-alive self-pinger started (8 min interval).")
    await asyncio.sleep(60)
    url = get_webapp_url()
    while True:
        try:
            if url and "localhost" not in url and "127.0.0.1" not in url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=15) as resp:
                        logger.info(f"Keep-alive ping to {url}: HTTP {resp.status}")
        except Exception as e:
            logger.debug(f"Keep-alive ping notice: {e}")
        await asyncio.sleep(480)

# --- MAIN ---

async def main():
    logger.info("Initializing database...")
    await database.init_db()
    await database.set_setting("primary_admin_id", "5891418490")

    # Start web server for Web App
    port = int(os.getenv("PORT", 7860))
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web App server started on http://0.0.0.0:{port}")

    # Start background scheduler for daily autopost (12:00 GMT+5)
    autopost_task = asyncio.create_task(daily_autopost_scheduler())

    # Start self-pinging keep-alive to keep Render awake 24/7
    keep_alive_task = asyncio.create_task(keep_alive_pinger())

    logger.info("Starting bot polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot)
    finally:
        autopost_task.cancel()
        keep_alive_task.cancel()
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
