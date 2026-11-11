"""Read-only X API v2 recent-search adapter."""
import httpx
from ..models import Post


class XApiClient:
    BASE_URL = "https://api.x.com/2/tweets/search/recent"

    def __init__(self, bearer_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {bearer_token}"}

    async def search(self, query: str, *, max_results: int = 50, since_id: str | None = None) -> tuple[list[Post], str | None]:
        params: dict[str, str | int] = {
            "query": query,
            "max_results": min(100, max(10, max_results)),
            "tweet.fields": "created_at,author_id,public_metrics,attachments",
            "expansions": "attachments.media_keys",
            "media.fields": "media_key,type,url,preview_image_url,alt_text",
        }
        if since_id:
            params["since_id"] = since_id
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.BASE_URL, headers=self._headers, params=params)
            response.raise_for_status()
            payload = response.json()

        media_by_key = {
            media.get("media_key"): media
            for media in payload.get("includes", {}).get("media", [])
        }
        posts: list[Post] = []
        for item in payload.get("data", []):
            metrics = item.get("public_metrics", {})
            media_urls: list[str] = []
            media_alt_texts: list[str] = []
            for media_key in item.get("attachments", {}).get("media_keys", []):
                media = media_by_key.get(media_key, {})
                # Only use actual image URLs; video previews are not token artwork.
                if media.get("type") == "photo" and media.get("url", "").startswith("https://"):
                    media_urls.append(media["url"])
                    media_alt_texts.append(media.get("alt_text", ""))
            posts.append(Post(
                post_id=str(item["id"]),
                media_urls=tuple(media_urls),
                media_alt_texts=tuple(media_alt_texts),
                text=item.get("text", ""),
                author_id=str(item.get("author_id", "")),
                created_at=item.get("created_at", ""),
                like_count=int(metrics.get("like_count", 0)),
                repost_count=int(metrics.get("retweet_count", 0)),
                reply_count=int(metrics.get("reply_count", 0)),
                quote_count=int(metrics.get("quote_count", 0)),
            ))
        newest_id = max((p.post_id for p in posts), key=int, default=since_id)
        return posts, newest_id
