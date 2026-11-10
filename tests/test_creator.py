from memehunter.creator import build_creator_draft
from memehunter.models import Candidate, Post
from memehunter.storage import Store


def _candidate(post_id, text="This #MoonCat trend is everywhere"):
    return Candidate(
        Post(post_id, text, "author", "2026-11-10T10:00:00Z", 100, 40, 12, 5,
             source="x", post_url=f"https://x.com/user/status/{post_id}"),
        82,
        ("signal:meme", "engagement:high"),
    )


def test_creator_draft_is_a_reviewable_zero_buy_concept():
    draft = build_creator_draft(_candidate("123"))
    assert draft["name"] == "Mooncat"
    assert draft["symbol"] == "MOONCA"
    assert draft["source_url"] == "https://x.com/user/status/123"
    assert draft["initial_buy_sol"] == 0
    assert draft["launch_enabled"] is False
    assert draft["status"] == "pending_review"


def test_creator_queue_is_idempotent_and_capped_at_five_per_day(tmp_path):
    store = Store(str(tmp_path / "memehunter.sqlite3"))
    for index in range(5):
        assert store.enqueue_creator_draft(_candidate(str(index))) is True
    assert store.enqueue_creator_draft(_candidate("duplicate")) is False
    assert store.enqueue_creator_draft(_candidate("0")) is False
    drafts = store.db.execute("SELECT COUNT(*) FROM creator_drafts").fetchone()[0]
    assert drafts == 5
    store.close()


def test_creator_queue_ignores_non_x_posts(tmp_path):
    store = Store(str(tmp_path / "memehunter.sqlite3"))
    post = Post("dex:mint", "Token", "", "2026-11-10T10:00:00Z",
                0, 0, 0, 0, source="dexscreener")
    assert store.enqueue_creator_draft(Candidate(post, 90, ("volume:high",))) is False
    store.close()
