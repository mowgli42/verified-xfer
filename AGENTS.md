# Agent notes

This repo follows **OpenSpec (behaviour-driven) → Beads → code**.

1. Read `openspec/specs/file-staging/spec.md` (Gherkin is the acceptance contract).
2. Read `openspec/changes/initial/tasks.md` for the ordered work items.
3. After `bd init`, convert tasks into Beads issues and drive implementation with `bd ready`.
4. Obey `.cursor/rules/ponytail.mdc` – keep the Python small and the status feedback loud.
5. Logging style is intentional: IxDF visibility-of-system-status. Do not silence the PRE-FLIGHT / TRANSFER / VERIFY / SUCCESS / SUMMARY lines.

When adding behaviour, update the Gherkin first, then the tasks, then the code.
