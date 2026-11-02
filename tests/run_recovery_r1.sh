#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -ne 2 ]]; then echo 'usage: bash tests/run_recovery_r1.sh custom.VSB backup.VSB' >&2; exit 2; fi
# Debian packages: clang lld llvm qemu-user python3-pil; or prepend an existing
# toolchain directory to PATH. No package download or instrument operation here.
for tool in clang ld.lld llvm-objdump qemu-arm python3; do command -v "$tool" >/dev/null; done
mkdir -p reports/recovery_r1
bash tests/run_md43_host.sh > reports/recovery_r1/md43.log 2>&1
bash tests/run_md44_host.sh > reports/recovery_r1/md44.log 2>&1
bash tests/run_merged_v29_4.sh "$@" > reports/recovery_r1/baseline.log 2>&1
cp reports/arm_callback_disasm.txt reports/recovery_r1/baseline_callback_disasm.txt
cp reports/arm_compare_disasm.txt reports/recovery_r1/baseline_compare_disasm.txt
sed -i '${/^$/d;}' reports/recovery_r1/baseline_compare_disasm.txt
cp reports/arm_sections.txt reports/recovery_r1/baseline_sections.txt
python3 tests/test_md31_audit_mutations.py "$1" > reports/recovery_r1/md31_mutations.log 2>&1
python3 md45_static_abi_audit.py build/arm/md31_RESEARCH_ONLY.elf --custom "$1" --backup "$2" --output reports/recovery_r1/md45_abi.json > reports/recovery_r1/md45.log
python3 tools/recovery_r1/run.py "$@" > reports/recovery_r1/validation.log 2>&1
cat reports/recovery_r1/validation.log
