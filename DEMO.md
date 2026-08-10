# DEMO — verified-xfer (graham-bell)

Three surfaces, one core: **CLI** (lab), **local FastAPI UI** (lab), **Vercel static demo** (remote review).

## 1. CLI (primary operator path)

```bash
pip install -e ".[sftp]"
cp config.example.yaml config.yaml   # or use %PROGRAMDATA%\verified-xfer\config.yaml

python -m verified_xfer stage --dry-run
python -m verified_xfer stage
python -m verified_xfer retrieve
```

Windows helpers: `examples/local-demo.ps1`, `examples/local-demo.bat`.

Sample successful logs: `docs/sample-logs/`

## 2. Local web UI (scrolling live log)

```bash
pip install -e ".[web]"
# from repo root so static/ is found
python -m verified_xfer.web.app
# → http://127.0.0.1:8765
```

Or: `verified-xfer-web` after install.

**What you see**
- Left: action (stage / retrieve), dry-run, force, optional config path
- Right: live scrolling log with the same IxDF status lines as the CLI
- Status pill: idle → running → success / failed

**Happy-path exercise (< 2 min)**
1. Point `config.yaml` at a local temp pair of folders (or use the demo script).
2. Open the UI, leave Dry-run checked, click Run.
3. Watch INITIALIZATION → FILE → TRANSFER → SUMMARY stream into the log.
4. Uncheck dry-run and run a real stage against a local backend folder.

Screenshot: `docs/demo/web-ui-stage.png`

## 3. Vercel public demo (sample-log replay)

Real SFTP/NFS cannot run on a static host. The Vercel site under `demo/` replays the same IxDF lines from `demo/samples.js` for remote / low-attention review.

```bash
# local preview of the static demo
npx serve demo   # or: python -m http.server -d demo 4173

# deploy (from repo root; needs Vercel auth)
npx vercel --yes
npx vercel --prod --yes
```

Health check: `GET /api/health` → `{ "status": "ok", "service": "verified-xfer-demo" }`

Screenshot: `docs/demo/vercel-demo-replay.png`  
Refresh screenshots: `NODE_PATH=~/node_modules node scripts/capture-demo-screenshots.mjs`

## Tests (no network)

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

## Graham-bell artifacts checklist

| Artifact | Location |
|----------|----------|
| Working demo | CLI + `http://127.0.0.1:8765` + Vercel `demo/` |
| Sample logs | `docs/sample-logs/` |
| Screenshots | `docs/demo/*.png` |
| OpenSpec + Gherkin | `openspec/specs/file-staging/spec.md` (+ web-ui change) |
| Production beads | `BEADS.md` / `openspec/changes/web-ui/` |
| Learnings | `LEARNINGS.md` |
