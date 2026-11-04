#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'Usage: bash tests/run_recovery_r16.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p build/recovery_r16 reports/recovery_r16
python3 tools/recovery_r16/run.py "$1" "$2" > reports/recovery_r16/validation.log
python3 tools/recovery_r16/audit.py "$1" "$2" > reports/recovery_r16/audit.log
python3 tools/recovery_r16/models.py > reports/recovery_r16/models.log
python3 tools/recovery_r16/verify.py
