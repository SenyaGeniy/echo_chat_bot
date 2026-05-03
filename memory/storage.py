import sqlite3
import json
from datetime import datetime
from ..config import DATABASE_PATH, MEMORY_JSON_PATH

class MemoryStorage:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._init_json_store()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entity TEXT NOT NULL,        -- ключевая сущность (Аня, кошки)
                attribute TEXT NOT NULL,      -- атрибут (подруга, аллергия)
                value TEXT NOT NULL,          -- значение (обидчивая, True)
                confidence REAL DEFAULT 0.7,  -- насколько модель уверена
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, entity, attribute)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'bot')),
                content TEXT NOT NULL,
                sentiment TEXT,              -- positive, negative, neutral
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def _init_json_store(self):
        try:
            with open(MEMORY_JSON_PATH, 'r', encoding='utf-8') as f:
                self.graph = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.graph = {"users": {}}
            self._save_graph()

    def _save_graph(self):
        with open(MEMORY_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, ensure_ascii=False, indent=2)

    def add_fact(self, user_id: int, entity: str, attribute: str, value: str, confidence: float = 0.7):
        self.cursor.execute("""
            INSERT INTO facts (user_id, entity, attribute, value, confidence, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, entity, attribute) DO UPDATE SET
                value = excluded.value,
                confidence = excluded.confidence,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, entity, attribute, value, confidence))
        self.conn.commit()

    def get_facts(self, user_id: int, entity: str = None) -> list:
        if entity:
            self.cursor.execute(
                "SELECT entity, attribute, value, confidence FROM facts WHERE user_id = ? AND entity = ?",
                (user_id, entity)
            )
        else:
            self.cursor.execute(
                "SELECT entity, attribute, value, confidence FROM facts WHERE user_id = ?",
                (user_id,)
            )
        return [{"entity": row[0], "attribute": row[1], "value": row[2], "confidence": row[3]}
                for row in self.cursor.fetchall()]

    def add_message(self, user_id: int, role: str, content: str, sentiment: str = None):
        self.cursor.execute(
            "INSERT INTO messages (user_id, role, content, sentiment) VALUES (?, ?, ?, ?)",
            (user_id, role, content, sentiment)
        )
        self.conn.commit()

    def get_last_messages(self, user_id: int, limit: int = 20) -> list:
        self.cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        return [{"role": row[0], "content": row[1], "timestamp": row[2]}
                for row in reversed(self.cursor.fetchall())]

    def close(self):
        self.conn.close()