#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 2 ]] || { echo 'usage: run_recovery_r25.sh custom.VSB backup.VSB' >&2; exit 2; }
python3 tools/recovery_r25/run.py "$1" "$2"
python3 tools/recovery_r25/verify.py
clang -std=c99 -O2 -Isrc tests/recovery_r25/cadence.c src/md15_bridge.c src/md21_v14_profiles.c src/mercury_live.c src/mercury_events.c src/mercury_glitch.c src/lcd_source_mux.c src/mercury_keys.c src/mini_lfo4.c -o build/recovery_r25/cadence
build/recovery_r25/cadence
python3 tools/recovery_r25/visual.py
python3 tools/recovery_r23_4/verify.py
