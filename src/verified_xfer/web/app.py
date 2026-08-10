"""FastAPI local web UI with live scrolling log.

Graham-bell trade-off:
  Chose SSE streaming of status lines over a job queue + WebSocket.
  Alternative: Redis/RQ + WebSocket for multi-user job history.
  Reason: zero extra deps, one process, demo works in <2 minutes.
  Revisit when: concurrent operators or durable job history → production bead.
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from verified_xfer.config import format_config_summary, load_config
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


def _run_transfer(req: RunRequest, line_q: queue.Queue) -> int:
    """Blocking worker: runs stage/retrieve and pushes each status line into line_q."""
    log = setup_logging(verbose=False)

    def on_line(msg: str) -> None:
        line_q.put({"type": "line", "text": msg})

    status = Status(log, on_line=on_line)

    cfg, cfg_path, source_label = load_config(req.config_path)
    if not cfg:
        status.fail(
            "no config file found",
            "copy config.example.yaml or set system-wide config — see TROUBLESHOOTING.md",
        )
        line_q.put({"type": "done", "rc": 1})
        return 1

    status.initialization("effective configuration")
    for line in format_config_summary(cfg, cfg_path, source_label):
        status.info(f"  CONFIG | {line}")

    required = ["source_dir", "staging_dir", "results_dir", "retrieve_to"]
    missing = [k for k in required if k not in cfg]
    if missing:
        status.fail(f"config missing keys: {missing}", "see config.example.yaml")
        line_q.put({"type": "done", "rc": 1})
        return 1

    if req.command == "stage":
        rc = stage(cfg, status, dry_run=req.dry_run, force=req.force)
    else:
        rc = retrieve(cfg, status, dry_run=req.dry_run)

    line_q.put({"type": "done", "rc": rc})
    return rc


async def _sse_stream(req: RunRequest) -> AsyncIterator[str]:
    """Yield SSE events while a background thread runs the transfer."""
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
    import uvicorn

    uvicorn.run(
        "verified_xfer.web.app:app",
        host="127.0.0.1",
        port=8765,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
