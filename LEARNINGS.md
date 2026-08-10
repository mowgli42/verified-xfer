# Learnings — graham-bell web + CLI slice

## What we tried / chose

1. **Log delivery to the browser**  
   - Tried conceptually: WebSocket job channel, polling a log file, SSE from the request itself.  
   - **Chose SSE on POST `/api/run`** with a background thread + `queue.Queue`.  
   - Why: one process, no Redis, lines appear as they are produced, same `Status` object as CLI.  
   - Failure avoided: buffering the entire run then dumping it (would break the “scrolling live” requirement).

2. **Status dual-sink**  
   - Adding `on_line` + `lines[]` to `Status` kept core.py unchanged.  
   - Alternative: logging.Handler subclass only. Callback is clearer for SSE and unit tests.

3. **UI complexity**  
   - Rejected Streamlit (log pane control is awkward) and a separate SPA.  
   - Single dark HTML page + vanilla JS is enough for an operator UI and stays in one repo folder.

4. **Config on the web**  
   - Same multi-location loader as CLI. Optional override path in the form.  
   - Do not invent a second config schema for the UI.

## What still hurts (honest)

- FastAPI + real SFTP will block the worker thread for the duration of large transfers; fine for lab files, not for multi-GB concurrent jobs.  
- No auth on the local web UI — acceptable only because bind is `127.0.0.1`.  
- Static path resolution depends on running from the editable install / repo layout.  
- **Vercel cannot run real transfers** — chose a static sample-log replay (`demo/`) instead of pretending serverless can mount NFS. Trade-off documented in DEMO.md.

## Vercel slice

- Tried: ship FastAPI to Vercel serverless.  
- **Chose:** static `demo/` + `api/health.js` + replay of `docs/sample-logs` lines.  
- Why: graham-bell remote review needs screenshots + clickable status stream without lab shares.  
- Failure avoided: a broken “Run” button that 500s on every Vercel invoke.

## Validated by this slice

- CLI stage/retrieve with IxDF lines (already green).  
- Web dry-run and real local-backend stage/retrieve stream the same lines into a scrolling pane.  
- Tests still pass with the extended `Status` signature.
