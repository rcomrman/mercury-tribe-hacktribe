#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -ne 2 ]]; then
  echo "Usage: bash tests/run_v29_3.sh /path/to/custom.VSB /path/to/backup.VSB"
  exit 2
fi
bash tests/build_v29_2.sh
python3 tools/v29_3_audit_readonly.py "$1" "$2" --elf build/arm/md31_RESEARCH_ONLY.elf > rapport_audit.json
python3 tests/test_v29_3_mutations.py "$1" build/arm/md31_RESEARCH_ONLY.elf
echo 'V29.4: read-only static checks + ARM build + native-restore tests PASS; NO HARDWARE VALIDATION'
