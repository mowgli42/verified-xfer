# File staging & retrieval

Verified stage of test input files to a remote directory, and retrieve of results/logs from a separate remote directory. Every step emits IxDF-style status (PRE-FLIGHT, TRANSFER, VERIFY, SUCCESS, FAIL, SUMMARY).

## Requirements

### Config discovery

The tool SHALL search for configuration in this order and use the first existing file:

1. explicit `--config` / `-c` path
2. `./config.yaml` in the current working directory
3. user config (`%APPDATA%\verified-xfer\config.yaml` on Windows, `~/.config/verified-xfer/config.yaml` elsewhere)
4. system-wide config (`%PROGRAMDATA%\verified-xfer\config.yaml` on Windows, `/etc/verified-xfer/config.yaml` on Linux)

The tool SHALL log the effective config source, path, backend, and directory keys (with SFTP secrets redacted).

The tool SHALL provide `--show-config-paths` to list the search order and whether each candidate exists.

### Stage

The `stage` command SHALL:

- list files in `source_dir` (non-recursive, files only)
- log each file's size and SHA-256 before transfer
- ensure the remote `staging_dir` exists
- copy each file to `staging_dir/<filename>`
- verify remote size and SHA-256 match the source
- emit a SUMMARY line with success count
- exit non-zero if any file fails

With `--dry-run`, no files SHALL be written; the tool SHALL still pre-flight and log what would happen.

With `--force`, existing remote files MAY be overwritten; without it, an existing remote file SHALL fail with a clear message.

### Retrieve

The `retrieve` command SHALL:

- list files in `results_dir` (non-recursive)
- download each file to `retrieve_to/<filename>`
- verify local size matches remote size
- emit a SUMMARY line with success count
- exit non-zero if any file fails

With `--dry-run`, no files SHALL be written.

### Backends

- `local`: treat remote paths as ordinary filesystem paths (NFS/SMB mount or same host).
- `sftp`: transfer via paramiko; hash verification by temporary download.

---

```gherkin
Feature: Verified file staging and retrieval

  Background:
    Given a valid config with backend "local"
    And source_dir contains test input files
    And staging_dir, results_dir, and retrieve_to are writable paths

  Scenario: Successful stage
    When I run "stage" without dry-run
    Then every file from source_dir appears in staging_dir
    And each staged file has matching size and SHA-256
    And the log contains PRE-FLIGHT, FILE, TRANSFER, VERIFY, SUCCESS, and SUMMARY lines
    And the process exits with code 0

  Scenario: Successful retrieve
    Given results_dir contains output files from a completed test
    When I run "retrieve" without dry-run
    Then every file from results_dir appears in retrieve_to
    And each retrieved file has matching size
    And the log contains PRE-FLIGHT, TRANSFER, VERIFY, SUCCESS, and SUMMARY lines
    And the process exits with code 0

  Scenario: Stage dry-run writes nothing
    When I run "stage" with --dry-run
    Then staging_dir remains empty
    And the log mentions dry-run
    And the process exits with code 0

  Scenario: Retrieve dry-run writes nothing
    Given results_dir contains output files
    When I run "retrieve" with --dry-run
    Then retrieve_to remains empty or unchanged
    And the log mentions dry-run
    And the process exits with code 0

  Scenario: Stage refuses overwrite without force
    Given a file already exists in staging_dir with the same name as a source file
    When I run "stage" without --force
    Then that file is not overwritten
    And the log contains a FAIL line suggesting --force
    And the process exits with code 1

  Scenario: Config not found
    Given no config file exists in any search location
    When I run any command
    Then the log contains a FAIL line about missing config
    And the process exits with code 1

  Scenario: Show config paths
    When I run with --show-config-paths
    Then the log lists every candidate path and whether it exists
    And the process exits with code 0

  Scenario: Empty source directory
    Given source_dir exists but contains no files
    When I run "stage"
    Then no files are transferred
    And the process exits with code 0

  Scenario: Empty results directory
    Given results_dir exists but contains no files
    When I run "retrieve"
    Then no files are downloaded
    And the process exits with code 0
```
