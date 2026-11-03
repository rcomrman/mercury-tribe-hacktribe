#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'Usage: bash tests/run_recovery_r14.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p build/recovery_r14 reports/recovery_r14
python3 tools/recovery_r14/run.py "$1" "$2" > reports/recovery_r14/validation.log
python3 tools/recovery_r14/run.py "$1" "$2" --recovery > reports/recovery_r14/recovery_validation.log
python3 tools/recovery_r14/audit.py "$1" "$2" > reports/recovery_r14/audit.log
python3 tools/recovery_r14/models.py > reports/recovery_r14/models.log
python3 tools/recovery_r14/verify.py
