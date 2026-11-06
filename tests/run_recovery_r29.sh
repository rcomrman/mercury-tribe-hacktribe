#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r29.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r29/run.py "$1" "$2"
python3 tools/recovery_r29/verify.py
python3 tools/recovery_r28/verify.py
