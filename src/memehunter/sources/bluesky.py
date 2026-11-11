"""Read-only adapter for public Bluesky search; no account or API key required."""
from urllib.parse import quote
import httpx
from ..models import Post


class BlueskyClient:
    BASE_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"

    async def search(self, query: str, *, max_results: int = 50) -> list[Post]:
        params = {"q": query, "sort": "latest", "limit": min(100, max(1, max_results))}
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "MemeHunter/0.4"}) as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        posts: list[Post] = []
        for item in payload.get("posts", []):
            record = item.get("record") or {}
            author = item.get("author") or {}
            handle = author.get("handle") or ""
            uri = item.get("uri") or ""
            rkey = uri.rsplit("/", 1)[-1]
            post_url = f"https://bsky.app/profile/{quote(handle, safe='.')}/post/{quote(rkey, safe='')}" if handle and rkey else ""
            embed = item.get("embed") or {}
            images = embed.get("images") or (embed.get("media") or {}).get("images") or []
            media_urls, media_alt_texts = [], []
            for image in images:
                url = image.get("fullsize") or image.get("thumb") or ""
                if url.startswith("https://"):
                    media_urls.append(url)
                    media_alt_texts.append(image.get("alt") or "")
            posts.append(Post(
                post_id=uri or f"bluesky:{handle}:{rkey}",
                text=record.get("text", ""),
                author_id=author.get("did", ""),
                created_at=record.get("createdAt") or item.get("indexedAt", ""),
                like_count=int(item.get("likeCount") or 0),
                repost_count=int(item.get("repostCount") or 0),
                reply_count=int(item.get("replyCount") or 0),
                quote_count=int(item.get("quoteCount") or 0),
                media_urls=tuple(media_urls),
                media_alt_texts=tuple(media_alt_texts),
                source="bluesky",
                post_url=post_url,
            ))
        return posts
