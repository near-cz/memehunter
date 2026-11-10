"""Read-only GeckoTerminal public API adapter for Solana pools.

Uses two bounded requests per scan cycle (new pools + trending pools).
No API key or wallet is required. The public API is beta and rate-limited.
"""
import asyncio
from datetime import datetime, timezone
import httpx
from ..models import Post

class GeckoTerminalClient:
    BASE_URL = "https://api.geckoterminal.com/api/v2"
    NETWORK = "solana"

    def __init__(self, *, max_pools: int = 20) -> None:
        self.max_pools = max(1, min(20, max_pools))

    async def _get(self, client: httpx.AsyncClient, endpoint: str) -> dict:
        response = await client.get(f"{self.BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _number(value, default: float = 0.0) -> float:
        try:
            return float(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    @classmethod
    def _pool_to_post(cls, pool: dict, included: dict[str, dict]) -> Post | None:
        attrs = pool.get("attributes") or {}
        relationships = pool.get("relationships") or {}
        base_ref = ((relationships.get("base_token") or {}).get("data") or {}).get("id")
        quote_ref = ((relationships.get("quote_token") or {}).get("data") or {}).get("id")
        base = included.get(base_ref, {})
        quote = included.get(quote_ref, {})
        base_attrs = base.get("attributes") or {}
        quote_attrs = quote.get("attributes") or {}
        quote_symbol = (quote_attrs.get("symbol") or "").upper()
        if quote_symbol in {"SOL", "WSOL", "USDC", "USDT", "USDS"} and base_attrs:
            token = base_attrs
        elif base_attrs:
            token = base_attrs
        else:
            token = quote_attrs
        address = token.get("address") or attrs.get("address") or ""
        if not address:
            return None
        txns = (attrs.get("transactions") or {}).get("h24") or {}
        volume = (attrs.get("volume_usd") or {}).get("h24")
        created_at = attrs.get("pool_created_at") or datetime.now(timezone.utc).isoformat()
        pool_address = attrs.get("address") or pool.get("id", "").split("_", 1)[-1]
        name = token.get("name") or attrs.get("name") or "Unknown token"
        symbol = token.get("symbol") or ""
        label = name + (" ($" + symbol + ")" if symbol else "")
        dex_ref = ((relationships.get("dex") or {}).get("data") or {}).get("id") or "unknown DEX"
        url = f"https://www.geckoterminal.com/solana/pools/{pool_address}"
        return Post(
            post_id=f"geckoterminal:{pool_address}",
            text=f"{label} | Pool: {attrs.get('name', '')} | DEX: {dex_ref}",
            author_id="", created_at=created_at, like_count=0, repost_count=0,
            reply_count=0, quote_count=0, source="geckoterminal", post_url=url,
            token_address=address, token_symbol=symbol, token_name=name,
            price_usd=cls._number(attrs.get("base_token_price_usd")),
            liquidity_usd=cls._number(attrs.get("reserve_in_usd")),
            volume_24h_usd=cls._number(volume),
            market_cap_usd=cls._number(attrs.get("market_cap_usd") or attrs.get("fdv_usd")),
            buys_24h=int(cls._number(txns.get("buys"))),
            sells_24h=int(cls._number(txns.get("sells"))),
        )

    @classmethod
    def _parse_pool_response(cls, payload: dict, max_pools: int) -> list[Post]:
        included = {
            item.get("id"): item for item in (payload.get("included") or [])
            if item.get("type") == "token" and item.get("id")
        }
        posts = []
        for pool in payload.get("data") or []:
            if pool.get("type") != "pool":
                continue
            post = cls._pool_to_post(pool, included)
            if post:
                posts.append(post)
            if len(posts) >= max_pools:
                break
        return posts

    async def discover(self) -> list[Post]:
        headers = {
            "User-Agent": "MemeHunter/0.4",
            "Accept": "application/json;version=20230203",
        }
        timeout = httpx.Timeout(20.0)
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            # Two API calls per cycle; do not paginate or fan out requests.
            new_pools, trending = await asyncio.gather(
                self._get(client, f"/networks/{self.NETWORK}/new_pools?include=base_token,quote_token,dex&page=1"),
                self._get(client, f"/networks/{self.NETWORK}/trending_pools?include=base_token,quote_token,dex&page=1&duration=24h"),
            )
        combined = self._parse_pool_response(new_pools, self.max_pools)
        seen = {post.post_id for post in combined}
        for post in self._parse_pool_response(trending, self.max_pools):
            if post.post_id not in seen and len(combined) < self.max_pools * 2:
                combined.append(post)
                seen.add(post.post_id)
        return combined
