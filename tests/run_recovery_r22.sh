#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports/recovery_r22
python3 tools/recovery_r22/model.py | tee reports/recovery_r22/model.log
python3 tools/recovery_r21/verify.py "$1" "$2" --manifest | tee reports/recovery_r22/r21-regression.log
