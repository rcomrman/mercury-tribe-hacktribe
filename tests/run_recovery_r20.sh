#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: bash tests/run_recovery_r20.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r19/verify.py --manifest
python3 tools/recovery_r20/extra_audit.py "$1" "$2" | tee reports/recovery_r20/supplement-audit.log
python3 tools/recovery_r20/model.py | tee reports/recovery_r20/model.log
python3 tools/recovery_r20/run.py "$1" "$2" | tee reports/recovery_r20/arm-run.log
python3 tools/recovery_r20/verify.py | tee reports/recovery_r20/independent-verification.log
python3 tools/recovery_r20/seal.py
python3 tools/recovery_r20/verify.py --manifest
