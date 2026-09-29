import aiosqlite
from typing import Optional, List, Dict, Any
from config import DB_PATH

DEFAULT_EXECUTORS = "ПК и Мобильные (Delta, Arceus X, Fluxus, Codex, Solara)"

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
        
        # Check if executors column exists in older table
        async with db.execute("PRAGMA table_info(scripts)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
            if "executors" not in columns:
                await db.execute(f"ALTER TABLE scripts ADD COLUMN executors TEXT DEFAULT '{DEFAULT_EXECUTORS}'")
                
        await db.commit()

async def record_user_received(user_id: int, script_key: str):
    """Records that this specific user opened/received this script."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO user_history (user_id, script_key) VALUES (?, ?) ON CONFLICT(user_id, script_key) DO UPDATE SET received_at = CURRENT_TIMESTAMP",
            (user_id, script_key)
        )
        await db.commit()

async def get_user_scripts(user_id: int) -> List[Dict[str, Any]]:
    """Returns only scripts that the user actually opened/received."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id and user_id > 0:
            query = """
                SELECT s.* FROM scripts s
                JOIN user_history h ON s.script_key = h.script_key
                WHERE h.user_id = ?
                ORDER BY h.received_at DESC
            """
            async with db.execute(query, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                if rows:
                    return [dict(r) for r in rows]

        # Fallback to all published scripts if user hasn't received any yet
        async with db.execute("SELECT * FROM scripts ORDER BY id DESC LIMIT 50") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def add_script(game_name: str, features: str, script_code: str, executors: str = DEFAULT_EXECUTORS) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO scripts (script_key, game_name, features, script_code, executors) VALUES (?, ?, ?, ?, ?)",
            ("temp", game_name, features, script_code, executors)
        )
        script_id = cursor.lastrowid
        script_key = f"s{script_id}"
        await db.execute(
            "UPDATE scripts SET script_key = ? WHERE id = ?",
            (script_key, script_id)
        )
        await db.commit()
        return script_key

async def get_script(script_key: str) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM scripts WHERE script_key = ? OR id = ?",
            (script_key, script_key.replace("s", "") if script_key.startswith("s") and script_key[1:].isdigit() else -1)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
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
