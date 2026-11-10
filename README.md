# MemeHunter

MemeHunter is a Solana memecoin trend-monitoring project with Telegram alerts and a planned web dashboard.

## Current MVP

- Read-only polling of X API v2 recent search.
- Explainable heuristic scoring based on post text and public engagement.
- SQLite deduplication and a saved X search cursor.
- Telegram alerts that always include the original post link.
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

Fill `.env` locally, then run:

```bash
memehunter
```

Run tests with `pytest`.

## Configuration

See `.env.example`. Credentials must remain local and must never be committed.

## Important

The score is a simple exploratory heuristic, not an AI prediction or investment advice. X API access and rate limits depend on the user's plan. The launch adapter is intentionally not implemented until Pump.fun's current official interfaces, fees, and terms are verified. No revenue is guaranteed.
