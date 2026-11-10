# MemeHunter

MemeHunter is a read-only Solana memecoin discovery dashboard with optional Telegram alerts.

## Current MVP

- **Default source: DexScreener public API**, no X account, API key, or paid X plan required.
- Latest public Solana token profiles and boosts are combined and enriched with public pair data.
- Explainable heuristic score based on liquidity, 24h volume, transaction activity, buy/sell balance and a simple FDV/liquidity risk flag.
- Optional X API v2 adapter; X is not required in the default configuration.
- Optional Telegram alerts; the scanner and dashboard can run without a Telegram bot.
- SQLite persistence and deduplication; local read-only FastAPI API and dashboard.
- No wallet connection, transaction signing, token creation, or automatic trading.

## Data-source limitations

DexScreener's public endpoints expose profiles, boosts and pair/market data. They do **not** provide a complete feed of every new token, social post, or pump.fun launch. A boost/profile is not proof of organic demand. The score is a heuristic signal, not investment advice. Public API limits and availability may change; requests are deliberately bounded.

Official reference: https://docs.dexscreener.com/api/reference

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env
```

No credentials are required for the default DexScreener scanner. Edit `.env` only if you want optional Telegram or X integration. Never commit or share API keys, Telegram tokens, seed phrases or private keys.

## Run locally

Terminal 1 — scanner:

```bash
memehunter
```

Terminal 2 — read-only API:

```bash
memehunter-api
```

Terminal 3 — dashboard static server:

```bash
python -m http.server 8080 --directory apps/dashboard
```

Open http://127.0.0.1:8080. API health: http://127.0.0.1:8000/api/v1/health. API docs: http://127.0.0.1:8000/api/docs.

## Optional sources

- `SOURCE_MODE=dexscreener` (default): free public market-data adapter.
- `SOURCE_MODE=x`: requires a valid local `X_API_BEARER_TOKEN`.
- `SOURCE_MODE=both`: combines both adapters.
- Telegram alerts activate only when both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set.

## Safety

Read-only mode only. No wallet or private key is accepted. No token launch or automated trading is implemented. Never assume a token launch is free or that Creator Fees, liquidity, volume or profit are guaranteed. Review token contracts and liquidity independently before making any decision.
