#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r23_1.sh custom.VSB backup.VSB' >&2; exit 2; }
mkdir -p reports/recovery_r23_1
python3 tools/recovery_r23_1/audit.py "$1" "$2"
python3 tools/recovery_r21/audit.py "$1" "$2" >/dev/null
for span in '0xc0015a60 0xc0015b50' '0xc0015dd0 0xc0015fa0' '0xc0015fa0 0xc00162a8' '0xc0015cdc 0xc0015dd0' '0xc00836e4 0xc0083714'; do
 read -r begin end <<< "$span"
 llvm-objdump -D --start-address="$begin" --stop-address="$end" build/recovery_r21/STATIC_ONLY.elf
done > reports/recovery_r23_1/lcd-disassembly.txt
python3 tools/recovery_r23_1/experiments.py
python3 tools/recovery_r23_1/adversarial.py
python3 tools/recovery_r23_1/worker_run.py "$1" "$2"
python3 tools/recovery_r23_1/verify_worker.py
python3 tests/recovery_r23_1/test_model.py
python3 tests/recovery_r23_1/mutations.py
python3 tools/recovery_r21/verify.py "$1" "$2" --manifest
