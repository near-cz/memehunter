"""Single-process cloud deployment: API, dashboard and scanner share one SQLite volume."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import app as api_app
from .main import run as run_scanner

log = logging.getLogger("memehunter.cloud")
scanner_task: asyncio.Task | None = None

@api_app.middleware("http")
async def dashboard_basic_auth(request, call_next):
    username = os.getenv("DASHBOARD_USERNAME", "")
    password = os.getenv("DASHBOARD_PASSWORD", "")
    if username and password:
        import base64
        import secrets
        from starlette.responses import Response
        header = request.headers.get("authorization", "")
        supplied_user = supplied_password = ""
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
                supplied_user, supplied_password = decoded.split(":", 1)
            except (ValueError, UnicodeDecodeError):
                pass
        if not (secrets.compare_digest(supplied_user, username) and
                secrets.compare_digest(supplied_password, password)):
            return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="MemeHunter"'})
    return await call_next(request)

@api_app.on_event("startup")
async def start_scanner():
    global scanner_task
    scanner_task = asyncio.create_task(run_scanner(), name="memehunter-scanner")
    log.info("Cloud dashboard/API started; scanner task launched")

@api_app.on_event("shutdown")
async def stop_scanner():
    global scanner_task
    if scanner_task:
        scanner_task.cancel()
        try:
            await scanner_task
        except asyncio.CancelledError:
            pass
        scanner_task = None

dashboard_dir = Path(__file__).resolve().parent / "static"
if dashboard_dir.exists():
    api_app.mount("/", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

app = api_app
