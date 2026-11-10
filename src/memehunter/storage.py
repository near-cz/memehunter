"""SQLite persistence for source-neutral opportunities and cursor."""
import sqlite3
from pathlib import Path
class Store:
    def __init__(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS seen_posts (
            post_id TEXT PRIMARY KEY, score INTEGER NOT NULL, created_at TEXT NOT NULL
        )""")
        self.db.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self._migrate()
        self.db.commit()
    def _migrate(self) -> None:
        columns = {row["name"] for row in self.db.execute("PRAGMA table_info(seen_posts)")}
        additions = {
            "text": "TEXT NOT NULL DEFAULT ''", "url": "TEXT NOT NULL DEFAULT ''",
            "like_count": "INTEGER NOT NULL DEFAULT 0", "repost_count": "INTEGER NOT NULL DEFAULT 0",
            "reply_count": "INTEGER NOT NULL DEFAULT 0", "quote_count": "INTEGER NOT NULL DEFAULT 0",
            "reasons": "TEXT NOT NULL DEFAULT ''", "source": "TEXT NOT NULL DEFAULT 'x'",
            "token_address": "TEXT NOT NULL DEFAULT ''", "token_symbol": "TEXT NOT NULL DEFAULT ''",
            "token_name": "TEXT NOT NULL DEFAULT ''", "price_usd": "REAL NOT NULL DEFAULT 0",
            "liquidity_usd": "REAL NOT NULL DEFAULT 0", "volume_24h_usd": "REAL NOT NULL DEFAULT 0",
            "market_cap_usd": "REAL NOT NULL DEFAULT 0", "buys_24h": "INTEGER NOT NULL DEFAULT 0",
            "sells_24h": "INTEGER NOT NULL DEFAULT 0"}
        for name, definition in additions.items():
            if name not in columns:
                self.db.execute(f"ALTER TABLE seen_posts ADD COLUMN {name} {definition}")
    def is_new(self, post_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM seen_posts WHERE post_id = ?", (post_id,)).fetchone() is None
    def mark_seen(self, candidate) -> None:
        post = candidate.post
        self.db.execute(
            """INSERT INTO seen_posts
            (post_id, score, created_at, text, url, like_count, repost_count, reply_count, quote_count,
             reasons, source, token_address, token_symbol, token_name, price_usd, liquidity_usd,
             volume_24h_usd, market_cap_usd, buys_24h, sells_24h)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(post_id) DO UPDATE SET score=excluded.score, created_at=excluded.created_at,
            text=excluded.text, url=excluded.url, like_count=excluded.like_count,
            repost_count=excluded.repost_count, reply_count=excluded.reply_count,
            quote_count=excluded.quote_count, reasons=excluded.reasons, source=excluded.source,
            token_address=excluded.token_address, token_symbol=excluded.token_symbol,
            token_name=excluded.token_name, price_usd=excluded.price_usd,
            liquidity_usd=excluded.liquidity_usd, volume_24h_usd=excluded.volume_24h_usd,
            market_cap_usd=excluded.market_cap_usd, buys_24h=excluded.buys_24h, sells_24h=excluded.sells_24h""",
            (post.post_id, candidate.score, post.created_at, post.text[:2000], post.url,
             post.like_count, post.repost_count, post.reply_count, post.quote_count,
             " | ".join(candidate.reasons)[:1000], post.source, post.token_address,
             post.token_symbol, post.token_name, post.price_usd, post.liquidity_usd,
             post.volume_24h_usd, post.market_cap_usd, post.buys_24h, post.sells_24h))
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
