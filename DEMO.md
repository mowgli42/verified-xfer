# DEMO — verified-xfer (graham-bell)

## Operator loop (keep it this simple)

1. Put `config.yaml` where the tool looks (cwd / user / system-wide) — once.
2. Start:
   - Terminal: `verified-xfer`
   - Browser: `verified-xfer web` → http://127.0.0.1:8765
3. Select **Stage** or **Retrieve**.
4. Press Enter / click **Run**.
5. Watch the scrolling status log until SUMMARY / NEXT.

That is the whole happy path. Extra flags (`--dry-run`, `--force`, one-shot `stage`/`retrieve`) are for scripts and troubleshooting only.

## Surfaces

| Surface | Command | Notes |
|---------|---------|-------|
| Interactive CLI | `verified-xfer` | Default when config exists |
| Local web UI | `verified-xfer web` | Same select → Run → live log |
| Vercel demo | `demo/` | Sample-log replay only (no real shares) |
| One-shot | `verified-xfer stage` | Automation / CI |

Windows wrappers: `examples/verified-xfer.bat` / `.ps1` (pass no args for the menu).

Sample logs: `docs/sample-logs/`  
Screenshots: `docs/demo/*.png`  
Refresh screenshots: `NODE_PATH=~/node_modules node scripts/capture-demo-screenshots.mjs`

## Tests

```bash
pip install -e ".[dev,web]"
pytest tests/ -q
```

## Graham-bell checklist

| Artifact | Location |
|----------|----------|
| Working demo | CLI menu + web UI + Vercel `demo/` |
| Sample logs | `docs/sample-logs/` |
| Screenshots | `docs/demo/*.png` |
| OpenSpec | `openspec/specs/file-staging/spec.md` |
| Learnings | `LEARNINGS.md` |
