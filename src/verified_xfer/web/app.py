"""FastAPI local web UI — select action, Run, watch scrolling log.

Graham-bell trade-off:
  Chose SSE streaming of status lines over a job queue + WebSocket.
  Default path loads system/cwd config automatically (no path typing).
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from verified_xfer.config import format_config_summary, load_config, validate_folders
from verified_xfer.core import retrieve, stage
from verified_xfer.ixdf_log import Status, setup_logging

app = FastAPI(title="verified-xfer", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class RunRequest(BaseModel):
    command: str = Field(..., pattern="^(stage|retrieve)$")
    dry_run: bool = False
    force: bool = False
    config_path: str | None = None


def _config_snapshot(config_path: str | None = None) -> dict[str, Any]:
    cfg, cfg_path, source_label = load_config(config_path)
    if not cfg:
        return {"ok": False, "error": "no config file found", "path": None, "lines": []}
    err = validate_folders(cfg)
    if err:
        return {"ok": False, "error": err, "path": str(cfg_path), "lines": []}
    lines = format_config_summary(cfg, cfg_path, source_label)
    return {
        "ok": True,
        "error": None,
        "path": str(cfg_path),
        "source": source_label,
        "lines": lines,
    }


def _run_transfer(req: RunRequest, line_q: queue.Queue) -> int:
    log = setup_logging(verbose=False)

    def on_line(msg: str) -> None:
        line_q.put({"type": "line", "text": msg})

    status = Status(log, on_line=on_line)

    cfg, cfg_path, source_label = load_config(req.config_path)
    if not cfg:
        status.fail(
            "no config file found",
            "copy config.example.yaml to ./config.yaml — see TROUBLESHOOTING.md",
        )
        line_q.put({"type": "done", "rc": 1})
        return 1

    status.initialization("config ready — four folders")
    for line in format_config_summary(cfg, cfg_path, source_label):
        status.info(f"  CONFIG | {line}")

    folder_err = validate_folders(cfg)
    if folder_err:
        status.fail(folder_err, "fix config.example.yaml four-folder section")
        line_q.put({"type": "done", "rc": 1})
        return 1

    if req.command == "stage":
        rc = stage(cfg, status, dry_run=req.dry_run, force=req.force)
    else:
        rc = retrieve(cfg, status, dry_run=req.dry_run)

    line_q.put({"type": "done", "rc": rc})
    return rc


async def _sse_stream(req: RunRequest) -> AsyncIterator[str]:
    line_q: queue.Queue = queue.Queue()
    thread = threading.Thread(target=_run_transfer, args=(req, line_q), daemon=True)
    thread.start()

    yield f"data: {json.dumps({'type': 'start', 'command': req.command})}\n\n"

    while True:
        try:
            item = line_q.get(timeout=0.15)
        except queue.Empty:
            if not thread.is_alive():
                while True:
                    try:
                        item = line_q.get_nowait()
                    except queue.Empty:
                        break
                    yield f"data: {json.dumps(item)}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'rc': -1})}\n\n"
                break
            await asyncio.sleep(0.05)
            continue

        yield f"data: {json.dumps(item)}\n\n"
        if item.get("type") == "done":
            break

    thread.join(timeout=2)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_path = STATIC_DIR / "index.html"
    if html_path.is_file():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse(
        "<h1>verified-xfer</h1><p>static/index.html missing — see DEMO.md</p>",
        status_code=500,
    )


@app.get("/api/ready")
async def ready() -> dict[str, Any]:
    """Startup check: is the default config present and valid?"""
    return _config_snapshot(None)


@app.post("/api/run")
async def run_transfer(req: RunRequest) -> StreamingResponse:
    return StreamingResponse(
        _sse_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "verified-xfer"}


def main() -> None:
    from verified_xfer.cli import launch_web

    raise SystemExit(launch_web())


if __name__ == "__main__":
    main()
