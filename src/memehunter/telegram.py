"""Telegram Bot API alert sender."""
import httpx
from .models import Candidate


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    async def send_candidate(self, candidate: Candidate) -> None:
        p = candidate.post
        reasons = ", ".join(candidate.reasons)
        message = (
            f"🧠 <b>MemeHunter — signal détecté</b>\n"
            f"Score heuristique : <b>{candidate.score}/100</b>\n\n"
            f"{_escape(p.text[:900])}\n\n"
            f"❤️ {p.like_count}  🔁 {p.repost_count}  💬 {p.reply_count}\n"
            f"Signaux : {_escape(reasons)}\n"
            f"<a href=\"{p.url}\">Voir le post source</a>\n\n"
            f"<i>Signal exploratoire, pas un conseil financier. Aucun lancement automatique n'est effectué.</i>"
        )
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self._url, json={
                "chat_id": self._chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            })
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                raise RuntimeError("Telegram rejected the alert")


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
