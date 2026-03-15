"""
database.py
إدارة قاعدة البيانات (SQLite) - تخزين الإعدادات والقنوات والإحصائيات
"""

import sqlite3
import json
from contextlib import contextmanager
from typing import Optional, Dict, List, Any
from logger import logger
from config import DATABASE_PATH

class Database:
    """فئة التعامل مع قاعدة البيانات"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """مدير سياق للاتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """إنشاء الجداول إذا لم تكن موجودة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # جدول الإعدادات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # جدول القنوات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    chat_id INTEGER PRIMARY KEY,
                    chat_title TEXT,
                    chat_type TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)

            # جدول المستخدمين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP
                )
            """)

            # جدول الإحصائيات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT,
                    channel_id INTEGER,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # جدول المهام المجدولة
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    job_id TEXT PRIMARY KEY,
                    job_data TEXT NOT NULL,
                    next_run_time TIMESTAMP
                )
            """)

            # إدراج الإعدادات الافتراضية إذا لم تكن موجودة
            default_settings = [
                ('publishing_enabled', 'false'),
                ('schedule_hour', str(9)),
                ('schedule_minute', str(0)),
                ('interval_hours', str(3)),
                ('selected_reciter', '1'),
                ('font_style', '1'),
                ('last_verse_index', '0'),
                ('last_surah', '1'),
                ('last_ayah', '1'),
            ]
            for key, value in default_settings:
                cursor.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )

            logger.info("Database initialized successfully")

    # دوال الإعدادات
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """الحصول على إعداد معين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        """تحديث أو إدراج إعداد"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )

    # دوال القنوات
    def add_channel(self, chat_id: int, chat_title: str, chat_type: str, added_by: int):
        """إضافة قناة أو مجموعة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO channels (chat_id, chat_title, chat_type, added_by)
                VALUES (?, ?, ?, ?)
            """, (chat_id, chat_title, chat_type, added_by))

    def remove_channel(self, chat_id: int):
        """إزالة قناة (تعطيل)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE channels SET is_active = 0 WHERE chat_id = ?",
                (chat_id,)
            )

    def get_active_channels(self) -> List[Dict]:
        """الحصول على جميع القنوات النشطة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM channels WHERE is_active = 1 ORDER BY added_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]

    def channel_exists(self, chat_id: int) -> bool:
        """التحقق من وجود قناة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM channels WHERE chat_id = ? AND is_active = 1",
                (chat_id,)
            )
            return cursor.fetchone() is not None

    # دوال المستخدمين
    def update_user(self, user_id: int, first_name: str, username: str = None):
        """تحديث أو إدراج مستخدم"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, first_name, username, last_interaction)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    first_name = excluded.first_name,
                    username = excluded.username,
                    last_interaction = CURRENT_TIMESTAMP
            """, (user_id, first_name, username))

    def get_user_count(self) -> int:
        """عدد المستخدمين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    # دوال الإحصائيات
    def add_stat(self, content_type: str, channel_id: int = None):
        """تسجيل رسالة مرسلة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stats (content_type, channel_id) VALUES (?, ?)",
                (content_type, channel_id)
            )

    def get_stats_summary(self) -> Dict:
        """ملخص الإحصائيات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # إجمالي الرسائل
            cursor.execute("SELECT COUNT(*) FROM stats")
            total = cursor.fetchone()[0]

            # حسب النوع
            cursor.execute("""
                SELECT content_type, COUNT(*) 
                FROM stats 
                GROUP BY content_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}

            # آخر 24 ساعة
            cursor.execute("""
                SELECT COUNT(*) FROM stats 
                WHERE sent_at >= datetime('now', '-1 day')
            """)
            last_day = cursor.fetchone()[0]

            return {
                'total': total,
                'by_type': by_type,
                'last_24h': last_day,
                'users': self.get_user_count(),
                'channels': len(self.get_active_channels())
            }

# إنشاء كائن عام من قاعدة البيانات
db = Database()