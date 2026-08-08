# verified-xfer

**Simple, heavily verified file staging + retrieval between Windows local storage and a Linux shared folder (SFTP / NFS mount / local path).**

Designed for test workflows:

1. Stage input data & config into a known remote folder.
2. Run the system under test (external).
3. Retrieve results + logs from a separate remote folder.
4. Confirm every file landed where expected, with hashes and explicit status feedback.

Follows **Ponytail minimalism**, OpenSpec + Gherkin behaviour specs, and Beads-style sequential development. Logging and CLI feedback follow IxDF / Nielsen visibility-of-system-status principles: always tell the operator what is happening, what just succeeded or failed, and what the next safe action is.

## Quick start

```bash
# install (stdlib + one optional dep)
pip install -e ".[sftp]"   # or just: pip install pyyaml paramiko

# Option A – local config in the current directory
cp config.example.yaml config.yaml
# edit config.yaml

# Option B – system-wide config on a Windows lab machine (admin once)
#   mkdir "%PROGRAMDATA%\verified-xfer"
#   copy config.example.yaml "%PROGRAMDATA%\verified-xfer\config.yaml"
#   (then every operator on the machine picks it up automatically)

# see which config file will be used
python -m verified_xfer stage --show-config-paths

# dry-run staging (no writes) – realtime status on stdout
python -m verified_xfer stage --dry-run

# real stage with verification
python -m verified_xfer stage

# after test finishes
python -m verified_xfer retrieve
```

## Config search order

The tool checks these locations **in order** and uses the first file that exists.  
The chosen source and full path are always printed in the log under `CONFIG | …`.

1. `--config / -c` (explicit path)
2. `./config.yaml` (current working directory)
3. **User**
   - Windows: `%APPDATA%\verified-xfer\config.yaml`
   - Linux/macOS: `~/.config/verified-xfer/config.yaml`
4. **System-wide** (recommended for shared lab PCs)
   - Windows: `%PROGRAMDATA%\verified-xfer\config.yaml`
   - Linux: `/etc/verified-xfer/config.yaml`

Passwords are redacted in the log; key paths are shown.

## Real-time output

All status lines (`PRE-FLIGHT`, `CONFIG`, `FILE`, `TRANSFER`, `VERIFY`, `SUCCESS`, `FAIL`, `SUMMARY`) are written immediately to **stdout**.  
Cursor, terminals, and CI see the live stream with no extra flags.  
If a particular environment buffers, use `python -u -m verified_xfer …`.

## Design goals

- **Lots of verification** – existence, size, SHA-256 before and after; remote listing confirmation; clear failure messages.
- **Right folder guarantee** – target path is checked; files are only considered “placed” after remote confirmation.
- **Separate retrieve path** – results/logs live in a different remote directory from the staging input.
- **Simple Python** – pathlib, hashlib, logging; paramiko only when SFTP is required. NFS is just a mounted local path.
- **IxDF-style feedback** – every step announces status, progress, and outcome so the operator never has to guess.
- **System-wide config** – one machine-wide YAML for the whole lab, still overridable per user or per run.

## Troubleshooting

See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for the full catalogue of failure modes (config discovery, permissions, SFTP auth, hash mismatches, overwrite protection, empty results, etc.) with concrete recovery steps.

## Repo layout

```
openspec/                 # source of truth for behaviour
  specs/file-staging/     # Gherkin scenarios + requirements
  changes/initial/        # proposal, design, tasks
src/verified_xfer/        # minimal implementation
.cursor/rules/ponytail.mdc
config.example.yaml
TROUBLESHOOTING.md
```

See `openspec/changes/initial/proposal.md` and `tasks.md` for the development sequence (OpenSpec → Beads-ready tasks). Cursor can continue from the remaining Beads tasks.

## Supported backends

| Backend | When to use | Notes |
|---------|-------------|-------|
| `local` | NFS / SMB / CIFS already mounted, or same machine | Uses `pathlib` + `shutil`. Fastest verification. |
| `sftp`  | True remote Linux host | paramiko. Hash verification by temporary re-download. |

## License

MIT – keep it simple.
