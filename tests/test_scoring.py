from memehunter.models import Post
from memehunter.scoring import score_post


def test_high_engagement_meme_post_scores_higher_than_weak_post():
    strong = Post("2", "This memecoin launch is going viral", "a", "2026-01-01T00:00:00Z", 800, 300, 100, 50)
    weak = Post("1", "hello world", "b", "2026-01-01T00:00:00Z", 0, 0, 0, 0)
    assert score_post(strong).score > score_post(weak).score
    assert score_post(strong).score <= 100


def test_market_signal_rewards_liquidity_and_activity():
    token = Post(
        "dexscreener:mint", "Example token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="dexscreener", liquidity_usd=12000,
        volume_24h_usd=150000, buys_24h=400, sells_24h=100,
    )
    candidate = score_post(token)
    assert candidate.score == 80
    assert "liquidity:strong" in candidate.reasons
    assert "flow:buys_above_sells" in candidate.reasons


def test_boost_or_profile_without_market_data_is_not_a_strong_signal():
    token = Post(
        "dexscreener:mint", "Promoted token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="dexscreener",
    )
    candidate = score_post(token)
    assert candidate.score == 0
    assert candidate.reasons == ("insufficient_market_signal",)


def test_extreme_market_cap_to_liquidity_ratio_is_penalized():
    token = Post(
        "dexscreener:mint", "Thin liquidity token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="dexscreener", market_cap_usd=2_000_000,
        liquidity_usd=5_000, volume_24h_usd=30_000, buys_24h=80, sells_24h=20,
    )
    candidate = score_post(token)
    assert "risk:high_fdv_to_liquidity" in candidate.reasons
    assert candidate.score < 50
