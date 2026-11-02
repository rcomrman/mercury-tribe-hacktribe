#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash tests/run_recovery_r2.sh "$@"
python3 tools/recovery_r3/run.py "$@"
