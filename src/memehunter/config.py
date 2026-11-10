"""Environment configuration; secrets are read locally and never logged."""
from dataclasses import dataclass
import os

def _load_dotenv_file(path: str = ".env") -> None:
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

@dataclass(frozen=True)
class Settings:
    x_api_bearer_token: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    poll_interval_seconds: int = 180
    min_score: int = 45
    database_path: str = "data/memehunter.sqlite3"
    search_query: str = '(memecoin OR meme coin OR "fair launch") lang:en -is:retweet'
    source_mode: str = "onchain"
    max_tokens_per_cycle: int = 12
    max_daily_launches: int = 5

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv_file()
        return cls(
            x_api_bearer_token=os.getenv("X_API_BEARER_TOKEN", ""),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            poll_interval_seconds=max(120, int(os.getenv("POLL_INTERVAL_SECONDS", "180"))),
            min_score=min(100, max(0, int(os.getenv("MIN_OPPORTUNITY_SCORE", "45")))),
            database_path=os.getenv("DATABASE_PATH", "data/memehunter.sqlite3"),
            search_query=os.getenv("X_SEARCH_QUERY", cls.search_query),
            source_mode=os.getenv("SOURCE_MODE", "onchain").lower(),
            max_tokens_per_cycle=max(1, min(20, int(os.getenv("MAX_TOKENS_PER_CYCLE", "12")))),
            max_daily_launches=max(0, min(5, int(os.getenv("MAX_DAILY_LAUNCHES", "5")))),
        )

    def validate(self) -> None:
        allowed = {"dexscreener", "geckoterminal", "onchain", "x", "both", "all"}
        if self.source_mode not in allowed:
            raise RuntimeError("SOURCE_MODE must be dexscreener, geckoterminal, onchain, x, both, or all")
        if bool(self.telegram_bot_token) != bool(self.telegram_chat_id):
            raise RuntimeError("Set both Telegram variables or leave both empty")
