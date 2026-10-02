# verified-xfer

Verified stage + retrieve of test files between a local folder and a Linux share (local mount or SFTP), with a checksum on every file.
Stack: Python CLI (`src/verified_xfer`), optional FastAPI web (`verified-xfer web`), static Vercel replay in `demo/`. Not Svelte — operator tool, exception is intentional.
Posture: ponytail (repo created 2026-08-08, older than 30 days). Shared health pack is `.cursor/skills/` and `.cursor/rules/` — follow those for `[Health]` work.

## Commands

- Install: `pip install -e ".[dev,web]"` (add `,[sftp]` only if touching the SFTP backend)
- Interactive: `verified-xfer` (menu) or `verified-xfer web` (http://127.0.0.1:8765)
- One-shot: `verified-xfer stage` / `verified-xfer retrieve` / `verified-xfer stage --dry-run`
- Local four-folder practice: `examples/local-demo.sh` (Windows: `examples/local-demo.bat` or `.ps1`)
- Test one file: `pytest tests/test_local_stage_retrieve.py -q`
- Test all: `pytest tests/ -q`
- Secrets: `bash scripts/scan-secrets.sh .`
- Demo evidence: `DEMO.md`, `docs/demo/*.png`, `docs/sample-logs/`. Public URL `https://verified-xfer.vercel.app` is currently 404 (see issue #8).

No lint or typecheck command is configured. Do not invent one.

## Hard prohibitions

- Do not commit private keys, `*-key.pem`, `*.key`, `.env` secrets, or `BEGIN … PRIVATE KEY`. Generate locally; gitignore them. Public certs may stay.
- Do not set `staging_dir` equal to `results_dir`. Upload landing and log folder stay distinct.
- Do not silence `INITIALIZATION` / `CONFIG` / `TRANSFER` / `VERIFY` / `SUCCESS` / `FAIL` / `SUMMARY` / `NEXT`. On FAIL, print a `NEXT` line with a `→` recovery step (`DESIGN.md`).
- Do not add a watch-for-complete service, GUI shell, or extra framework. Capture it as a bead instead.
- Do not invent SFTP hosts, routes, or env vars that are not in `config.example.yaml` or the CLI.
- Do not rewrite OpenSpec / Gherkin to match a hoped-for future. Update them only when code already changed.

## Verify by change type

| Change | Check |
| --- | --- |
| CLI stage/retrieve | `pytest tests/test_local_stage_retrieve.py -q` and a sample log still matches `docs/sample-logs/` |
| Interactive menu | `pytest tests/test_cli_interactive.py -q` |
| SFTP backend | `pytest tests/test_sftp_backend.py -q` (mocked; do not require a lab host) |
| Web UI | `verified-xfer web` and `docs/demo/web-ui-stage.png` still describes the screen |
| Spec | `openspec/specs/file-staging/spec.md` still matches the code you changed |
| Deploy | `https://verified-xfer.vercel.app` and `/api/health` return 200 (currently open: #8) |
| Secrets | `bash scripts/scan-secrets.sh .` passes |

## Source of truth

- Behavior: `openspec/specs/file-staging/spec.md` (Gherkin is the contract)
- Remaining work: Beads (`bd ready`, epic `vx-0t0`) and GitHub issues; see `BEADS.md`
- Operator voice: `DESIGN.md` and `.cursor/rules/ixdf-operator-feedback.mdc`
- Demo evidence: `DEMO.md`

## House vocabulary

- stage — copy `source_dir` → `staging_dir` and recheck size + checksum. Do not say upload-job or sync.
- retrieve — copy `results_dir` → `retrieve_to` and recheck. Do not say download-job.
- The four folders are `source_dir`, `staging_dir`, `results_dir`, `retrieve_to`. Do not collapse them.
- Status lines are `INITIALIZATION`, `TRANSFER`, `VERIFY`, `SUCCESS` / `FAIL`, `SUMMARY`, `NEXT`. Do not replace them with a progress bar or log-level names.

## Good / bad

Bad: a checksum mismatch that only raises and exits.
Good: `FAIL` plus `NEXT | →` telling the operator what to fix (see `DESIGN.md`).

## Borrowed patterns

- hard-prohibition — apache/airflow via ossrules.md (never-hedge rules for keys, folder split, status lines)
- verification-matrix — apache/airflow via ossrules.md (CLI vs SFTP vs web vs spec)
- single-source — browser-use/browser-use via ossrules.md (Gherkin and Beads stay authoritative)
- house-vocabulary — apache/airflow via ossrules.md (stage/retrieve and the four folder keys)
