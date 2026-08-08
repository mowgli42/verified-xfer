#!/usr/bin/env bash
# Tiny end-to-end demo using LocalBackend and temporary directories.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO=$(mktemp -d)
echo "Demo root: $DEMO"

mkdir -p "$DEMO/source" "$DEMO/staging" "$DEMO/results" "$DEMO/retrieved"
echo "sample payload" > "$DEMO/source/payload.txt"
echo "run: 42" > "$DEMO/source/meta.txt"

cat > "$DEMO/config.yaml" <<CFG
backend: local
source_dir: $DEMO/source
staging_dir: $DEMO/staging
results_dir: $DEMO/results
retrieve_to: $DEMO/retrieved
CFG

PY="${PYTHON:-python3}"
echo "=== STAGE (dry-run) ==="
"$PY" -m verified_xfer stage -c "$DEMO/config.yaml" --dry-run

echo "=== STAGE ==="
"$PY" -m verified_xfer stage -c "$DEMO/config.yaml"

echo "=== Simulate test producing results ==="
echo "PASS" > "$DEMO/results/test.log"
echo "42" > "$DEMO/results/answer.txt"

echo "=== RETRIEVE ==="
"$PY" -m verified_xfer retrieve -c "$DEMO/config.yaml"

echo "=== Retrieved contents ==="
ls -l "$DEMO/retrieved"
cat "$DEMO/retrieved/test.log"

echo "Demo complete.  Temp dir left at $DEMO (remove manually)."
