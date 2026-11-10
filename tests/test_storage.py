from memehunter.models import Candidate, Post
from memehunter.storage import Store


def test_notification_outbox_is_durable_and_idempotent(tmp_path):
    path = str(tmp_path / "memehunter.sqlite3")
    candidate = Candidate(
        Post("dex:mint123", "Example token", "", "2026-11-10T10:00:00Z",
             0, 0, 0, 0, source="dexscreener", token_address="mint123"),
        72,
        ("liquidity:strong",),
    )

    store = Store(path)
    assert store.enqueue_notification(candidate) is True
    assert store.enqueue_notification(candidate) is False
    store.mark_seen(candidate)
    store.record_notification_failure(candidate.post.post_id, "TimeoutException")
    store.close()

    reopened = Store(path)
    pending = reopened.pending_notifications()
    assert len(pending) == 1
    assert pending[0] == candidate
    reopened.mark_notification_sent(candidate.post.post_id)
    assert reopened.pending_notifications() == []
    reopened.close()
