# -*- coding: utf-8 -*-
"""
SQLite ma'lumotlar bazasi bilan ishlash uchun funksiyalar.
Barcha funksiyalar async (aiosqlite orqali).
"""
import datetime
import aiosqlite

from config import DB_PATH


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def init_db():
    """Bot ishga tushganda jadvallarni yaratish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT,
                photo TEXT,
                age INTEGER,
                gender TEXT,
                region TEXT,
                bio TEXT,
                status TEXT DEFAULT 'none',
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                liker_id INTEGER NOT NULL,
                liked_id INTEGER NOT NULL,
                created_at TEXT,
                UNIQUE(liker_id, liked_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                viewer_id INTEGER NOT NULL,
                viewed_id INTEGER NOT NULL,
                created_at TEXT,
                UNIQUE(viewer_id, viewed_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                text TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_chats (
                user_id INTEGER PRIMARY KEY,
                partner_id INTEGER NOT NULL
            )
        """)
        await db.commit()


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------

async def create_user_if_not_exists(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, status, created_at) VALUES (?, 'none', ?)",
            (telegram_id, now()),
        )
        await db.commit()


async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def save_profile(telegram_id: int, name: str, photo: str, age: int,
                        gender: str, region: str, bio: str, status: str = "pending"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE users SET name=?, photo=?, age=?, gender=?, region=?, bio=?,
               status=?, updated_at=? WHERE telegram_id=?""",
            (name, photo, age, gender, region, bio, status, now(), telegram_id),
        )
        await db.commit()


async def set_status(telegram_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET status=?, updated_at=? WHERE telegram_id=?",
            (status, now(), telegram_id),
        )
        await db.commit()


async def delete_profile(telegram_id: int):
    """Anketani butunlay o'chirish (lekin foydalanuvchi qatori reklama ro'yxati uchun saqlanadi)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE users SET name=NULL, photo=NULL, age=NULL, gender=NULL,
               region=NULL, bio=NULL, status='none', updated_at=? WHERE telegram_id=?""",
            (now(), telegram_id),
        )
        await db.execute("DELETE FROM likes WHERE liker_id=? OR liked_id=?", (telegram_id, telegram_id))
        await db.execute("DELETE FROM views WHERE viewer_id=? OR viewed_id=?", (telegram_id, telegram_id))
        await db.execute(
            "DELETE FROM active_chats WHERE user_id=? OR partner_id=?", (telegram_id, telegram_id)
        )
        await db.commit()


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT telegram_id FROM users")
        rows = await cur.fetchall()
        return [r[0] for r in rows]


async def get_users_for_excel():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT telegram_id, name, age, gender, region, bio, status
               FROM users WHERE name IS NOT NULL ORDER BY created_at DESC"""
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# SEARCH / VIEWS
# ---------------------------------------------------------------------------

async def get_random_profile(viewer_id: int):
    """
    Ko'rilmagan, tasdiqlangan anketalardan birini qaytaradi.
    Eng ko'p layk olganlar ustunlik bilan (lekin teng laykdagilar tasodifiy aralashtiriladi).
    Agar barcha anketalar ko'rilgan bo'lsa - tarixni tozalab, qaytadan boshlanadi.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT u.*, (SELECT COUNT(*) FROM likes WHERE liked_id = u.telegram_id) AS likes_count
            FROM users u
            WHERE u.status = 'approved' AND u.telegram_id != ?
              AND u.telegram_id NOT IN (SELECT viewed_id FROM views WHERE viewer_id = ?)
            ORDER BY likes_count DESC, RANDOM()
            LIMIT 1
        """
        cur = await db.execute(query, (viewer_id, viewer_id))
        row = await cur.fetchone()

        if row is None:
            # Hammasi ko'rilgan - tarixni tozalab qaytadan urinib ko'ramiz
            await db.execute("DELETE FROM views WHERE viewer_id=?", (viewer_id,))
            await db.commit()
            query2 = """
                SELECT u.*, (SELECT COUNT(*) FROM likes WHERE liked_id = u.telegram_id) AS likes_count
                FROM users u
                WHERE u.status = 'approved' AND u.telegram_id != ?
                ORDER BY likes_count DESC, RANDOM()
                LIMIT 1
            """
            cur2 = await db.execute(query2, (viewer_id,))
            row = await cur2.fetchone()

        return dict(row) if row else None


async def mark_viewed(viewer_id: int, viewed_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO views (viewer_id, viewed_id, created_at) VALUES (?, ?, ?)",
            (viewer_id, viewed_id, now()),
        )
        await db.commit()


# ---------------------------------------------------------------------------
# LIKES
# ---------------------------------------------------------------------------

async def add_like(liker_id: int, liked_id: int) -> bool:
    """Layk qo'shadi. Yangi layk bo'lsa True, oldin qo'yilgan bo'lsa False qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT OR IGNORE INTO likes (liker_id, liked_id, created_at) VALUES (?, ?, ?)",
            (liker_id, liked_id, now()),
        )
        await db.commit()
        return cur.rowcount > 0


async def get_likes_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM likes WHERE liked_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_likes_received(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT u.telegram_id, u.name, u.age
               FROM likes l JOIN users u ON u.telegram_id = l.liker_id
               WHERE l.liked_id = ? ORDER BY l.created_at DESC""",
            (user_id,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# MESSAGES / CHAT RELAY
# ---------------------------------------------------------------------------

async def add_message(sender_id: int, receiver_id: int, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (sender_id, receiver_id, text, created_at) VALUES (?, ?, ?, ?)",
            (sender_id, receiver_id, text, now()),
        )
        await db.commit()


async def get_writers(user_id: int):
    """Foydalanuvchiga yozgan insonlar ro'yxati (oxirgi xabar vaqti bo'yicha)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT m.sender_id AS sender_id, u.name AS name, MAX(m.created_at) AS last_at
               FROM messages m JOIN users u ON u.telegram_id = m.sender_id
               WHERE m.receiver_id = ?
               GROUP BY m.sender_id
               ORDER BY last_at DESC""",
            (user_id,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def set_active_chat(user_id: int, partner_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO active_chats (user_id, partner_id) VALUES (?, ?)",
            (user_id, partner_id),
        )
        await db.commit()


async def get_active_chat(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT partner_id FROM active_chats WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else None


async def clear_active_chat(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM active_chats WHERE user_id=?", (user_id,))
        await db.commit()


# ---------------------------------------------------------------------------
# STATISTIKA
# ---------------------------------------------------------------------------

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async def count(query, params=()):
            cur = await db.execute(query, params)
            row = await cur.fetchone()
            return row[0] if row else 0

        total = await count("SELECT COUNT(*) FROM users")
        approved = await count("SELECT COUNT(*) FROM users WHERE status='approved'")
        pending = await count("SELECT COUNT(*) FROM users WHERE status='pending'")
        rejected = await count("SELECT COUNT(*) FROM users WHERE status='rejected'")
        likes = await count("SELECT COUNT(*) FROM likes")
        messages = await count("SELECT COUNT(*) FROM messages")

        return {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
            "likes": likes,
            "messages": messages,
        }
