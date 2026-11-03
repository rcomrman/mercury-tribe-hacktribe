#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'Usage: bash tests/run_recovery_r12.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p build/recovery_r12 reports/recovery_r12
python3 tools/recovery_r12/run.py "$1" "$2" > reports/recovery_r12/validation.log
python3 tools/recovery_r12/audit.py "$1" "$2" > reports/recovery_r12/audit.log
python3 tools/recovery_r12/models.py > reports/recovery_r12/models.log
python3 tools/recovery_r12/layout.py > reports/recovery_r12/layout.log
python3 tools/recovery_r12/verify.py
