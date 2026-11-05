#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."; mkdir -p reports/recovery_r23
python3 tools/recovery_r23/audit.py "$1" "$2" | tee reports/recovery_r23/audit.log
python3 tools/recovery_r23/model.py | tee reports/recovery_r23/model.log
python3 tools/recovery_r21/verify.py "$1" "$2" --manifest | tee reports/recovery_r23/r21-regression.log
