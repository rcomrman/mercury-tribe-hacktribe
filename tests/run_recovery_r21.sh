#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: bash tests/run_recovery_r21.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r21/audit.py "$1" "$2" | tee reports/recovery_r21/audit.log
python3 tools/recovery_r21/run.py "$1" "$2" | tee reports/recovery_r21/run.log
python3 tools/recovery_r21/verify.py "$1" "$2" | tee reports/recovery_r21/verification.log
