"""Environment configuration; secrets are read locally and never logged."""
from dataclasses import dataclass
import os


def _load_dotenv_file(path: str = ".env") -> None:
    # Tiny .env reader to keep the first MVP dependency-light.
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
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
    x_api_bearer_token: str
    telegram_bot_token: str
    telegram_chat_id: str
    poll_interval_seconds: int = 180
    min_score: int = 45
    database_path: str = "data/memehunter.sqlite3"
    search_query: str = '(memecoin OR meme coin OR "fair launch") lang:en -is:retweet'

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv_file()
        return cls(
            x_api_bearer_token=os.getenv("X_API_BEARER_TOKEN", ""),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            poll_interval_seconds=max(60, int(os.getenv("POLL_INTERVAL_SECONDS", "180"))),
            min_score=min(100, max(0, int(os.getenv("MIN_OPPORTUNITY_SCORE", "45")))),
            database_path=os.getenv("DATABASE_PATH", "data/memehunter.sqlite3"),
            search_query=os.getenv("X_SEARCH_QUERY", cls.search_query),
        )

    def validate(self) -> None:
        missing = [name for name, value in (
            ("X_API_BEARER_TOKEN", self.x_api_bearer_token),
            ("TELEGRAM_BOT_TOKEN", self.telegram_bot_token),
            ("TELEGRAM_CHAT_ID", self.telegram_chat_id),
        ) if not value]
        if missing:
            raise RuntimeError("Missing local environment settings: " + ", ".join(missing))
