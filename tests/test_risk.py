from memehunter.models import Post
from memehunter.risk import market_risk_flags, risk_status


def market_post(**kwargs):
    values = dict(
        post_id="mint", text="Example", author_id="", created_at="2026-11-10T10:00:00Z",
        like_count=0, repost_count=0, reply_count=0, quote_count=0,
        source="dexscreener", liquidity_usd=12_000, volume_24h_usd=80_000,
        market_cap_usd=400_000, buys_24h=120, sells_24h=80,
    )
    values.update(kwargs)
    return Post(**values)


def test_very_low_liquidity_and_sell_pressure_are_high_risk_flags():
    flags = market_risk_flags(market_post(liquidity_usd=400, buys_24h=10, sells_24h=40))
    assert "risk:very_low_liquidity" in flags
    assert "risk:sell_pressure" in flags
    assert risk_status(flags) == "high"


def test_low_liquidity_is_watch_status():
    flags = market_risk_flags(market_post(liquidity_usd=2_000))
    assert "risk:low_liquidity" in flags
    assert risk_status(flags) == "watch"


def test_missing_liquidity_and_valuation_are_unknown_not_safe():
    flags = market_risk_flags(market_post(liquidity_usd=0, market_cap_usd=0))
    assert "risk:unknown_liquidity" in flags
    assert "risk:unknown_valuation_ratio" in flags
    assert risk_status(flags) == "unknown"


def test_social_source_has_no_onchain_safety_assessment():
    post = market_post(source="x")
    flags = market_risk_flags(post)
    assert flags == ("risk:unknown_security_checks",)
