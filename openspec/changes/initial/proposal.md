# Proposal: Initial verified stage + retrieve

## Why

Operators copy test data from a Windows workstation into a shared folder on a Linux system (SFTP or NFS mount), then later pull results and logs from a different folder. Manual copies are error-prone: wrong directory, incomplete transfer, silent failures, no audit trail.

We need a single, boring tool that:

- stages files with explicit verification that they landed in the *correct* remote directory,
- retrieves results/logs from a separate remote directory after the test run,
- makes every step’s status visible (IxDF visibility-of-system-status),
- stays simple enough that the code itself is trustworthy.

## What (scope)

- Config-driven source local path, staging target, retrieve source.
- Two commands: `stage` and `retrieve`.
- Backends: `local` (mounted share) and `sftp`.
- Pre- and post-transfer verification (existence, size, SHA-256).
- Dry-run mode.
- Structured, human-readable logging that always answers “what is happening / what just happened / did it succeed?”.
- System-wide Windows config support (`%PROGRAMDATA%\\verified-xfer\\config.yaml`).
- No GUI, no daemon, no database. One-shot CLI.

## Out of scope (YAGNI)

- Watching for test completion (caller decides when to retrieve).
- Parallel transfers of thousands of files.
- Encryption beyond what SFTP already provides.
- Windows service / scheduled task wrappers.
- Full remote hash without re-transfer (optional future).

## Success criteria

- Gherkin scenarios in the behaviour-driven spec stay green.
- An operator can stage → run external test → retrieve with confidence that every file is accounted for and logged.
- Code remains under a few hundred lines of readable Python.
