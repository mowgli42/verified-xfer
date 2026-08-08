# Design – initial verified stage + retrieve

## Shape

One-shot Python CLI. No daemon, no database, no GUI.

```
config.yaml  →  CLI (stage | retrieve)  →  Backend (local | sftp)
                      ↓
                 IxDF status lines on stdout
```

## Key decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Language | Python 3.10+ | Available on lab Windows + Linux; stdlib covers most of the job |
| Config | YAML, multi-location | One machine-wide default for shared lab PCs (`%PROGRAMDATA%`) |
| Backends | `local` + `sftp` | NFS/SMB mounts look like paths; true remotes need paramiko |
| Verification | size + SHA-256 | Catches truncated / wrong-folder copies without exotic protocols |
| Feedback | Tagged stdout lines | Operators are not always technical — status must be obvious |
| Minimalism | Ponytail ladder | Prefer stdlib; paramiko only for SFTP |

## Operator model (non-technical)

1. Someone sets up `config.yaml` once (often system-wide).
2. Operator drops inputs into `source_dir`.
3. Operator runs `stage` — watches green SUCCESS / SUMMARY.
4. External test runs (out of scope).
5. Operator runs `retrieve` — results land under `retrieve_to`.
6. On FAIL, follow the `→` hint or open TROUBLESHOOTING.md.

## IxDF mapping

| IxDF / Nielsen idea | How we apply it |
|---------------------|-----------------|
| Visibility of system status | INITIALIZATION / TRANSFER / VERIFY / SUMMARY always printed |
| Four folders | local source → linux staging; linux results/logs → local retrieve (staging ≠ results) |
| Match the real world | Talk about folders and files, not “payloads” or “artifacts” |
| Error prevention | Overwrite protection unless `--force`; dry-run available |
| Help users recover | Every FAIL includes a next safe action |
| Recognition over recall | `--show-config-paths` lists where configs can live |

See also: [DESIGN.md](../../../DESIGN.md) (operator feedback voice).
