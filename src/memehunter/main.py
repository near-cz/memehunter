"""Polling loop for read-only trend discovery; it never signs Solana transactions."""
import asyncio
import logging
from .config import Settings
from .scoring import score_post
from .sources.dexscreener import DexScreenerClient
from .sources.geckoterminal import GeckoTerminalClient
from .sources.x_api import XApiClient
from .storage import Store
from .telegram import TelegramNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("memehunter")

async def run() -> None:
    settings = Settings.from_env()
    settings.validate()
    store = Store(settings.database_path)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id) if settings.telegram_bot_token else None
    dex = DexScreenerClient(max_tokens=settings.max_tokens_per_cycle)
    gecko = GeckoTerminalClient(max_pools=settings.max_tokens_per_cycle)
    x_source = XApiClient(settings.x_api_bearer_token) if settings.x_api_bearer_token else None
    modes = settings.source_mode
    use_dex = modes in {"dexscreener", "onchain", "both", "all"}
    use_gecko = modes in {"geckoterminal", "onchain", "both", "all"}
    use_x = modes in {"x", "both", "all"}
    log.info("MemeHunter scanner started (read-only; source_mode=%s)", modes)
    try:
        while True:
            try:
                posts = []
                if use_dex:
                    try:
                        posts.extend(await dex.discover())
                    except Exception as exc:
                        log.warning("DexScreener unavailable: %s", type(exc).__name__)
                if use_gecko:
                    try:
                        posts.extend(await gecko.discover())
                    except Exception as exc:
                        log.warning("GeckoTerminal unavailable: %s", type(exc).__name__)
                if use_x and x_source:
                    x_posts, newest_id = await x_source.search(settings.search_query, since_id=store.get_cursor())
                    posts.extend(x_posts)
                    store.set_cursor(newest_id)
                for post in posts:
                    is_new = store.is_new(post.post_id)
                    candidate = score_post(post)
                    if is_new and candidate.score >= settings.min_score and notifier:
                        # Persist only after successful delivery so transient Telegram errors retry next cycle.
                        await notifier.send_candidate(candidate)
                        log.info("Alert sent for %s item %s (score=%s)", post.source, post.post_id, candidate.score)
                    store.mark_seen(candidate)
                log.info("Cycle complete: %s public signals", len(posts))
            except Exception as exc:
                log.warning("Polling cycle failed: %s", type(exc).__name__)
            await asyncio.sleep(settings.poll_interval_seconds)
    finally:
        store.close()

def main() -> None:
    asyncio.run(run())

if __name__ == "__main__":
    main()
