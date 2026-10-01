import aiosqlite
import json
import re
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from config import DB_PATH, SCRIPTS_STORE_PATH

logger = logging.getLogger(__name__)

DEFAULT_EXECUTORS = "ПК и Мобильные (Delta, Arceus X, Fluxus, Codex, Solara)"

def _read_scripts_store() -> Dict[str, Any]:
    """Reads scripts from persistent JSON file."""
    if not SCRIPTS_STORE_PATH.exists():
        return {}
    try:
        with open(SCRIPTS_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading scripts_store.json: {e}")
        return {}

def _write_scripts_store(data: Dict[str, Any]):
    """Persists scripts into JSON file across Render rebuilds."""
    try:
        with open(SCRIPTS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error writing scripts_store.json: {e}")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_key TEXT UNIQUE NOT NULL,
                game_name TEXT NOT NULL,
                features TEXT NOT NULL,
                script_code TEXT NOT NULL,
                executors TEXT DEFAULT 'ПК и Мобильные (Delta, Arceus X, Fluxus, Codex, Solara)',
                image_url TEXT DEFAULT NULL,
                channel_message_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                script_key TEXT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, script_key)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS script_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT,
                game_name TEXT NOT NULL,
                note TEXT DEFAULT '',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if columns exist in older table
        async with db.execute("PRAGMA table_info(scripts)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
            if "executors" not in columns:
                await db.execute(f"ALTER TABLE scripts ADD COLUMN executors TEXT DEFAULT '{DEFAULT_EXECUTORS}'")
            if "channel_message_id" not in columns:
                await db.execute("ALTER TABLE scripts ADD COLUMN channel_message_id INTEGER DEFAULT NULL")
            if "image_url" not in columns:
                await db.execute("ALTER TABLE scripts ADD COLUMN image_url TEXT DEFAULT NULL")
                
        # Synchronize from persistent JSON store into SQLite
        store = _read_scripts_store()
        if store:
            for key, item in store.items():
                s_id = item.get("id")
                s_key = item.get("script_key", key)
                await db.execute("""
                    INSERT OR REPLACE INTO scripts (id, script_key, game_name, features, script_code, executors, image_url, channel_message_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
                """, (
                    s_id,
                    s_key,
                    item.get("game_name", "Roblox"),
                    item.get("features", ""),
                    item.get("script_code", ""),
                    item.get("executors", DEFAULT_EXECUTORS),
                    item.get("image_url"),
                    item.get("channel_message_id"),
                    item.get("created_at")
                ))

        await db.commit()

async def update_script_channel_post(script_key: str, message_id: int):
    """Saves the channel message ID of the published post."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE scripts SET channel_message_id = ? WHERE script_key = ?",
            (message_id, script_key)
        )
        await db.commit()

    # Also update store
    store = _read_scripts_store()
    if script_key in store:
        store[script_key]["channel_message_id"] = message_id
        _write_scripts_store(store)

async def search_scripts(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Searches scripts by game name or features, handling Russian aliases."""
    raw = query.strip().lower()
    
    synonyms = {
        "блокс": "blox",
        "фрут": "fruit",
        "блейд": "blade",
        "бол": "ball",
        "стил": "steal",
        "яйц": "egg",
        "райвал": "rivals",
        "ривал": "rivals",
        "мардер": "murder",
        "мм2": "murder",
        "mm2": "murder",
        "bf": "blox fruits",
        "bb": "blade ball",
        "пульс": "pulse",
        "pulse": "pulse",
        "лоадер": "pulse",
        "loader": "pulse",
        "бедварс": "bedwars",
        "дахуд": "hood",
        "дорс": "doors",
        "брукхейвен": "brookhaven",
        "форсакен": "forsaken",
        "фиш": "fisch",
        "ночей": "nights",
        "ночи": "nights",
        "лес": "forest",
        "99": "99",
    }
    
    normalized = raw
    for ru, en in synonyms.items():
        if ru in normalized:
            normalized = normalized.replace(ru, en)
            
    pattern1 = f"%{raw}%"
    pattern2 = f"%{normalized}%"
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        sql = """
            SELECT * FROM scripts
            WHERE LOWER(game_name) LIKE ? OR LOWER(game_name) LIKE ?
               OR LOWER(features) LIKE ? OR LOWER(features) LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """
        async with db.execute(sql, (pattern1, pattern2, pattern1, pattern2, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def record_user_received(user_id: int, script_key: str):
    """Records that this specific user opened/received this script."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO user_history (user_id, script_key) VALUES (?, ?) ON CONFLICT(user_id, script_key) DO UPDATE SET received_at = CURRENT_TIMESTAMP",
            (user_id, script_key)
        )
        await db.commit()

async def get_user_scripts(user_id: int) -> List[Dict[str, Any]]:
    """Returns ONLY scripts that this specific user actually received."""
    if not user_id or user_id <= 0:
        return []

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT s.* FROM scripts s
            JOIN user_history h ON s.script_key = h.script_key
            WHERE h.user_id = ?
            ORDER BY h.received_at DESC
        """
        async with db.execute(query, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def add_script(
    game_name: str,
    features: str,
    script_code: str,
    executors: str = DEFAULT_EXECUTORS,
    image_url: Optional[str] = None,
    custom_key: Optional[str] = None,
) -> str:
    """Adds a script to both SQLite and persistent JSON store with collision prevention."""
    slug = re.sub(r'[^a-z0-9]', '', game_name.lower())
    store = _read_scripts_store()

    if not custom_key:
        max_k = 0
        for k in store.keys():
            if k.startswith("s") and k[1:].isdigit():
                max_k = max(max_k, int(k[1:]))
        script_key = f"s{max_k + 1}"
    else:
        script_key = custom_key
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM scripts WHERE script_key = ?", (script_key,)) as cur:
            row = await cur.fetchone()
            if row:
                script_id = row[0]
                await db.execute(
                    "UPDATE scripts SET game_name = ?, features = ?, script_code = ?, executors = ?, image_url = ? WHERE id = ?",
                    (game_name, features, script_code, executors, image_url, script_id)
                )
            else:
                cursor = await db.execute(
                    "INSERT INTO scripts (script_key, game_name, features, script_code, executors, image_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (script_key, game_name, features, script_code, executors, image_url)
                )
                script_id = cursor.lastrowid
        await db.commit()

    # Also persist to JSON store so it survives any Render reboot
    store[script_key] = {
        "id": script_id,
        "script_key": script_key,
        "slug": slug,
        "game_name": game_name,
        "features": features,
        "script_code": script_code,
        "executors": executors,
        "image_url": image_url,
        "channel_message_id": None,
        "created_at": None,
    }
    _write_scripts_store(store)
    return script_key

async def get_script(script_key: str) -> Optional[Dict[str, Any]]:
    """
    Multi-tier resilient lookup:
    1. Query SQLite by key or ID
    2. Fallback to scripts_store.json by key, ID, or slug
    3. Auto-sync recovered entry into SQLite
    """
    script_key = str(script_key).strip()
    num_id = int(script_key.replace("s", "")) if (script_key.startswith("s") and script_key[1:].isdigit()) else -1
    
    # Tier 1: Check SQLite
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM scripts WHERE script_key = ? OR id = ?",
            (script_key, num_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)

    # Tier 2: Check JSON store
    store = _read_scripts_store()
    match = store.get(script_key)
    
    if not match and num_id > 0:
        for k, v in store.items():
            if v.get("id") == num_id or k == f"s{num_id}":
                match = v
                break
                
    if not match:
        clean_key = re.sub(r'[^a-z0-9]', '', script_key.lower())
        alias_map = {
            "99ночей": "99nightsintheforest",
            "99ночейвлесу": "99nightsintheforest",
            "99ночи": "99nightsintheforest",
            "99nights": "99nightsintheforest",
            "ночей": "99nightsintheforest",
            "мм2": "murdermystery2",
            "мардер": "murdermystery2",
            "блоксфрутс": "bloxfruits",
            "блейдбол": "bladeball",
            "стилэгг": "stealanegg",
            "яйца": "stealanegg",
            "ривалс": "rivals",
            "райвалс": "rivals",
        }
        normalized_target = alias_map.get(script_key.lower().replace(" ", "").replace("_", ""), clean_key)
        for k, v in store.items():
            slug = v.get("slug", "")
            if slug and normalized_target:
                if slug == normalized_target or (len(normalized_target) >= 4 and normalized_target in slug) or (len(slug) >= 4 and slug in normalized_target):
                    match = v
                    break

    # If found in JSON, resurrect into SQLite
    if match:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO scripts (id, script_key, game_name, features, script_code, executors, image_url, channel_message_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
            """, (
                match.get("id"),
                match.get("script_key", script_key),
                match.get("game_name", "Roblox"),
                match.get("features", ""),
                match.get("script_code", ""),
                match.get("executors", DEFAULT_EXECUTORS),
                match.get("image_url"),
                match.get("channel_message_id"),
                match.get("created_at")
            ))
            await db.commit()
        return match

    return None

async def get_all_scripts(limit: int = 50) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM scripts ORDER BY id DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_setting(key: str, default: str = "") -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value))
        )
        await db.commit()


# --- SCRIPT REQUESTS (SUGGESTIONS FROM USERS) ---

async def add_script_request(
    user_id: int,
    username: Optional[str],
    full_name: Optional[str],
    game_name: str,
    note: str = ""
) -> int:
    """Saves a script/game suggestion from a user. Returns the request ID."""
    clean_game = game_name.strip()
    clean_note = note.strip()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO script_requests (user_id, username, full_name, game_name, note, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (user_id, username or "", full_name or "", clean_game, clean_note))
        await db.commit()
        return cursor.lastrowid

async def get_script_requests(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Fetches script requests, optionally filtered by status ('pending', 'published', 'rejected')."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            query = "SELECT * FROM script_requests WHERE status = ? ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (status, limit, offset)
        else:
            query = "SELECT * FROM script_requests ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (limit, offset)
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_script_request(request_id: int) -> Optional[Dict[str, Any]]:
    """Gets a specific script request by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM script_requests WHERE id = ?", (request_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_script_request_status(request_id: int, status: str):
    """Updates request status (e.g. 'published', 'rejected', 'pending')."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE script_requests SET status = ? WHERE id = ?",
            (status, request_id)
        )
        await db.commit()

async def delete_script_request(request_id: int):
    """Deletes a request completely."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM script_requests WHERE id = ?", (request_id,))
        await db.commit()

async def get_script_request_stats() -> Dict[str, Any]:
    """Returns aggregated statistics of user script requests."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Total count
        async with db.execute("SELECT COUNT(*) FROM script_requests") as cur:
            row = await cur.fetchone()
            total = row[0] if row else 0

        # Pending count
        async with db.execute("SELECT COUNT(*) FROM script_requests WHERE status = 'pending'") as cur:
            row = await cur.fetchone()
            pending = row[0] if row else 0

        # Published count
        async with db.execute("SELECT COUNT(*) FROM script_requests WHERE status = 'published'") as cur:
            row = await cur.fetchone()
            published = row[0] if row else 0

        # Unique users count
        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM script_requests") as cur:
            row = await cur.fetchone()
            unique_users = row[0] if row else 0

        # Top requested games
        async with db.execute("""
            SELECT TRIM(game_name) as g_name, COUNT(*) as cnt
            FROM script_requests
            GROUP BY LOWER(TRIM(game_name))
            ORDER BY cnt DESC
            LIMIT 10
        """) as cur:
            rows = await cur.fetchall()
            top_games = [{"game": r["g_name"], "count": r["cnt"]} for r in rows]

        return {
            "total": total,
            "pending": pending,
            "published": published,
            "unique_users": unique_users,
            "top_games": top_games,
        }

