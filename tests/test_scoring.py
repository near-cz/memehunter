from memehunter.models import Post
from memehunter.scoring import score_post


def test_high_engagement_meme_post_scores_higher_than_weak_post():
    strong = Post("2", "This memecoin launch is going viral", "a", "2026-01-01T00:00:00Z", 800, 300, 100, 50)
    weak = Post("1", "hello world", "b", "2026-01-01T00:00:00Z", 0, 0, 0, 0)
    assert score_post(strong).score > score_post(weak).score
    assert score_post(strong).score <= 100
