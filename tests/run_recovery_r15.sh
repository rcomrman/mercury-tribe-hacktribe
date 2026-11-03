#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'Usage: bash tests/run_recovery_r15.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p build/recovery_r15 reports/recovery_r15
python3 tools/recovery_r15/run.py "$1" "$2" > reports/recovery_r15/validation.log
python3 tools/recovery_r15/audit.py "$1" "$2" > reports/recovery_r15/audit.log
python3 tools/recovery_r15/models.py > reports/recovery_r15/models.log
python3 tools/recovery_r15/verify.py
