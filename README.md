# verified-xfer

Upload test files from a **local folder** to a **Linux folder**, then pull **logs/results** from a **different Linux folder** back to a local folder — with a check on every file.

The config names four folders:

| Key | Role |
|-----|------|
| `source_dir` | Local folder to upload from |
| `staging_dir` | Linux folder that receives the upload |
| `results_dir` | Linux folder for log/result data (must differ from `staging_dir`) |
| `retrieve_to` | Local folder where retrieved logs/results are saved |

Built for lab operators: each step prints plain status (`INITIALIZATION` → `TRANSFER` → `VERIFY` → `SUCCESS` / `FAIL` → `SUMMARY` → `NEXT`) so you always know what happened and what to do next. No GUI, no daemon — one small Python CLI.

## CLI session capture

From `examples/local-demo.sh` (full log: [docs/images/cli-demo.txt](docs/images/cli-demo.txt)):

```text
=== STAGE ===
INITIALIZATION | 2 file(s) to upload
FILE       | meta.txt  size=8  checksum=1afd1b403a9a…
TRANSFER   | → …/staging/meta.txt
VERIFY     | OK   size=8 checksum=1afd1b403a9a…
SUCCESS    | meta.txt copied and checked at …/staging/meta.txt
SUMMARY    | OK  2/2 files staged
NEXT       | All 2 file(s) staged. Safe to continue.

=== RETRIEVE ===
SUMMARY    | OK  2/2 files retrieved
NEXT       | All 2 file(s) retrieved. Safe to continue.
```

## Architecture

```mermaid
flowchart LR
  subgraph Windows_or_Linux["Operator machine"]
    SRC[source_dir<br/>local upload]
    RET[retrieve_to<br/>local retrieve]
    CLI[verified-xfer CLI]
  end
  subgraph Share["Linux share / SFTP host"]
    STG[staging_dir<br/>linux upload]
    RES[results_dir<br/>linux logs]
  end
  SRC -->|stage + verify| CLI
  CLI -->|copy + checksum| STG
  RES -->|retrieve + verify| CLI
  CLI --> RET
```

- **local** backend — NFS / SMB / CIFS already mounted (or same machine).
- **sftp** backend — true remote host via paramiko (optional install).

## Sequence — stage then retrieve

```mermaid
sequenceDiagram
  actor Op as Operator
  participant CLI as verified-xfer
  participant Share as Staging / results folders
  Op->>CLI: stage
  CLI->>CLI: Load config (print CONFIG path)
  CLI->>CLI: Hash each local file
  CLI->>Share: Copy file
  CLI->>Share: Recheck size + checksum
  CLI-->>Op: SUCCESS / FAIL + NEXT
  Note over Op: External test runs (out of scope)
  Op->>CLI: retrieve
  CLI->>Share: List results_dir (logs, separate from staging)
  CLI->>Op: Copy into retrieve_to + verify
  CLI-->>Op: SUMMARY + NEXT
```

## Remaining / planned

| Item | Tracking |
|------|----------|
| Automated SFTP backend test (mocked or lab host) | [#2](https://github.com/mowgli42/verified-xfer/issues/2) |
| Watch-for-test-complete / GUI / service wrappers | Out of scope (YAGNI) |

Initial epic beads B1–B12 are done — see [BEADS.md](BEADS.md).

Process: OpenSpec + Gherkin → Beads (`bd ready`) → Ponytail-minimal code.  
See [BEADS.md](BEADS.md), [openspec/specs/file-staging/spec.md](openspec/specs/file-staging/spec.md), [DESIGN.md](DESIGN.md).

## Quick start

### Windows (PowerShell or Command Prompt)

```powershell
pip install -e ".[sftp]"   # or: pip install -e .

copy config.example.yaml config.yaml
# edit the four folder paths in config.yaml

# Wrapper (finds py/python automatically; unbuffered status lines)
.\examples\verified-xfer.ps1 stage --show-config-paths
.\examples\verified-xfer.ps1 stage --dry-run
.\examples\verified-xfer.ps1 stage
# … run your external test …
.\examples\verified-xfer.ps1 retrieve

# Same via cmd.exe:
examples\verified-xfer.bat stage --dry-run

# Local four-folder demo (no real share needed):
.\examples\local-demo.ps1
examples\local-demo.bat
```

### Linux / macOS

```bash
pip install -e ".[sftp]"   # or: pip install -e .   (local/NFS only)

# Option A – config in the current folder
cp config.example.yaml config.yaml
# edit the four folder paths

python -m verified_xfer stage --show-config-paths   # where we look
python -m verified_xfer stage --dry-run             # practice, no writes
python -m verified_xfer stage                       # copy + check inputs
# … run your external test …
python -m verified_xfer retrieve                    # pull results + logs

bash examples/local-demo.sh
```

Lab-wide Windows config (admin once): copy `config.example.yaml` to `%PROGRAMDATA%\verified-xfer\config.yaml`.

If a terminal buffers output: `python -u -m verified_xfer …` (the `.bat` / `.ps1` wrappers already set `PYTHONUNBUFFERED=1`).

## Config search order

First existing file wins. The chosen path is always printed under `CONFIG | …`.

1. `--config` / `-c`
2. `./config.yaml`
3. User — `%APPDATA%\verified-xfer\` (Windows) or `~/.config/verified-xfer/`
4. System-wide — `%PROGRAMDATA%\verified-xfer\` (Windows) or `/etc/verified-xfer/`

Passwords are hidden in the log; key paths are shown.

## Troubleshooting

**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — config discovery, permissions, SFTP auth, checksum mismatches, overwrite protection, empty results — each with recovery steps.

## Repo layout

```
openspec/specs/file-staging/   # Gherkin acceptance contract
openspec/changes/initial/      # proposal, design, tasks
beads via bd (vx-*) + BEADS.md
src/verified_xfer/             # minimal implementation
examples/verified-xfer.ps1|.bat  # Windows wrappers
examples/local-demo.ps1|.bat|.sh # four-folder local demos
.cursor/rules/                 # ponytail + ixdf-operator-feedback + repo-health
.cursor/skills/                # Repo Health Loop fix-lane skills
DESIGN.md                      # operator feedback voice (IxDF)
```

## License

MIT — keep it simple.
