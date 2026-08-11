# Agent notes

This repo follows **OpenSpec (behaviour-driven) → Beads → Ponytail code**, with **IxDF operator feedback** for non-technical lab users.

1. Read `openspec/specs/file-staging/spec.md` (Gherkin is the acceptance contract).
2. Read `BEADS.md` or run `bd ready` (epic `vx-0t0`).
3. Obey `.cursor/rules/ponytail.mdc` — smallest working change.
4. Obey `.cursor/rules/ixdf-operator-feedback.mdc` — status lines stay loud and plain; every FAIL has a `→` next step. See `DESIGN.md`.
5. Do not silence `INITIALIZATION` / `CONFIG` / `TRANSFER` / `VERIFY` / `SUCCESS` / `SUMMARY` / `NEXT`.
6. Config always names four folders: local `source_dir` → linux `staging_dir` (upload); linux `results_dir` (logs, separate) → local `retrieve_to`.
7. Default UX is interactive: `verified-xfer` (no args) or `verified-xfer web` — select action → run → scrolling log. Keep one-shot `stage`/`retrieve` for scripts.

When adding behaviour: update Gherkin first, then Beads, then code.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
