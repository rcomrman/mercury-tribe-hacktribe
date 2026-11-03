#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'Usage: bash tests/run_recovery_r11.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p reports/recovery_r11
python3 tools/recovery_r11/run.py "$1" "$2" > reports/recovery_r11/validation.log
python3 tools/recovery_r11/audit.py "$1" "$2" > reports/recovery_r11/audit.log
python3 tools/recovery_r11/verify.py
