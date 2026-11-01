#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -ne 2 ]]; then
  echo "Usage: bash tests/run_merged_v29_4.sh /path/custom.VSB /path/backup.VSB"
  exit 2
fi
bash tests/run_v29_3.sh "$1" "$2"
python3 - <<'PYR'
import json
r=json.load(open('rapport_audit.json'))
for f in r['firmwares']:
 print(f['name'], f['passed'], '/', f['total'], f['sha256'])
PYR
echo 'MERGED V29.4: HOST + static only. NOT FLASHABLE.'
