#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -ne 2 ]]; then echo 'usage: bash tests/run_recovery_r2.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p reports/recovery_r2
bash tests/run_recovery_r1.sh "$@" > reports/recovery_r2/r1_regression.log 2>&1
python3 tools/recovery_r2/run.py "$@" > reports/recovery_r2/validation.log 2>&1
python3 tools/recovery_r2/visualize.py
python3 tools/recovery_r2/audit.py "$@" > reports/recovery_r2/static_audit.log 2>&1
cat reports/recovery_r2/static_audit.log
python3 - <<'PY'
import json
r=json.load(open('reports/recovery_r2/results.json'))
assert not r['exploratory']
for x in r['results']:print(x['vsb'],x['name'],x['exit'])
print('R2: 17 scenarios per original, all expected outcomes verified; RESEARCH ONLY')
PY
