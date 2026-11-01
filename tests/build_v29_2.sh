#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/arm reports
SRC=(src/*.c)
for test in test_md30_lab test_v28_global test_md31_buttons_lcd test_md32_timeout_restore test_md39_keymap test_md40_rearm_barrier test_md41_restore_ack test_md42_spi_failure_gap test_md44_native_pending_reentry; do
 clang -DMD31_HOST_TEST -std=c99 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -Isrc "${SRC[@]}" "tests/$test.c" -o "build/$test"
 ASAN_OPTIONS=detect_leaks=1 "build/$test"
done
OBJECTS=()
for f in src/*.c src/*.S; do
 n="$(basename "${f%.*}")"
 clang --target=armv5te-none-eabi -mcpu=arm926ej-s -mfloat-abi=soft -std=c99 -Os -ffreestanding -fno-builtin -fno-unwind-tables -fno-asynchronous-unwind-tables -Wall -Wextra -Werror -Isrc -c "$f" -o "build/arm/$n.o"
 OBJECTS+=("build/arm/$n.o")
done
ld.lld -flavor gnu -m armelf -T src/md30_lab_layout.ld -o build/arm/md31_RESEARCH_ONLY.elf "${OBJECTS[@]}"
readelf -S build/arm/md31_RESEARCH_ONLY.elf > reports/arm_sections.txt
llvm-objdump -d -j .md30_callback build/arm/md31_RESEARCH_ONLY.elf > reports/arm_callback_disasm.txt
llvm-objdump -d build/arm/md31_RESEARCH_ONLY.elf | grep -A4 -E '<md31_compare_veneer>:' > reports/arm_compare_disasm.txt || true
nm -u build/arm/md31_RESEARCH_ONLY.elf > reports/unresolved_symbols.txt
test ! -s reports/unresolved_symbols.txt
if grep -q ' \.bss ' reports/arm_sections.txt; then echo 'unexpected .bss'; exit 1;fi
python3 tools/md30_static_gate_check.py build/arm/md31_RESEARCH_ONLY.elf reports/arm_callback_disasm.txt
printf 'V29.2: buttons + LCD comparator + fallback + ARM independent build PASS; NON FLASHABLE\n'
