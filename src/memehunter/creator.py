"""Safe draft generation for candidate memecoin launches; no wallet or transaction logic."""
import re
from .models import Candidate

STOP_WORDS = {
    "about", "after", "again", "also", "been", "being", "could", "from", "have",
    "here", "just", "like", "make", "more", "most", "much", "only", "over",
    "really", "should", "some", "than", "that", "their", "there", "these",
    "they", "this", "those", "through", "very", "want", "what", "when",
    "where", "which", "while", "with", "would", "your", "will", "into",
    "pump", "fun", "coin", "meme", "memecoin", "token", "launch", "viral",
    "trending", "twitter", "tweet", "post", "https", "http", "com",
}


def _concept_words(text: str) -> list[str]:
    hashtags = re.findall(r"(?<!\w)#([A-Za-z][A-Za-z0-9]{1,23})", text)
    words = hashtags or re.findall(r"\b[A-Za-z][A-Za-z0-9]{2,17}\b", text)
    result = []
    for word in words:
        lowered = word.lower()
        if lowered not in STOP_WORDS and lowered not in {item.lower() for item in result}:
            result.append(word)
        if len(result) == 3:
            break
    return result


def build_creator_draft(candidate: Candidate) -> dict:
    post = candidate.post
    words = _concept_words(post.text)
    if not words:
        words = ["Trend"]
    name = " ".join(word.capitalize() for word in words[:2])[:32]
    symbol_seed = "".join(words).upper()
    symbol = re.sub(r"[^A-Z0-9]", "", symbol_seed)[:6] or "TREND"
    return {
        "source_post_id": post.post_id,
        "source_url": post.url,
        "source_text": post.text[:1000],
        "name": name,
        "symbol": symbol,
        "description": (
            f"A community meme concept inspired by a public trend. "
            f"Review originality, rights and metadata before any publication. "
            f"Source: {post.url}"
        ),
        "score": candidate.score,
        "reasons": list(candidate.reasons),
        "image_status": "needs_artwork",
        "status": "pending_review",
        "launch_enabled": False,
        "initial_buy_sol": 0,
    }
