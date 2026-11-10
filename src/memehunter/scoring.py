"""Transparent heuristic scoring; not an investment recommendation."""
from .models import Candidate, Post

KEYWORDS = {
    "launch": ("launch", "launched", "fair launch", "pump.fun", "pumpfun"),
    "meme": ("meme", "memecoin", "meme coin", "ticker"),
    "momentum": ("trending", "viral", "everywhere", "community", "everyone"),
}


def score_post(post: Post) -> Candidate:
    text = post.text.lower()
    engagement = post.like_count + 2 * post.repost_count + post.reply_count + post.quote_count
    score = 0
    reasons: list[str] = []

    for label, words in KEYWORDS.items():
        if any(word in text for word in words):
            score += 12
            reasons.append(f"signal:{label}")

    if engagement >= 1000:
        score += 30
        reasons.append("engagement:very_high")
    elif engagement >= 250:
        score += 22
        reasons.append("engagement:high")
    elif engagement >= 50:
        score += 12
        reasons.append("engagement:moderate")
    elif engagement >= 10:
        score += 5
        reasons.append("engagement:early")

    # Reposts and quotes are weighted more heavily as propagation signals.
    if post.repost_count + post.quote_count >= 20:
        score += 10
        reasons.append("propagation:visible")

    # Keep the score bounded and explicitly explain that it is heuristic.
    return Candidate(post=post, score=min(100, score), reasons=tuple(reasons or ["weak_signal"]))
