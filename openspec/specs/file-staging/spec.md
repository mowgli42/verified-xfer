# File staging & retrieve

## Purpose

Operators need to move test inputs onto a Linux share, run an external system under test, then pull results and logs back — with proof that every file landed in the right place.

Audience is often **lab operators who are not software engineers**. Status lines and errors must say what happened and what to do next in plain language.

## Requirements

### Requirement: Config discovery with visible source

The tool SHALL load YAML configuration from an ordered search path and SHALL always print which file was chosen.

#### Scenario: System-wide Windows lab config

- **GIVEN** no `--config` flag and no `./config.yaml`
- **AND** `%PROGRAMDATA%\verified-xfer\config.yaml` exists
- **WHEN** the operator runs `stage` or `retrieve`
- **THEN** the tool loads that system-wide file
- **AND** the log includes `CONFIG | source=…` and `CONFIG | path=…`

#### Scenario: Explicit config wins

- **GIVEN** `--config path\to\my.yaml` points at a valid file
- **WHEN** the operator runs any command
- **THEN** that file is used even if cwd / user / system configs also exist

#### Scenario: Missing config fails with recovery hint

- **GIVEN** no config file exists in the search order
- **WHEN** the operator runs `stage`
- **THEN** the tool exits non-zero
- **AND** the log includes `FAIL | no config file found` with a next-step hint

### Requirement: Verified stage

The tool SHALL copy every file from `source_dir` into `staging_dir`, then verify size and SHA-256 before reporting success.

#### Scenario: Successful stage

- **GIVEN** a valid config with `backend: local` and a non-empty `source_dir`
- **WHEN** the operator runs `stage`
- **THEN** each file appears under `staging_dir`
- **AND** each file emits `FILE`, `TRANSFER`, `VERIFY | OK`, and `SUCCESS` lines
- **AND** `SUMMARY` reports all files staged
- **AND** the exit code is 0

#### Scenario: Dry-run stage writes nothing

- **GIVEN** a valid config
- **WHEN** the operator runs `stage --dry-run`
- **THEN** no files are written to `staging_dir`
- **AND** the log shows what would transfer

#### Scenario: Overwrite protection

- **GIVEN** a remote file already exists at the staging path
- **AND** `--force` was not passed
- **WHEN** the operator runs `stage`
- **THEN** that file is not overwritten
- **AND** the log shows `FAIL | remote file already exists` with a `--force` hint

### Requirement: Verified retrieve

The tool SHALL copy every file from `results_dir` into `retrieve_to`, verifying size and SHA-256.

#### Scenario: Successful retrieve

- **GIVEN** `results_dir` contains result/log files after an external test
- **WHEN** the operator runs `retrieve`
- **THEN** each file appears under `retrieve_to`
- **AND** verification lines confirm size and hash
- **AND** the exit code is 0

### Requirement: IxDF operator feedback

Every important step SHALL announce status so a non-technical operator never has to guess.

#### Scenario: Live status stream

- **GIVEN** a stage or retrieve run
- **WHEN** work progresses
- **THEN** stdout shows tagged lines: `INITIALIZATION`, `CONFIG`, `FILE`, `TRANSFER`, `VERIFY`, `SUCCESS`/`FAIL`, `SUMMARY`
- **AND** failures include a plain-language next action (`→ …`)

#### Scenario: Four distinct folders in config

- **GIVEN** a config file
- **THEN** it specifies `source_dir` (local upload), `staging_dir` (linux upload destination), `results_dir` (linux logs/results), and `retrieve_to` (local retrieve)
- **AND** `staging_dir` and `results_dir` are different paths
- **WHEN** they are the same path
- **THEN** the tool exits non-zero with a clear FAIL hint

#### Scenario: Interactive menu with default config

- **GIVEN** a valid config is found via the normal search order
- **WHEN** the operator runs `verified-xfer` with no subcommand
- **THEN** the tool prints the effective four folders
- **AND** offers Stage / Retrieve / Quit
- **WHEN** the operator chooses Stage and presses Enter
- **THEN** the scrolling status stream shows INITIALIZATION through SUMMARY

#### Scenario: Web UI loads default config

- **GIVEN** a valid config is found
- **WHEN** the operator opens the local web UI
- **THEN** the page shows config ready without typing a path
- **AND** selecting Stage and clicking Run streams the same IxDF lines into the live log

### Requirement: SFTP backend

The optional `sftp` backend SHALL implement the same put/get/list/size/hash contract as `local`, using paramiko. Automated tests MAY mock the SFTP session (no live host required). Missing paramiko SHALL fail with an install hint.

#### Scenario: Mocked SFTP put/get verifies size and SHA-256

- **GIVEN** an SFTP backend with a mocked paramiko session
- **WHEN** a file is put to a remote staging path
- **THEN** get returns the same bytes
- **AND** size and SHA-256 match the source
- **AND** list_files names that file

#### Scenario: SFTP without paramiko

- **GIVEN** paramiko is not installed
- **WHEN** the operator selects `backend: sftp`
- **THEN** the tool exits with a message to `pip install 'verified-xfer[sftp]'`

