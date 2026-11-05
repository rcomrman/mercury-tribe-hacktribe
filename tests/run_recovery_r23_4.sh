#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r23_4.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r23_4/run.py "$1" "$2"
python3 tools/recovery_r23_4/verify.py
python3 tools/recovery_r23_3/verify.py
python3 tools/recovery_r23_2/verify.py
