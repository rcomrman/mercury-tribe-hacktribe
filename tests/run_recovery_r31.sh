#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/recovery_r31 reports/recovery_r31
python3 tools/recovery_r31/coverage.py
cc -std=c99 -O2 -Wall -Wextra -Wno-unused-function -Wno-misleading-indentation tests/recovery_r31/arbiter.c -o build/recovery_r31/arbiter
build/recovery_r31/arbiter
python3 tools/recovery_r31/verify.py
