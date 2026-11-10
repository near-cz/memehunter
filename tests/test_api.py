from memehunter.api import _market_risk_status


def test_legacy_market_rows_without_risk_flags_are_unknown():
    assert _market_risk_status("", "dexscreener") == "unknown"


def test_social_rows_do_not_claim_onchain_risk_assessment():
    assert _market_risk_status("", "x") == "unknown"


def test_market_row_uses_persisted_risk_flags():
    assert _market_risk_status("liquidity:strong | risk:sell_pressure", "geckoterminal") == "high"
