"""Read-only local API for the MemeHunter dashboard."""
import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


def _database_path() -> str:
    return os.getenv("DATABASE_PATH", "data/memehunter.sqlite3")


def _connect_readonly():
    path = Path(_database_path()).resolve()
    if not path.exists():
        return None
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


app = FastAPI(title="MemeHunter API", version="0.2.0", docs_url="/api/docs")
origins = [item.strip() for item in os.getenv(
    "DASHBOARD_ORIGINS", "http://127.0.0.1:8080,http://localhost:8080"
).split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health():
    path = Path(_database_path())
    return {
        "status": "ok",
        "database": "ready" if path.exists() else "waiting_for_scanner",
        "mode": "read-only",
        "token_launch_enabled": False,
    }


@app.get("/api/v1/opportunities")
def opportunities(limit: int = Query(default=50, ge=1, le=100)):
    connection = _connect_readonly()
    if connection is None:
        return {"items": [], "total": 0}
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(seen_posts)")}
        required = {"text", "url", "like_count", "repost_count", "reply_count", "quote_count", "reasons"}
        if not required.issubset(columns):
            return {"items": [], "total": 0, "message": "Scanner schema upgrade pending"}
        total = connection.execute("SELECT COUNT(*) FROM seen_posts WHERE score >= 45").fetchone()[0]
        rows = connection.execute(
            """SELECT post_id, score, created_at, text, url, like_count, repost_count,
                      reply_count, quote_count, reasons
               FROM seen_posts WHERE score >= 45
               ORDER BY created_at DESC LIMIT ?""", (limit,)
        ).fetchall()
        items = [{
            "post_id": row[0], "score": row[1], "created_at": row[2],
            "text": row[3], "url": row[4], "likes": row[5],
            "reposts": row[6], "replies": row[7], "quotes": row[8],
            "reasons": row[9].split(" | ") if row[9] else [],
        } for row in rows]
        return {"items": items, "total": total}
    finally:
        connection.close()


def main() -> None:
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "127.0.0.1"),
                port=int(os.getenv("API_PORT", "8000")))


if __name__ == "__main__":
    main()
