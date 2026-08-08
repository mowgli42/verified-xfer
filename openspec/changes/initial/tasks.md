# Tasks – initial implementation

Convert each item below into a Beads issue (`bd create … --parent <epic>`).  
Dependencies are expressed so `bd ready` yields a safe sequence.

**Status: complete** (2026-08-08). Epic `workspace-dhk` in Beads; tasks 1–10 closed; task 11 closed after Gherkin spec + test coverage audit.

## Epic: verified-xfer-initial

### 1. Project skeleton & Ponytail rule ✅
- Create package layout, `pyproject.toml`, `config.example.yaml`, `.cursor/rules/ponytail.mdc`.
- Add minimal `README` already present.
- **Beads tag**: setup
- **Done**: `src/verified_xfer/`, `pyproject.toml`, `config.example.yaml`, `.cursor/rules/ponytail.mdc`, `README.md`

### 2. Config loader (multi-location + system-wide) ✅
- Search order: explicit → cwd → user (%APPDATA% / XDG) → system-wide (%PROGRAMDATA% on Windows, /etc on Linux).
- Parse YAML, validate required keys, resolve paths, select backend.
- Always log the effective config source + redacted summary (IxDF visibility).
- `--show-config-paths` diagnostic.
- Fail with clear message on missing/invalid config.
- **Depends on**: 1
- **Done**: `src/verified_xfer/config.py`, CLI wiring in `cli.py`

### 3. IxDF-style logger ✅
- Custom formatter + helpers (`preflight`, `transfer`, `verify`, `success`, `fail`, `summary`).
- Always include concrete paths / sizes / short hashes.
- **Depends on**: 1
- **Done**: `src/verified_xfer/ixdf_log.py`

### 4. Hash & size helpers (stdlib) ✅
- `file_sha256(path) -> str`, `file_size(path) -> int`.
- Used by both backends and verification.
- **Depends on**: 1
- **Done**: `src/verified_xfer/hashutil.py`

### 5. LocalBackend ✅
- Implement the Backend protocol with pathlib / shutil.
- `ensure_dir`, `put`, `get`, `list_dir`, `size`, `sha256`.
- **Depends on**: 4
- **Done**: `LocalBackend` in `src/verified_xfer/backends.py`

### 6. SFTPBackend (optional extra) ✅
- paramiko implementation of the same protocol.
- Simple hash via temporary get + local hash for v1.
- **Depends on**: 4
- **Blocks**: only needed when config.backend == "sftp"
- **Done**: `SFTPBackend` in `src/verified_xfer/backends.py` (requires `pip install verified-xfer[sftp]`)

### 7. Stage command ✅
- Pre-flight list + hashes.
- Ensure remote dir.
- Transfer + verify each file.
- Summary + non-zero exit on any failure.
- Honour `--dry-run` and `--force`.
- **Depends on**: 2, 3, 5 (and 6 if SFTP)
- **Done**: `stage()` in `src/verified_xfer/core.py`

### 8. Retrieve command ✅
- Mirror of stage but reverse direction, using `results_dir` → `retrieve_to`.
- **Depends on**: 2, 3, 5 (and 6)
- **Done**: `retrieve()` in `src/verified_xfer/core.py`

### 9. CLI entry point ✅
- `python -m verified_xfer stage|retrieve [--config] [--dry-run] [--force] [--strict]`
- **Depends on**: 7, 8
- **Done**: `src/verified_xfer/cli.py`, `__main__.py`, console script in `pyproject.toml`

### 10. Smoke tests & example ✅
- Temp-dir LocalBackend tests that mirror the Gherkin “Successful stage” and “Successful retrieve” scenarios.
- `examples/local-demo.yaml` + short shell script.
- **Depends on**: 9
- **Done**: `tests/test_local_stage_retrieve.py`, `tests/test_cli.py`, `examples/local-demo.yaml`, `examples/local-demo.sh`

### 11. OpenSpec archive readiness ✅
- Confirm all Gherkin scenarios have corresponding tests or clear manual verification steps.
- Update this tasks.md with completion notes.
- **Depends on**: 10
- **Done**: Gherkin spec at `openspec/specs/file-staging/spec.md`. Coverage:

| Gherkin scenario | Verification |
|------------------|--------------|
| Successful stage | `test_stage_and_retrieve_roundtrip` |
| Successful retrieve | `test_stage_and_retrieve_roundtrip` |
| Stage dry-run writes nothing | `test_dry_run_writes_nothing` |
| Retrieve dry-run writes nothing | `test_retrieve_dry_run_writes_nothing` |
| Stage refuses overwrite without force | `test_stage_refuses_overwrite_without_force` |
| Config not found | `test_config_not_found` (CLI subprocess) |
| Show config paths | `test_show_config_paths` (CLI subprocess) |
| Empty source directory | `test_empty_source_dir` |
| Empty results directory | `test_empty_results_dir` |

SFTP backend: manual verification with a lab host (`backend: sftp` in config); no automated SFTP test in v0.1 (YAGNI).

---

**Beads creation** (after `bd init`):

```bash
bd init --skip-agents --non-interactive
# Epic and tasks created as workspace-dhk … workspace-dhk.11
bd ready   # shows workspace-dhk.11 when task 10 was still open
```
