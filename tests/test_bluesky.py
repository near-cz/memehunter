from memehunter.sources.bluesky import BlueskyClient


def test_parse_bluesky_search_response(monkeypatch):
    payload = {
        "posts": [{
            "uri": "at://did:plc:abc/app.bsky.feed.post/post123",
            "record": {"text": "This meme is going viral", "createdAt": "2026-11-11T12:00:00Z"},
            "author": {"did": "did:plc:abc", "handle": "meme.bsky.social"},
            "likeCount": 42, "repostCount": 8, "replyCount": 3, "quoteCount": 1,
            "embed": {"images": [{"fullsize": "https://cdn.bsky.app/img/feed_fullsize/plain/example", "alt": "A meme"}]},
        }]
    }

    class Response:
        def raise_for_status(self):
            pass
        def json(self):
            return payload

    class Client:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def get(self, *args, **kwargs):
            return Response()

    monkeypatch.setattr("memehunter.sources.bluesky.httpx.AsyncClient", Client)
    import asyncio
    posts = asyncio.run(BlueskyClient().search("meme"))
    assert len(posts) == 1
    post = posts[0]
    assert post.source == "bluesky"
    assert post.post_url == "https://bsky.app/profile/meme.bsky.social/post/post123"
    assert post.like_count == 42
    assert post.media_urls == ("https://cdn.bsky.app/img/feed_fullsize/plain/example",)
