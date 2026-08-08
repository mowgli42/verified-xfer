# Troubleshooting Guide – verified-xfer

When something goes wrong, the tool prints a `FAIL | … → …` line.  
The text after `→` is the next thing to try. Use this guide when you need more detail.

Written for lab operators: start with the symptom you see on screen, then follow the Fix.

---

## 1. Config not found / wrong config used

**Symptoms**
```
FAIL | no config file found  → copy config.example.yaml to one of the locations…
```
or the tool silently uses a different config than the one you edited.

**Diagnosis**
```bash
python -m verified_xfer stage --show-config-paths
```
This prints the exact search order and which files exist.

**Search order (first hit wins)**
1. `--config / explicit path`
2. `./config.yaml` (current working directory)
3. **User**  
   - Windows: `%APPDATA%\verified-xfer\config.yaml`  
   - Linux/macOS: `~/.config/verified-xfer/config.yaml`
4. **System-wide (machine)**  
   - Windows: `%PROGRAMDATA%\verified-xfer\config.yaml`  ← intended for lab-wide defaults  
   - Linux: `/etc/verified-xfer/config.yaml`

**Fixes**
- Place a machine-wide default in `%PROGRAMDATA%\verified-xfer\config.yaml` (requires admin once).
- Override per-run with `-c path\to\my-config.yaml`.
- The log always prints `CONFIG | source=…` and `CONFIG | path=…` so you can see which file was chosen.

---

## 2. Missing required keys

**Symptoms**
```
FAIL | config missing keys: ['source_dir', …]  → see config.example.yaml
```

**Fix**  
Copy from `config.example.yaml` and fill every required field:
- `source_dir`, `staging_dir`, `results_dir`, `retrieve_to`
- when `backend: sftp` also `sftp.host`, `sftp.username`, and either `key_filename` or `password`.

---

## 3. source_dir does not exist or is empty

**Symptoms**
```
FAIL | source_dir does not exist or is not a directory: D:\…  → check config.source_dir
PRE-FLIGHT | no files found in source_dir
```

**Common Windows causes**
- Path written with single backslashes in YAML without quotes → YAML interprets `\t` etc.
  Use forward slashes or doubled backslashes, or a quoted raw path:
  ```yaml
  source_dir: "D:/testdata/run-42"
  # or
  source_dir: "D:\\testdata\\run-42"
  ```
- Running from a different drive / elevated vs non-elevated context so the path is invisible.
- The directory exists but contains only sub-folders (tool only stages files, not recursive trees in v0.1).

---

## 4. Permission / access denied on local or mounted share

**Symptoms**
```
FAIL | transfer/verify error for foo.bin: [WinError 5] Access is denied  → check permissions…
```

**Local / NFS / SMB mount**
- Confirm the mount is actually present: `dir \\server\share` or `ls /mnt/labshare`.
- Windows: the user running the tool must have write permission on the target folder.
- NFS: check `exportfs` / `/etc/exports` and that the client is allowed.

**SFTP**
- Key permissions: private key must be readable only by the current user (`icacls` / `chmod 600`).
- Account on the Linux side must be able to write the staging directory.

---

## 5. SFTP connection failures

**Symptoms**
```
FAIL | transfer/verify error …: Authentication failed.
FAIL | …: [Errno 110] Connection timed out
FAIL | …: No such file
```

**Checklist**
| Symptom | Likely cause | Action |
|---------|--------------|--------|
| Auth failed | Wrong key, passphrase-protected key, or password | Use `key_filename` pointing at an unencrypted key, or supply password (less preferred) |
| Connection timed out / refused | Firewall, wrong host/port, SSH not listening | `Test-NetConnection host -Port 22` (Windows) or `nc -zv host 22` |
| Host key / known_hosts | First connection or host key change | Tool currently uses AutoAddPolicy; for stricter environments change the backend |
| “No such file” on put | Parent directory missing and ensure_dir failed | Manually `mkdir -p` the staging path once, or fix permissions |

Install the optional dependency:
```bash
pip install "verified-xfer[sftp]"
```

---

## 6. Verification failures (size or hash mismatch)

**Symptoms**
```
VERIFY | FAIL size MISMATCH  hash OK
FAIL   | verification failed for payload.bin  → delete remote file and re-run stage
```

**Causes**
- File was partially written (network drop, disk full).
- Antivirus / endpoint protection rewrote or locked the file mid-copy.
- Two processes writing the same remote name concurrently.
- (Rare) different newline handling if a text file was edited in transit – prefer binary comparison via SHA-256.

**Recovery**
1. Delete the bad remote file.
2. Re-run `stage` (without `--force` it will refuse to overwrite, which is intentional).
3. If the problem repeats, try a different target path or switch from SFTP to a mounted share to isolate the transport.

---

## 7. “Remote file already exists”

**Symptoms**
```
FAIL | remote file already exists: /staging/foo.bin  → use --force to overwrite
```

**Intentional** – the tool refuses silent overwrites so you never lose a previous test’s inputs by accident.

**Fix**
- Move the old files aside, or
- `python -m verified_xfer stage --force …`

---

## 8. Retrieve finds zero files / wrong results folder

**Symptoms**
```
PRE-FLIGHT | zero files in results_dir – nothing to retrieve
SUMMARY    | OK  0/0 files retrieved
```

**Causes**
- The test wrote results somewhere else (check the actual path the system-under-test uses).
- Typo in `results_dir` (the log prints the exact path that was used).
- Permissions prevent listing the directory → earlier `FAIL | cannot list results_dir`.

---

## 9. Real-time output / Cursor / CI

The logger writes every status line to **stdout** immediately (no buffering tricks).  
When Cursor or another agent runs the command you will see the PRE-FLIGHT / TRANSFER / VERIFY / SUCCESS / SUMMARY stream in real time.

To force line buffering in some environments:
```bash
python -u -m verified_xfer stage -c config.yaml
```

---

## 10. Quick health-check sequence

```bash
# 1. See which config will be used
python -m verified_xfer stage --show-config-paths

# 2. Dry-run the stage (no writes)
python -m verified_xfer stage --dry-run

# 3. Real stage
python -m verified_xfer stage

# 4. After the external test finishes
python -m verified_xfer retrieve
```

If any step fails, the last `FAIL | … → …` line plus the matching section above should be enough to resolve it.

---

## Still stuck?

Open an issue on the repo with:
- the full console output (CONFIG lines + the FAIL line),
- `python -m verified_xfer stage --show-config-paths` output,
- Windows version / whether you are using a mounted share or pure SFTP.
