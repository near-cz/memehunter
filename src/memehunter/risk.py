"""Transparent market-data risk flags. These checks do not establish token safety."""
from .models import Post

ONCHAIN_SOURCES = {"dexscreener", "geckoterminal"}


def market_risk_flags(post: Post) -> tuple[str, ...]:
    if post.source not in ONCHAIN_SOURCES:
        return ("risk:unknown_security_checks",)

    flags: list[str] = []
    trades = post.buys_24h + post.sells_24h

    if post.liquidity_usd <= 0:
        flags.append("risk:unknown_liquidity")
    elif post.liquidity_usd < 1_000:
        flags.append("risk:very_low_liquidity")
    elif post.liquidity_usd < 5_000:
        flags.append("risk:low_liquidity")

    if trades < 10:
        flags.append("risk:very_low_activity")

    if post.sells_24h >= 20 and post.sells_24h >= max(1, post.buys_24h) * 2:
        flags.append("risk:sell_pressure")

    if post.market_cap_usd > 0 and post.liquidity_usd > 0:
        if post.market_cap_usd / post.liquidity_usd > 100:
            flags.append("risk:high_valuation_to_liquidity")
    else:
        flags.append("risk:unknown_valuation_ratio")

    if not flags:
        flags.append("risk:no_obvious_market_flag")

    return tuple(flags)


def risk_status(flags: tuple[str, ...] | list[str]) -> str:
    flags = tuple(flags)
    if any(flag in flags for flag in ("risk:very_low_liquidity", "risk:sell_pressure")):
        return "high"
    if any(flag in flags for flag in ("risk:low_liquidity", "risk:high_valuation_to_liquidity",
                                      "risk:very_low_activity")):
        return "watch"
    if any(flag.startswith("risk:unknown_") for flag in flags):
        return "unknown"
    return "no_obvious_flag"
