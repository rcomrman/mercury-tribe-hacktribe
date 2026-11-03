#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'Usage: bash tests/run_recovery_r13.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p build/recovery_r13 reports/recovery_r13
python3 tools/recovery_r13/run.py "$1" "$2" > reports/recovery_r13/validation.log
python3 tools/recovery_r13/audit.py "$1" "$2" > reports/recovery_r13/audit.log
python3 tools/recovery_r13/models.py > reports/recovery_r13/models.log
python3 tools/recovery_r13/verify.py
