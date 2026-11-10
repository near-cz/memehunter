"""Minimal SQLite persistence for deduplication and polling cursor."""
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS seen_posts (post_id TEXT PRIMARY KEY, score INTEGER NOT NULL, created_at TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.db.commit()

    def is_new(self, post_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM seen_posts WHERE post_id = ?", (post_id,)).fetchone() is None

    def mark_seen(self, post_id: str, score: int, created_at: str) -> None:
        self.db.execute("INSERT OR IGNORE INTO seen_posts(post_id, score, created_at) VALUES (?, ?, ?)", (post_id, score, created_at))
        self.db.commit()

    def get_cursor(self) -> str | None:
        row = self.db.execute("SELECT value FROM app_state WHERE key = 'x_since_id'").fetchone()
        return row[0] if row else None

    def set_cursor(self, value: str | None) -> None:
        if value:
            self.db.execute("INSERT INTO app_state(key, value) VALUES ('x_since_id', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (value,))
            self.db.commit()

    def close(self) -> None:
        self.db.close()
