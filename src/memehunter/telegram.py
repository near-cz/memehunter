"""Telegram Bot API alert sender."""
import html
from urllib.parse import urlparse

import httpx
from .models import Candidate


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    @staticmethod
    def format_candidate(candidate: Candidate) -> str:
        post = candidate.post
        reasons = ", ".join(candidate.reasons)
        is_market = post.source in {"dexscreener", "geckoterminal"}
        if is_market:
            details = (
                f"💧 Liquidité : ${post.liquidity_usd:,.0f}\n"
                f"📊 Volume 24 h : ${post.volume_24h_usd:,.0f}\n"
                f"🟢 Achats / ventes : {post.buys_24h} / {post.sells_24h}\n"
                f"💵 Prix : ${post.price_usd:.8g}\n"
                f"🪙 Mint : <code>{html.escape(post.token_address)}</code>\n"
            )
            title = post.token_name + (f" (${post.token_symbol})" if post.token_symbol else "")
            source_label = "Voir le token / pool"
        else:
            details = f"❤️ {post.like_count}  🔁 {post.repost_count}  💬 {post.reply_count}\n"
            title = post.text[:900]
            source_label = "Voir le post source"

        parsed = urlparse(post.url)
        safe_url = post.url if parsed.scheme == "https" and parsed.netloc in {
            "dexscreener.com", "www.geckoterminal.com", "geckoterminal.com", "x.com", "twitter.com"
        } else ""
        link = f'<a href="{html.escape(safe_url, quote=True)}">{source_label}</a>' if safe_url else source_label
        return (
            f"🧠 <b>MemeHunter — signal détecté</b>\n"
            f"Score heuristique : <b>{candidate.score}/100</b>\n\n"
            f"{html.escape(title)}\n\n"
            f"{details}"
            f"Signaux : {html.escape(reasons)}\n"
            f"{link}\n\n"
            f"<i>Signal exploratoire, pas un conseil financier. Aucun lancement automatique n'est effectué.</i>"
        )

    async def send_candidate(self, candidate: Candidate) -> None:
        message = self.format_candidate(candidate)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self._url, json={
                "chat_id": self._chat_id, "text": message,
                "parse_mode": "HTML", "disable_web_page_preview": True,
            })
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                raise RuntimeError("Telegram rejected the alert")
