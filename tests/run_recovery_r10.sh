#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# -eq 2 ]] || { echo 'usage: run_recovery_r10.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r10/audit.py "$@"
python3 tools/recovery_r10/run.py "$@"
python3 tools/recovery_r10/verify.py
