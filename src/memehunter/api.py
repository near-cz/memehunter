"""Read-only local API for the MemeHunter dashboard."""
import json
import os
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .risk import risk_status

def _market_risk_status(reasons: str, source: str) -> str:
    if source not in {"dexscreener", "geckoterminal"}:
        return "unknown"
    flags = [part for part in (reasons or "").split(" | ") if part.startswith("risk:")]
    return risk_status(flags) if flags else "unknown"


def _database_path() -> str:
    return os.getenv("DATABASE_PATH", "data/memehunter.sqlite3")
def _connect_readonly():
    path = Path(_database_path()).resolve()
    if not path.exists():
        return None
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
app = FastAPI(title="MemeHunter API", version="0.3.0", docs_url="/api/docs")
origins = [item.strip() for item in os.getenv("DASHBOARD_ORIGINS", "http://127.0.0.1:8080,http://localhost:8080").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])
@app.get("/api/v1/health")
def health():
    path = Path(_database_path())
    return {"status": "ok", "database": "ready" if path.exists() else "waiting_for_scanner",
            "mode": "read-only", "token_launch_enabled": False, "x_required": False,
            "default_source": os.getenv("SOURCE_MODE", "onchain"),
            "x_configured": bool(os.getenv("X_API_BEARER_TOKEN")),
            "creator_queue_enabled": True,
            "token_launch_enabled": False}
@app.get("/api/v1/opportunities")
def opportunities(limit: int = Query(default=50, ge=1, le=100)):
    connection = _connect_readonly()
    if connection is None:
        return {"items": [], "total": 0}
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(seen_posts)")}
        required = {"text", "url", "reasons", "source", "token_address", "price_usd", "liquidity_usd", "volume_24h_usd", "buys_24h", "sells_24h"}
        if not required.issubset(columns):
            return {"items": [], "total": 0, "message": "Scanner schema upgrade pending"}
        total = connection.execute("SELECT COUNT(*) FROM seen_posts WHERE score >= 45").fetchone()[0]
        rows = connection.execute("""SELECT post_id, score, created_at, text, url, like_count, repost_count,
            reply_count, quote_count, reasons, source, token_address, token_symbol, token_name,
            price_usd, liquidity_usd, volume_24h_usd, market_cap_usd, buys_24h, sells_24h
            FROM seen_posts WHERE score >= 45 ORDER BY created_at DESC LIMIT ?""", (limit,)).fetchall()
        items = [{"post_id": r[0], "score": r[1], "created_at": r[2], "text": r[3], "url": r[4],
            "likes": r[5], "reposts": r[6], "replies": r[7], "quotes": r[8],
            "reasons": r[9].split(" | ") if r[9] else [], "source": r[10],
            "token_address": r[11], "token_symbol": r[12], "token_name": r[13],
            "price_usd": r[14], "liquidity_usd": r[15], "volume_24h_usd": r[16],
            "market_cap_usd": r[17], "buys_24h": r[18], "sells_24h": r[19],
            "risk_flags": [part for part in (r[9] or "").split(" | ") if part.startswith("risk:")],
            "risk_status": _market_risk_status(r[9], r[10])} for r in rows]
        return {"items": items, "total": total}
    finally:
        connection.close()
@app.get("/api/v1/creator/drafts")
def creator_drafts(limit: int = Query(default=20, ge=1, le=50)):
    """Read-only list of generated creator drafts awaiting human review."""
    connection = _connect_readonly()
    if connection is None:
        return {"items": [], "total": 0, "daily_limit": 5}
    try:
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if "creator_drafts" not in tables:
            return {"items": [], "total": 0, "daily_limit": 5}
        total = connection.execute("SELECT COUNT(*) FROM creator_drafts").fetchone()[0]
        rows = connection.execute(
            "SELECT payload, status, created_at FROM creator_drafts "
            "ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        items = []
        for payload, status, created_at in rows:
            item = json.loads(payload)
            item["status"] = status
            item["created_at"] = created_at
            items.append(item)
        today = connection.execute(
            "SELECT COUNT(*) FROM creator_drafts WHERE date(created_at) = date('now')"
        ).fetchone()[0]
        return {"items": items, "total": total, "created_today": today, "daily_limit": 5,
                "launch_enabled": False}
    finally:
        connection.close()


def main() -> None:
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "127.0.0.1"), port=int(os.getenv("API_PORT", "8000")))
if __name__ == "__main__":
    main()
