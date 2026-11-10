# MemeHunter

MemeHunter is a read-only Solana memecoin discovery dashboard with optional Telegram alerts.

## Current MVP

- **Default sources: DexScreener + GeckoTerminal public APIs**, no X account, API key, or paid X plan required.
- DexScreener latest Solana token profiles and boosts enriched with pair data.
- GeckoTerminal latest Solana pools plus 24-hour trending pools.
- Explainable heuristic score based on liquidity, 24h volume, transaction activity, buy/sell balance and an FDV/liquidity risk flag.
- Optional X API adapter; X is not required in the default configuration.
- Optional Telegram alerts; scanner and dashboard can run without a Telegram bot.
- SQLite persistence and deduplication; local read-only FastAPI API and dashboard.
- No wallet connection, transaction signing, token creation, or automated trading.

## Data-source limitations

Both on-chain sources are public indexers, not complete feeds of every new token or every pump.fun launch. GeckoTerminal's API is beta, data is cached, and its public rate limit is low (official docs say approximately 10 calls/minute; CoinGecko's help article updated Oct 2, 2026 says 30 calls/minute). MemeHunter uses only two GeckoTerminal requests per scan cycle and enforces a minimum 120-second polling interval. Limits can change.

DexScreener profile/boost feeds can over-represent promoted tokens. A pool, profile or boost is not proof of organic demand or safety. The score is a heuristic signal, not investment advice. Always verify token address, liquidity, contract and holder distribution independently.

Official references:
- https://docs.dexscreener.com/api/reference
- https://api.geckoterminal.com/docs/index.html
- https://support.coingecko.com/articles/6867086195-does-geckoterminal-have-an-api

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env
```

No credentials are required for the default on-chain scanner. Edit `.env` only if you want optional Telegram or X integration. Never commit or share API keys, Telegram tokens, seed phrases or private keys.

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

## Source modes

- `SOURCE_MODE=onchain` (default): DexScreener + GeckoTerminal.
- `SOURCE_MODE=dexscreener`: DexScreener only.
- `SOURCE_MODE=geckoterminal`: GeckoTerminal only.
- `SOURCE_MODE=x`: X only; requires a valid local `X_API_BEARER_TOKEN`.
- `SOURCE_MODE=both`: both on-chain sources plus X; requires X credentials.
- `SOURCE_MODE=all`: all three sources; requires X credentials.
- Telegram alerts activate only when both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set.

## Safety

Read-only mode only. No wallet or private key is accepted. No token launch or automated trading is implemented. Never assume a token launch is free or that Creator Fees, liquidity, volume or profit are guaranteed.
