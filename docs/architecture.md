# Initial architecture

## Components

1. Ingestion: collect permitted public trend signals.
2. Normalization: deduplicate posts and normalize timestamps, links, and entities.
3. Scoring: evaluate momentum, novelty, saturation, source quality, and risk.
4. Opportunity store: persist candidates and original source-post URLs.
5. Telegram: send alerts and expose basic status commands.
6. Dashboard: present candidates, launches, and operational metrics.
7. Launch adapter: isolated and disabled until current official interfaces, fees, and terms are verified.

## Safety boundaries

- Discovery and scoring must work without a funded wallet.
- Never accept private keys or seed phrases in the scanner, bot, or dashboard.
- Isolate any future transaction signer from web-facing services.
- Enforce a hard maximum of five launches per day, spending ceilings, duplicate checks, confidence thresholds, and a kill switch.
- Record source URLs and actual transaction fees.
- Creator-fee revenue is variable and never guaranteed.

## Implementation order

1. Repository hygiene and configuration.
2. Read-only trend ingestion and deduplication.
3. Scoring and candidate persistence.
4. Telegram alerts.
5. Dashboard.
6. Separately tested launch integration.
