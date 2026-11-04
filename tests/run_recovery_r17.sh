#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: bash tests/run_recovery_r17.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r17/audit.py "$1" "$2"
python3 tools/recovery_r17/model.py
python3 tools/recovery_r17/run.py "$1" "$2"
python3 tools/recovery_r17/verify.py
