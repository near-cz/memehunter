"""Polling loop for read-only trend discovery; it never signs or sends Solana transactions."""
import asyncio
import logging

from .config import Settings
from .scoring import score_post
from .sources.x_api import XApiClient
from .storage import Store
from .telegram import TelegramNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("memehunter")


async def run() -> None:
    settings = Settings.from_env()
    settings.validate()
    store = Store(settings.database_path)
    source = XApiClient(settings.x_api_bearer_token)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    log.info("MemeHunter scanner started (read-only mode)")
    try:
        while True:
            try:
                posts, newest_id = await source.search(settings.search_query, since_id=store.get_cursor())
                # Process oldest-first so Telegram alerts are chronological.
                for post in reversed(posts):
                    if not store.is_new(post.post_id):
                        continue
                    candidate = score_post(post)
                    store.mark_seen(post.post_id, candidate.score, post.created_at)
                    if candidate.score >= settings.min_score:
                        await notifier.send_candidate(candidate)
                        log.info("Alert sent for post %s (score=%s)", post.post_id, candidate.score)
                store.set_cursor(newest_id)
            except Exception as exc:  # keep the worker alive; never log credentials or full request headers
                log.warning("Polling cycle failed: %s", type(exc).__name__)
            await asyncio.sleep(settings.poll_interval_seconds)
    finally:
        store.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
