#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r23_2.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r23_2/run.py "$1" "$2"
python3 tools/recovery_r23_2/verify.py
python3 tools/recovery_r23_1/verify_worker.py
python3 tools/recovery_r21/verify.py "$1" "$2" --manifest
