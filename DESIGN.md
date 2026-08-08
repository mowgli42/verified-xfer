# DESIGN — Operator feedback (IxDF)

Source of truth for **how verified-xfer talks to people**.  
Most operators are lab technicians, not software engineers. The CLI *is* the UI.

## Voice

- Short sentences. Concrete nouns: folder, file, copy, check.
- Prefer “we could not find the config file” over “configuration resolution failed”.
- Always pair a failure with a next step after `→`.
- Never require reading the source code to know what happened.

## Status line grammar

```
HH:MM:SS | LEVEL   | TAG        | message  [key=value …]
```

| Tag | Meaning for operators |
|-----|------------------------|
| `INITIALIZATION` | Setup — config loaded, four folders shown, ready to copy |
| `CONFIG` | Which settings file is in use (path + source) |
| `FILE` | One local file we will copy (name, size, short hash) |
| `TRANSFER` | Copy in progress (arrow + destination path) |
| `VERIFY` | After-copy check (`OK` or `FAIL`) |
| `SUCCESS` | That file is done and confirmed |
| `FAIL` | Something blocked us — read the `→` hint |
| `SUMMARY` | Roll-up: how many files succeeded |
| `DRY-RUN` | Practice mode — nothing was written |
| `NEXT` | Optional plain-language “what to do now” |

## Non-technical defaults

1. **Say where we are** — print the config path before any copy.
2. **Say what moved** — each file gets TRANSFER + VERIFY, not a silent batch.
3. **Say what to do next** — FAIL lines end with `→ …`; SUMMARY can add `NEXT | …`.
4. **Avoid jargon in user-facing text** — keep SHA-256 (needed for trust) but explain as “checksum / fingerprint”.
5. **No silent success** — even a one-file run ends with SUMMARY.

## Visual / CLI atmosphere

- Monospace status stream; no spinner libraries; no TUI frameworks (Ponytail).
- Realtime stdout (unbuffered friendly: `python -u` if a host buffers).
- Redacted secrets in CONFIG lines.

## Agent rule

Cursor agents MUST follow `.cursor/rules/ixdf-operator-feedback.mdc` when changing
log copy, README operator sections, or TROUBLESHOOTING recovery text.
Ponytail still governs *how much* code to write; this file governs *how we speak*.
