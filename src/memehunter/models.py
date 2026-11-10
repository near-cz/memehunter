"""Small typed model for public X posts and scored candidates."""
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

    @property
    def url(self) -> str:
        return f"https://x.com/i/web/status/{self.post_id}"


@dataclass(frozen=True)
class Candidate:
    post: Post
    score: int
    reasons: tuple[str, ...]
