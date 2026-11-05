#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r26.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r26/run.py "$1" "$2"
python3 tools/recovery_r26/verify.py
python3 tools/recovery_r26/visual.py
python3 tools/recovery_r23_4/verify.py
