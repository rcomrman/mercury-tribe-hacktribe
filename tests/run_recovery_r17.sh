#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: bash tests/run_recovery_r17.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r17/audit.py "$1" "$2" | tee reports/recovery_r17/audit.log
python3 tools/recovery_r17/model.py | tee reports/recovery_r17/model.log
python3 tools/recovery_r17/run.py "$1" "$2" | tee reports/recovery_r17/arm-run.log
python3 tools/recovery_r17/verify.py | tee reports/recovery_r17/independent-verification.log
python3 tools/recovery_r17/seal.py
python3 tools/recovery_r17/verify.py --manifest
