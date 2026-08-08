# Beads — verified-xfer

Atomic units from `openspec/changes/initial/tasks.md`.  
CLI database: `bd ready` / `bd list` (prefix `vx-`). Epic: `vx-0t0`.

Ponytail: each bead is the smallest shippable slice. IxDF: status feedback stays loud and plain.

## Done

### B1 — Project skeleton & Ponytail rule ✅ `vx-0t0.1`
- Package layout, `pyproject.toml`, `config.example.yaml`, health/ponytail rules

### B2 — Config loader (multi-location + system-wide) ✅ `vx-0t0.2`
- Search order: explicit → cwd → user → system-wide (`%PROGRAMDATA%` / `/etc`)
- `--show-config-paths`; CONFIG log lines; redacted secrets

### B3 — IxDF-style logger ✅ `vx-0t0.3`
- `ixdf_log.Status`: preflight / file / transfer / verify / success / fail / summary

### B4 — Hash & size helpers ✅ `vx-0t0.4`
- stdlib SHA-256 + size

### B5 — LocalBackend ✅ `vx-0t0.5`
- pathlib / shutil for mounted shares

### B6 — SFTPBackend ✅ `vx-0t0.6`
- paramiko optional extra; hash via temporary get

### B7 — Stage command ✅ `vx-0t0.7`
- Pre-flight, transfer, verify, dry-run, overwrite protection

### B8 — Retrieve command ✅ `vx-0t0.8`
- Reverse of stage: `results_dir` → `retrieve_to`

### B9 — CLI entry point ✅ `vx-0t0.9`
- `python -m verified_xfer stage|retrieve`

### B10 — Smoke tests & example ✅ `vx-0t0.10`
- `tests/test_local_stage_retrieve.py`, `examples/local-demo.sh`

## Done this pass (docs / design framework)

### B11 — OpenSpec archive readiness ✅ `vx-0t0.11`
- Gherkin under `openspec/specs/file-staging/spec.md`
- README health UX order (summary → capture → diagrams → remaining)
- Completion notes in tasks.md

### B12 — Operator feedback (non-technical IxDF) ✅ `vx-0t0.12`
- `DESIGN.md` + `.cursor/rules/ixdf-operator-feedback.mdc`
- Plain-language NEXT / FAIL hints for lab operators

## Out of scope (YAGNI)

Watching for test completion, parallel bulk transfers, encryption beyond SFTP,
Windows service wrappers, GUI, database.
