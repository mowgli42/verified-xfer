# DEMO — verified-xfer (graham-bell prototype)

Two surfaces, one core.

## 1. CLI (primary operator path)

```bash
pip install -e ".[sftp]"
cp config.example.yaml config.yaml   # or use %PROGRAMDATA%\\verified-xfer\\config.yaml

python -m verified_xfer stage --dry-run
python -m verified_xfer stage
python -m verified_xfer retrieve
```

Windows helpers: `examples/local-demo.ps1`, `examples/local-demo.bat`.

Sample successful log: `docs/sample-logs/cli-stage-ok.txt`

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

## Remote / low-attention review

Real SFTP/NFS cannot run on a static host. For off-machine review use:

- This `DEMO.md` + sample logs under `docs/sample-logs/`
- CLI transcript in `docs/images/cli-demo.txt` (if present)
- Screenshot the web UI after a dry-run and drop under `docs/demo/` when convenient

A production rebuild would host a job API + auth (see beads roadmap below).

## Tests (no network)

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

## Graham-bell artifacts checklist

| Artifact | Location |
|----------|----------|
| Working demo | CLI + `http://127.0.0.1:8765` |
| Sample logs | `docs/sample-logs/` |
| OpenSpec + Gherkin | `openspec/specs/file-staging/spec.md` (+ web scenarios) |
| Production beads | `BEADS.md` / `openspec/changes/web-ui/` |
| Learnings | `LEARNINGS.md` |
