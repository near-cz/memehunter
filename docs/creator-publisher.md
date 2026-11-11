# MemeHunter Creator & Publisher

## Product role

Creator & Publisher is a first-class product pillar beside MemeHunter's discovery scanner. It helps prepare, review, launch and promote a Solana memecoin from one workspace. It must not imply that a launch, audience, trading volume, price appreciation or creator-fee income is guaranteed.

## User journey

1. **Concept** — choose a name, ticker, description, narrative, links and target audience. Check for duplicate or confusingly similar names and obvious impersonation/IP concerns.
2. **Brand kit** — create or upload original artwork, crop it for token metadata, and prepare consistent profile/banner/social assets. Keep generated assets editable/reviewable before publication.
3. **Metadata** — validate image and metadata fields, upload through a configured pinning provider, and retain the resulting content URI and upload status.
4. **Launch review** — show the creator wallet, network, estimated network/priority/provider fees, initial buy amount (including an explicit zero-buy option), selected Pump.fun options, and the exact transaction summary. Run duplicate, metadata, balance and configuration checks.
5. **Wallet approval** — build the transaction server-side or in a trusted client module, but never collect or store a seed phrase/private key. The connected wallet must display and sign the transaction itself. No transaction is sent until the user confirms in their wallet.
6. **Publish & verify** — submit only the wallet-signed transaction, track its signature, confirm finality, and record the mint address and canonical token page only after on-chain verification.
7. **Promotion studio** — draft launch posts, Telegram announcements, descriptions and follow-up updates. Preview each destination, preserve source links, and require explicit approval before publishing. Respect platform rate limits and anti-spam rules.
8. **Creator dashboard** — show launch status, transaction costs, public links, campaign history and creator-fee information where a reliable source is available. Label estimates and unverified data clearly.

## Implementation phases

### Phase A — Creator workspace (partially implemented; no wallet required)
- [x] Add a dedicated Creator Studio area to the dashboard.
- [x] Generate review-only concept drafts from qualifying new X posts: suggested name, ticker, neutral description, score and source link.
- [x] Request X photo-media expansions and preview up to four source-tweet photos in Creator Studio when available.
- [x] Persist drafts in SQLite and expose a read-only API endpoint.
- [x] Enforce a maximum of five new draft records per UTC day (configurable from zero to five).
- [ ] Add editable draft fields, image upload/generation, metadata validation and a launch checklist.
- [ ] Add reviewed campaign copy/templates with manual approval.

### Phase B — Metadata and wallet connection
- Add a supported metadata pinning adapter configured with server-side secrets.
- Add a Solana wallet-adapter flow; wallet connection is not wallet custody.
- Display network, creator address, fees and all launch parameters before approval.
- Add transaction simulation/preflight where supported.

### Phase C — Pump.fun launch adapter
- Verify the current official Pump.fun launch interface, SDK versions, endpoint availability, regional eligibility, terms and fee model immediately before implementation.
- Keep the launch adapter isolated from the scanner and web-facing API.
- Build an unsigned/partially signed transaction and require the user's wallet to co-sign and submit it.
- Verify the confirmed transaction and mint from Solana RPC before showing "Published".
- If the documented interface is unavailable or changes, stop safely and offer a manual Pump.fun handoff instead of silently using an unofficial endpoint.

### Phase D — Publisher automation
- Add opt-in publishing integrations one destination at a time.
- Require preview and explicit approval per post/campaign; allow the user to disable or cancel scheduled work.
- Store delivery status and source URLs; use bounded retries and avoid duplicate posts.
- No fake engagement, wash trading, misleading claims, spam, impersonation or undisclosed paid promotion.

## Non-negotiable security and launch controls

- Never request, transmit, log or store a seed phrase or raw private key.
- Never sign transactions on the user's behalf. Signing happens only in the user's connected wallet.
- Never launch or spend SOL without an explicit, per-launch confirmation in the wallet.
- Make initial buy amount, creator wallet, network and fee estimates visible before signing.
- Enforce configurable daily launch limits, spend ceilings, duplicate checks and an emergency kill switch.
- Keep API keys and pinning credentials server-side in environment secrets.
- Record transaction signatures, actual network fees and launch outcomes.
- Do not promise creator-fee revenue; show only verifiable payouts and clearly labelled estimates.
- Do not enable automated trading or artificial volume/engagement.

## Current implementation boundary

The current Creator Studio queue is a research/drafting aid only. It previews photo URLs returned by X (it does not download, host or grant reuse rights to them), does not generate artwork or create metadata uploads, connect a wallet, build or sign transactions, create tokens, publish posts, or calculate Creator Fees. X scanning requires a valid X API bearer token; without it, the on-chain scanner remains active and X polling is paused.

## Pump.fun integration note (verified 10 November 2026)

The public Pump.fun Developer API documentation describes a keyed, read-only API. Its terms state that the API key cannot create, post, trade, transfer or sign. A separate official pump-fun/pump-fun-skills repository contains a create-coin workflow referencing the fun-block.pump.fun/agents/create-coin endpoint, a partially signed transaction and wallet co-signing. That repository is archived, so this endpoint must be re-verified for availability, current support, terms, SDK compatibility and eligibility before production use. Do not treat the read-only Developer API key as a launch credential.

References:
- https://docs.pump.fun/
- https://docs.pump.fun/terms/
- https://github.com/pump-fun/pump-fun-skills/blob/main/create-coin/SKILL.md
