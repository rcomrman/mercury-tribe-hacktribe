#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# -eq 2 ]] || { echo 'usage: run_recovery_r9.sh custom.VSB backup.VSB' >&2; exit 2; }
# Only R9 experiments run; R6–R8 archives are checked without replaying them.
python3 tools/recovery_r9/audit.py "$@"
python3 tools/recovery_r9/run.py "$@"
python3 tools/recovery_r9/models.py
clang -O2 -Wall -Wextra -Werror -fsanitize=undefined -fno-sanitize-recover=all -Isrc src/lcd_source_mux.c tests/recovery_r9/mux_contract.c -o build/recovery_r9/mux_contract_host
build/recovery_r9/mux_contract_host > reports/recovery_r9/mux_contract.log
cat reports/recovery_r9/mux_contract.log
python3 tools/recovery_r9/layout.py
python3 tools/recovery_r9/visualize.py
python3 tools/recovery_r9/verify.py
