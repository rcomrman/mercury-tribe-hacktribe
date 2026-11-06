#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r27.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r27/capture.py "$1" "$2"
python3 tools/recovery_r27/verify.py
python3 tools/recovery_r26/verify.py
