#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: bash tests/run_recovery_r19.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r19/audit.py "$1" "$2" | tee reports/recovery_r19/audit.log
python3 tools/recovery_r19/model.py | tee reports/recovery_r19/model.log
python3 tools/recovery_r19/run.py "$1" "$2" | tee reports/recovery_r19/arm-run.log
python3 tools/recovery_r19/verify.py | tee reports/recovery_r19/independent-verification.log
python3 tools/recovery_r19/seal.py
python3 tools/recovery_r19/verify.py --manifest
