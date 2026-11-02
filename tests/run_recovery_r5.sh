#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash tests/run_recovery_r4.sh "$@"
python3 tools/recovery_r5/run.py "$@"
