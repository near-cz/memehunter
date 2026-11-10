"""Transparent heuristic scoring; never an investment recommendation."""
from .models import Candidate, Post
from .risk import market_risk_flags

KEYWORDS = {
    "launch": ("launch", "launched", "fair launch", "pump.fun", "pumpfun"),
    "meme": ("meme", "memecoin", "meme coin", "ticker"),
    "momentum": ("trending", "viral", "everywhere", "community", "everyone"),
}
ONCHAIN_SOURCES = {"dexscreener", "geckoterminal"}

def score_post(post: Post) -> Candidate:
    if post.source in ONCHAIN_SOURCES:
        return score_market_signal(post)
    text = post.text.lower()
    engagement = post.like_count + 2 * post.repost_count + post.reply_count + post.quote_count
    score, reasons = 0, []
    for label, words in KEYWORDS.items():
        if any(word in text for word in words):
            score += 12
            reasons.append(f"signal:{label}")
    if engagement >= 1000:
        score += 30; reasons.append("engagement:very_high")
    elif engagement >= 250:
        score += 22; reasons.append("engagement:high")
    elif engagement >= 50:
        score += 12; reasons.append("engagement:moderate")
    elif engagement >= 10:
        score += 5; reasons.append("engagement:early")
    if post.repost_count + post.quote_count >= 20:
        score += 10; reasons.append("propagation:visible")
    return Candidate(post, min(100, score), tuple(reasons or ["weak_signal"]))

def score_market_signal(post: Post) -> Candidate:
    score, reasons = 0, []
    liquidity, volume = post.liquidity_usd, post.volume_24h_usd
    trades = post.buys_24h + post.sells_24h
    if liquidity >= 10000:
        score += 25; reasons.append("liquidity:strong")
    elif liquidity >= 2000:
        score += 15; reasons.append("liquidity:moderate")
    elif liquidity >= 500:
        score += 5; reasons.append("liquidity:early")
    if volume >= 100000:
        score += 25; reasons.append("volume:high")
    elif volume >= 20000:
        score += 15; reasons.append("volume:moderate")
    elif volume >= 2000:
        score += 5; reasons.append("volume:early")
    if trades >= 500:
        score += 20; reasons.append("activity:high")
    elif trades >= 100:
        score += 12; reasons.append("activity:moderate")
    elif trades >= 20:
        score += 5; reasons.append("activity:early")
    if post.buys_24h > post.sells_24h and trades >= 20:
        score += 10; reasons.append("flow:buys_above_sells")
    if not reasons:
        reasons.append("insufficient_market_signal")
    flags = market_risk_flags(post)
    if "risk:high_valuation_to_liquidity" in flags:
        score -= 10
    if "risk:very_low_liquidity" in flags:
        score -= 15
    elif "risk:low_liquidity" in flags:
        score -= 8
    if "risk:sell_pressure" in flags:
        score -= 12
    reasons.extend(flags)
    return Candidate(post, max(0, min(100, score)), tuple(reasons or ["insufficient_market_signal"]))
