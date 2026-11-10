from memehunter.models import Post
from memehunter.scoring import score_post
from memehunter.sources.geckoterminal import GeckoTerminalClient


def test_high_engagement_meme_post_scores_higher_than_weak_post():
    strong = Post("2", "This memecoin launch is going viral", "a", "2026-01-01T00:00:00Z", 800, 300, 100, 50)
    weak = Post("1", "hello world", "b", "2026-01-01T00:00:00Z", 0, 0, 0, 0)
    assert score_post(strong).score > score_post(weak).score
    assert score_post(strong).score <= 100


def test_market_signal_rewards_liquidity_and_activity():
    token = Post("dexscreener:mint", "Example token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="dexscreener", liquidity_usd=12000,
        volume_24h_usd=150000, buys_24h=400, sells_24h=100)
    candidate = score_post(token)
    assert candidate.score == 80
    assert "liquidity:strong" in candidate.reasons
    assert "flow:buys_above_sells" in candidate.reasons


def test_geckoterminal_pool_parsing_uses_included_token_metadata():
    payload = {
        "data": [{
            "id": "solana_pool123", "type": "pool",
            "attributes": {
                "address": "pool123", "name": "MEME / SOL",
                "pool_created_at": "2026-11-10T10:00:00Z",
                "base_token_price_usd": "0.0001", "market_cap_usd": "500000",
                "reserve_in_usd": "12000",
                "volume_usd": {"h24": "80000"},
                "transactions": {"h24": {"buys": 350, "sells": 120}},
            },
            "relationships": {
                "base_token": {"data": {"id": "solana_meme", "type": "token"}},
                "quote_token": {"data": {"id": "solana_sol", "type": "token"}},
                "dex": {"data": {"id": "raydium", "type": "dex"}},
            },
        }],
        "included": [
            {"id": "solana_meme", "type": "token", "attributes": {
                "address": "mint123", "name": "Meme", "symbol": "MEME"}},
            {"id": "solana_sol", "type": "token", "attributes": {
                "address": "So11111111111111111111111111111111111111112",
                "name": "Wrapped SOL", "symbol": "SOL"}},
        ],
    }
    posts = GeckoTerminalClient._parse_pool_response(payload, 10)
    assert len(posts) == 1
    post = posts[0]
    assert post.source == "geckoterminal"
    assert post.token_address == "mint123"
    assert post.token_symbol == "MEME"
    assert post.liquidity_usd == 12000
    assert post.volume_24h_usd == 80000
    assert post.buys_24h == 350 and post.sells_24h == 120
    assert post.url.endswith("/pool123")


def test_geckoterminal_market_signals_are_scored():
    token = Post("geckoterminal:pool", "Example token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="geckoterminal", liquidity_usd=12000,
        volume_24h_usd=80000, buys_24h=350, sells_24h=120)
    candidate = score_post(token)
    assert candidate.score >= 45
    assert "liquidity:strong" in candidate.reasons


def test_profile_without_market_data_is_not_a_strong_signal():
    token = Post("dexscreener:mint", "Promoted token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="dexscreener")
    candidate = score_post(token)
    assert candidate.score == 0
    assert "insufficient_market_signal" in candidate.reasons


def test_extreme_market_cap_to_liquidity_ratio_is_penalized():
    token = Post("dexscreener:mint", "Thin liquidity token", "", "2026-01-01T00:00:00Z",
        0, 0, 0, 0, source="dexscreener", market_cap_usd=2_000_000,
        liquidity_usd=5_000, volume_24h_usd=30_000, buys_24h=80, sells_24h=20)
    candidate = score_post(token)
    assert "risk:high_valuation_to_liquidity" in candidate.reasons
    assert candidate.score < 50


def test_geckoterminal_selects_non_quote_token_when_base_is_sol():
    payload = {
        "data": [{
            "id": "solana_pool456", "type": "pool",
            "attributes": {"address": "pool456", "name": "SOL / MEME",
                "base_token_price_usd": "150", "quote_token_price_usd": "0.0002",
                "reserve_in_usd": "9000", "volume_usd": {"h24": "40000"},
                "transactions": {"h24": {"buys": 120, "sells": 40}}},
            "relationships": {
                "base_token": {"data": {"id": "solana_sol", "type": "token"}},
                "quote_token": {"data": {"id": "solana_meme", "type": "token"}},
            },
        }],
        "included": [
            {"id": "solana_sol", "type": "token", "attributes": {
                "address": "So11111111111111111111111111111111111111112",
                "name": "Wrapped SOL", "symbol": "SOL"}},
            {"id": "solana_meme", "type": "token", "attributes": {
                "address": "mint456", "name": "Meme Coin", "symbol": "MEME"}},
        ],
    }
    post = GeckoTerminalClient._parse_pool_response(payload, 10)[0]
    assert post.token_address == "mint456"
    assert post.token_symbol == "MEME"
    assert post.price_usd == 0.0002


def test_geckoterminal_skips_pool_when_token_mint_metadata_is_missing():
    payload = {
        "data": [{
            "id": "solana_pool789", "type": "pool",
            "attributes": {"address": "pool789", "name": "Unknown / SOL"},
            "relationships": {
                "base_token": {"data": {"id": "solana_unknown", "type": "token"}},
                "quote_token": {"data": {"id": "solana_sol", "type": "token"}},
            },
        }],
        "included": [],
    }
    assert GeckoTerminalClient._parse_pool_response(payload, 10) == []


def test_telegram_market_alert_includes_geckoterminal_token_link_and_mint():
    from memehunter.models import Candidate
    from memehunter.telegram import TelegramNotifier

    post = Post("geckoterminal:pool123", "Meme <script> ($MEME)", "", "2026-11-10T10:00:00Z",
        0, 0, 0, 0, source="geckoterminal",
        post_url="https://www.geckoterminal.com/solana/pools/pool123",
        token_address="MintABC123", token_symbol="MEME", token_name="Meme <script>",
        liquidity_usd=12000, volume_24h_usd=80000, buys_24h=350, sells_24h=120)
    message = TelegramNotifier.format_candidate(Candidate(post, 72, ("liquidity:strong",)))
    assert "Voir le token / pool" in message
    assert "https://www.geckoterminal.com/solana/pools/pool123" in message
    assert "<code>MintABC123</code>" in message
    assert "&lt;script&gt;" in message
    assert "<script>" not in message
    assert "DONNÉES INSUFFISANTES" in message
    assert "pas de vérification honeypot" in message


def test_telegram_alert_does_not_link_untrusted_url():
    from memehunter.models import Candidate
    from memehunter.telegram import TelegramNotifier

    post = Post("x1", "Hello", "", "2026-11-10T10:00:00Z", 1, 0, 0, 0,
        post_url='javascript:alert("x")')
    message = TelegramNotifier.format_candidate(Candidate(post, 50, ()))
    assert 'href="javascript:' not in message
    assert "Voir le post source" in message
