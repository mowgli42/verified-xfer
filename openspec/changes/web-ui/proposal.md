# Proposal: Local FastAPI web UI with live scrolling log

## Why

Lab operators who prefer a browser over a terminal still need the same verified stage/retrieve flow and the same visible status feedback. A local web surface also makes demos easier to show on a shared machine.

## What (prototype scope)

- FastAPI app bound to 127.0.0.1
- Single-page UI: choose stage/retrieve, dry-run, force
- Live scrolling log fed by the same IxDF `Status` lines as the CLI (SSE)
- Reuses existing config discovery and core transfer logic

## Out of scope (capture as beads)

- Authentication / multi-user sessions
- Durable job history
- Hosting beyond localhost
- Uploading files through the browser (config still points at folders)

## Success

- `python -m verified_xfer.web.app` serves UI; dry-run stage shows live lines
- Gherkin scenarios for web marked Validated vs Future
- Production rebuild path listed in beads
