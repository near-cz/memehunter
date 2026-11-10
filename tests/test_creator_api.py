def test_creator_drafts_api_returns_review_queue(tmp_path, monkeypatch):
    from memehunter.api import creator_drafts
    from memehunter.models import Candidate, Post
    from memehunter.storage import Store

    path = str(tmp_path / "api.sqlite3")
    store = Store(path)
    post = Post("tweet-1", "A #MoonCat meme is trending", "author",
                "2026-11-10T10:00:00Z", 100, 50, 20, 10,
                source="x", post_url="https://x.com/user/status/tweet-1")
    store.enqueue_creator_draft(Candidate(post, 82, ("engagement:high",)))
    store.close()
    monkeypatch.setattr("memehunter.api._database_path", lambda: path)

    response = creator_drafts(limit=20)
    assert response["total"] == 1
    assert response["created_today"] == 1
    assert response["items"][0]["symbol"] == "MOONCA"
    assert response["launch_enabled"] is False
