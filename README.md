# MemeHunter

MemeHunter is a Solana memecoin trend-monitoring project with Telegram alerts and a local web dashboard.

## Current MVP

- Read-only polling of X API v2 recent search.
- Explainable heuristic scoring based on post text and public engagement.
- SQLite deduplication, polling cursor and saved opportunity details.
- Telegram alerts include the original X post link.
- Local read-only FastAPI endpoints for health and opportunities.
- Dashboard consumes the local API; no fabricated market data.
- No wallet connection, transaction signing, token creation, or automatic trading.

## Setup

Requires Python 3.11+ and an X API bearer token with recent-search access.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill `.env` locally. Never commit it or share API keys, Telegram tokens, seed phrases or private keys.

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

Open http://127.0.0.1:8080. The API binds to 127.0.0.1 by default and only allows the local dashboard origins configured in `DASHBOARD_ORIGINS`.

API health: http://127.0.0.1:8000/api/v1/health  
API opportunities: http://127.0.0.1:8000/api/v1/opportunities  
Interactive API docs: http://127.0.0.1:8000/api/docs

Run tests with `pytest`.

## Important

The scanner requires X API recent-search access; availability and pricing depend on the X developer plan. This MVP has not been verified against a live X account in production. The API is read-only. Pump.fun launching, wallet signing, Creator Fee collection and automatic trading are not implemented. Do not assume launches are free or that Creator Fees or trading volume are guaranteed.
