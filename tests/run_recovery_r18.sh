#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: bash tests/run_recovery_r18.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r18/audit.py "$1" "$2" | tee reports/recovery_r18/audit.log
python3 tools/recovery_r18/model.py | tee reports/recovery_r18/model.log
python3 tools/recovery_r18/run.py "$1" "$2" | tee reports/recovery_r18/arm-run.log
python3 tools/recovery_r18/verify.py | tee reports/recovery_r18/independent-verification.log
python3 tools/recovery_r18/seal.py
python3 tools/recovery_r18/verify.py --manifest
