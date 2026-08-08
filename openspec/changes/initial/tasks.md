# Tasks – initial implementation

Convert each item below into a Beads issue (`bd create … --epic verified-xfer-initial`).  
Dependencies are expressed so `bd ready` yields a safe sequence.

## Epic: verified-xfer-initial

### 1. Project skeleton & Ponytail rule
- Create package layout, `pyproject.toml`, `config.example.yaml`, `.cursor/rules/ponytail.mdc`.
- Add minimal `README` already present.
- **Beads tag**: setup

### 2. Config loader (multi-location + system-wide)
- Search order: explicit → cwd → user (%APPDATA% / XDG) → system-wide (%PROGRAMDATA% on Windows, /etc on Linux).
- Parse YAML, validate required keys, resolve paths, select backend.
- Always log the effective config source + redacted summary (IxDF visibility).
- `--show-config-paths` diagnostic.
- Fail with clear message on missing/invalid config.
- **Depends on**: 1

### 3. IxDF-style logger
- Custom formatter + helpers (`preflight`, `transfer`, `verify`, `success`, `fail`, `summary`).
- Always include concrete paths / sizes / short hashes.
- **Depends on**: 1

### 4. Hash & size helpers (stdlib)
- `file_sha256(path) -> str`, `file_size(path) -> int`.
- Used by both backends and verification.
- **Depends on**: 1

### 5. LocalBackend
- Implement the Backend protocol with pathlib / shutil.
- `ensure_dir`, `put`, `get`, `list_dir`, `size`, `sha256`.
- **Depends on**: 4

### 6. SFTPBackend (optional extra)
- paramiko implementation of the same protocol.
- Simple hash via temporary get + local hash for v1.
- **Depends on**: 4
- **Blocks**: only needed when config.backend == "sftp"

### 7. Stage command
- Pre-flight list + hashes.
- Ensure remote dir.
- Transfer + verify each file.
- Summary + non-zero exit on any failure.
- Honour `--dry-run` and `--force`.
- **Depends on**: 2, 3, 5 (and 6 if SFTP)

### 8. Retrieve command
- Mirror of stage but reverse direction, using `results_dir` → `retrieve_to`.
- **Depends on**: 2, 3, 5 (and 6)

### 9. CLI entry point
- `python -m verified_xfer stage|retrieve [--config] [--dry-run] [--force] [--strict]`
- **Depends on**: 7, 8

### 10. Smoke tests & example
- Temp-dir LocalBackend tests that mirror the Gherkin “Successful stage” and “Successful retrieve” scenarios.
- `examples/local-demo.yaml` + short shell script.
- **Depends on**: 9

### 11. OpenSpec archive readiness
- Confirm all Gherkin scenarios have corresponding tests or clear manual verification steps.
- Update this tasks.md with completion notes.
- **Depends on**: 10

### 12. Operator feedback (non-technical IxDF)
- `DESIGN.md` voice rules + `.cursor/rules/ixdf-operator-feedback.mdc`.
- Plain-language FAIL / NEXT lines for lab operators.
- **Depends on**: 3

---

## Completion notes (2026-08-08)

| # | Status | Evidence |
|---|--------|----------|
| 1–10 | Done | Package, config discovery, IxDF logger, backends, stage/retrieve, CLI, `tests/test_local_stage_retrieve.py`, `examples/local-demo.sh` |
| 11 | Done (this pass) | `openspec/specs/file-staging/spec.md`, README health UX order, design.md, BEADS.md |
| 12 | Done (this pass) | `DESIGN.md`, `ixdf-operator-feedback.mdc`, NEXT lines + softened FAIL copy |

Beads epic: `vx-0t0` (`bd ready` / `BEADS.md`).
