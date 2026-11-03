#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# -eq 2 ]] || { echo 'usage: run_recovery_r8.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r6/prepare.py
python3 tools/recovery_r8/run.py "$@"
