# MemeHunter

MemeHunter is a Solana memecoin discovery system: public market scanning, explainable scoring, a mobile-friendly dashboard and optional Telegram alerts.

## Product roadmap: two core pillars

- **MemeHunter** discovers Solana memecoin opportunities and highlights market risks.
- **Creator & Publisher** is the next major build: prepare a token brand and metadata, review a launch, publish through a wallet-approved flow, then prepare and manage launch communications. The staged implementation and security requirements are documented in [docs/creator-publisher.md](docs/creator-publisher.md).

Creator & Publisher is not implemented yet; the current application remains read-only.

## Current capabilities

- **Default sources: DexScreener + GeckoTerminal public APIs**, no X account or paid API key required.
- New/trending Solana pool discovery and market activity scoring.
- **Market-risk flags:** highlights very low/low liquidity, very low activity, sell pressure and unusually high valuation-to-liquidity ratios. Missing market fields are labelled unknown rather than safe. These are screening heuristics, not honeypot, holder, mint-authority or freeze-authority checks.
- Optional X API v2 scanning; the cloud blueprint enables the combined mode and pauses X polling until a bearer token is configured.
- **Creator Studio draft queue:** qualifying new X signals can produce a concept name, ticker, review description and source link. The queue is capped at five drafts per UTC day.
- Optional Telegram alerts with the token/source link.
- SQLite persistence and deduplication.
- Read-only launch workflow: Creator Studio drafts are review-only. No wallet custody, transaction signing, token creation or automated trading.
- Cloud mode runs the scanner, API and dashboard in one service so they share a persistent SQLite database.

## Cloud hosting (recommended)

The included `render.yaml` deploys one Render web service with a persistent disk. This is deliberately one service: the scanner and API must share the same SQLite file, and a Render persistent disk cannot be mounted by multiple services simultaneously.

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint**, connect this repository and apply the blueprint.
3. Before the first deploy, open the service's **Environment** page and set `DASHBOARD_USERNAME=admin` and `DASHBOARD_PASSWORD` to your chosen secret. The password is stored as a server-side environment variable, never in the HTML or Git.
4. Set `X_API_BEARER_TOKEN` in the service environment to enable X scanning. X API access is subject to X's current access tiers, rate limits and pricing; without the token, on-chain scanning continues but X polling is paused.\n5. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the service environment if you want Telegram alerts. Never paste any secret into GitHub or this chat.
5. Deploy the changes. Open the service URL; the browser asks for the username `admin` and the generated password.
6. Test `/api/v1/health`, then check Telegram after a new signal qualifies. If the dashboard credentials are missing, cloud mode fails closed with HTTP 503 instead of exposing the dashboard.

**Important:** choose a paid always-on Render web service with a persistent disk for continuous scanning and SQLite persistence. Free services may sleep and are not suitable for an always-on scanner. Hosting and disk have a cost; check Render's current pricing before confirming.

The dashboard and API are served from the same origin, protected by HTTP Basic Auth. Configure `DASHBOARD_PASSWORD` in Render's Environment settings; do not hardcode it in HTML, JavaScript, or a committed file. The scanner starts automatically with the web service and restarts when the service restarts. No computer needs to remain on.

## Local development

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env
memehunter
```

In another terminal run `memehunter-api`, then serve `apps/dashboard` with `python -m http.server 8080 --directory apps/dashboard`. Open `http://127.0.0.1:8080`.

## Configuration

- `SOURCE_MODE=onchain`: DexScreener + GeckoTerminal (default).
- `SOURCE_MODE=dexscreener` or `geckoterminal`: one source only.
- `SOURCE_MODE=x`: X only; requires `X_API_BEARER_TOKEN`.
- `SOURCE_MODE=both` or `all`: on-chain sources plus X; requires X credentials.
- Telegram activates only when both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set.
- `POLL_INTERVAL_SECONDS` has a 120-second minimum.

## Automation roadmap and boundaries

**Already automatic:** scanner polling, candidate scoring, database deduplication, Telegram alert delivery (when Telegram is configured), and creation of up to five review-only Creator Studio drafts per UTC day from qualifying new X posts (when X API access is configured).

**Not implemented yet:** image generation/artwork upload, full promotional launch campaigns, publishing to X, Pump.fun transaction construction/submission, token creation, trading, or Creator Fee accounting. Telegram signal alerts can be delivered to a private chat or posted directly into a channel where the bot is an administrator; they are scanner alerts, not automatic token-launch announcements. Pump.fun launch automation must wait for verified official interfaces, fee/terms review, explicit user approval and secure wallet signing. No seed phrase or private key should ever be entered into MemeHunter's dashboard or this chat.

No score guarantees safety, volume, profit or Creator Fees. Public indexers are incomplete and may contain stale or promoted data. Always verify token mint, liquidity, authority settings and holder distribution independently.

## CI

GitHub Actions runs the unit tests on pushes and pull requests to `main`.
