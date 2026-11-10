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
        if p.source == "dexscreener":
            details = (
                f"💧 Liquidité : ${p.liquidity_usd:,.0f}\n"
                f"📊 Volume 24 h : ${p.volume_24h_usd:,.0f}\n"
                f"🟢 Achats / ventes : {p.buys_24h} / {p.sells_24h}\n"
                f"💵 Prix : ${p.price_usd:.8g}\n"
            )
            source_label = "Voir le token sur DexScreener"
            title = p.token_name + (f" (${p.token_symbol})" if p.token_symbol else "")
        else:
            details = f"❤️ {p.like_count}  🔁 {p.repost_count}  💬 {p.reply_count}\n"
            source_label = "Voir le post source"
            title = p.text[:900]
        message = (
            f"🧠 <b>MemeHunter — signal détecté</b>\n"
            f"Score heuristique : <b>{candidate.score}/100</b>\n\n"
            f"{_escape(title)}\n\n"
            f"{details}"
            f"Signaux : {_escape(reasons)}\n"
            f"<a href=\"{p.url}\">{source_label}</a>\n\n"
            f"<i>Signal exploratoire, pas un conseil financier. Aucun lancement automatique n'est effectué.</i>"
        )
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self._url, json={
                "chat_id": self._chat_id, "text": message,
                "parse_mode": "HTML", "disable_web_page_preview": True,
            })
            response.raise_for_status()
            data = response.json()
            if not data.get("ok"):
                raise RuntimeError("Telegram rejected the alert")

def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
