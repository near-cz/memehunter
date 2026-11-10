"""Read-only adapter for public DexScreener market data (no API key)."""
import asyncio
from datetime import datetime, timezone
import httpx
from ..models import Post

class DexScreenerClient:
    BASE_URL = "https://api.dexscreener.com"
    def __init__(self, *, max_tokens: int = 12) -> None:
        self.max_tokens = max(1, min(20, max_tokens))
    async def _get(self, client: httpx.AsyncClient, path: str):
        response = await client.get(f"{self.BASE_URL}{path}")
        response.raise_for_status()
        return response.json()
    async def discover(self) -> list[Post]:
        timeout = httpx.Timeout(15.0)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "MemeHunter/0.3"}) as client:
            profiles, boosts = await asyncio.gather(
                self._get(client, "/token-profiles/latest/v1"),
                self._get(client, "/token-boosts/latest/v1"))
            merged: dict[str, dict] = {}
            for item in (profiles if isinstance(profiles, list) else []) + (boosts if isinstance(boosts, list) else []):
                if item.get("chainId") != "solana" or not item.get("tokenAddress"):
                    continue
                address = item["tokenAddress"]
                current = merged.setdefault(address, dict(item))
                for key, value in item.items():
                    if value and not current.get(key):
                        current[key] = value
            addresses = list(merged)[:self.max_tokens]
            semaphore = asyncio.Semaphore(4)
            async def fetch_pairs(address: str):
                async with semaphore:
                    try:
                        return address, await self._get(client, f"/token-pairs/v1/solana/{address}")
                    except (httpx.HTTPError, ValueError):
                        return address, []
            pair_results = await asyncio.gather(*(fetch_pairs(address) for address in addresses))
            pair_map = dict(pair_results)
        now = datetime.now(timezone.utc).isoformat()
        posts = []
        for address in addresses:
            metadata = merged[address]
            pairs = pair_map.get(address) or []
            solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]
            if not solana_pairs:
                continue
            pair = max(solana_pairs, key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0))
            base = pair.get("baseToken") or {}
            h24 = (pair.get("txns") or {}).get("h24") or {}
            links = metadata.get("links") or []
            social_links = [f'{x.get("type", "link")}: {x.get("url")}' for x in links if x.get("url")]
            description = metadata.get("description") or ""
            name, symbol = base.get("name") or "Unknown token", base.get("symbol") or ""
            label = name + " ($" + symbol + ")" if symbol else name
            text_value = " | ".join(part for part in (label, description[:700], " ".join(social_links[:4])) if part)
            pair_created = pair.get("pairCreatedAt")
            created_at = datetime.fromtimestamp(pair_created / 1000, timezone.utc).isoformat() if pair_created else now
            pair_url = pair.get("url") or metadata.get("url") or f"https://dexscreener.com/solana/{address}"
            posts.append(Post(
                post_id=f"dexscreener:{address}", text=text_value, author_id="", created_at=created_at,
                like_count=0, repost_count=0, reply_count=0, quote_count=0,
                source="dexscreener", post_url=pair_url, token_address=address,
                token_symbol=symbol, token_name=name, price_usd=float(pair.get("priceUsd") or 0),
                liquidity_usd=float((pair.get("liquidity") or {}).get("usd") or 0),
                volume_24h_usd=float((pair.get("volume") or {}).get("h24") or 0),
                market_cap_usd=float(pair.get("marketCap") or 0),
                buys_24h=int(h24.get("buys") or 0), sells_24h=int(h24.get("sells") or 0)))
        return posts
