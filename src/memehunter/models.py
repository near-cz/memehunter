"""Typed models shared by social and on-chain data sources."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Post:
    post_id: str
    text: str
    author_id: str
    created_at: str
    like_count: int
    repost_count: int
    reply_count: int
    quote_count: int
    source: str = "x"
    post_url: str = ""
    token_address: str = ""
    token_symbol: str = ""
    token_name: str = ""
    price_usd: float = 0.0
    liquidity_usd: float = 0.0
    volume_24h_usd: float = 0.0
    market_cap_usd: float = 0.0
    buys_24h: int = 0
    sells_24h: int = 0
    @property
    def url(self) -> str:
        return self.post_url or f"https://x.com/i/web/status/{self.post_id}"
@dataclass(frozen=True)
class Candidate:
    post: Post
    score: int
    reasons: tuple[str, ...]
