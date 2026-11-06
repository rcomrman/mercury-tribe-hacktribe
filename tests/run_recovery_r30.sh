#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r30.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r30/audit.py "$1" "$2"
python3 tools/recovery_r30/verify.py "$1" "$2"
