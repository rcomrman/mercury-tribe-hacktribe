#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/arm reports
SRC=(src/*.c)
clang -std=c99 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -Isrc "${SRC[@]}" tests/test_md30_lab.c -o build/test_md30_lab
ASAN_OPTIONS=detect_leaks=1 build/test_md30_lab
clang -std=c99 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -Isrc "${SRC[@]}" tests/test_v28_global.c -o build/test_v28_global
ASAN_OPTIONS=detect_leaks=1 build/test_v28_global
OBJECTS=()
for f in src/*.c src/*.S; do
 n="$(basename "${f%.*}")"
 clang --target=armv5te-none-eabi -mcpu=arm926ej-s -mfloat-abi=soft -std=c99 -Os -ffreestanding -fno-builtin -fno-unwind-tables -fno-asynchronous-unwind-tables -Wall -Wextra -Werror -Isrc -c "$f" -o "build/arm/$n.o"
 OBJECTS+=("build/arm/$n.o")
done
ld.lld -flavor gnu -m armelf -T src/md30_lab_layout.ld -o build/arm/md30_RESEARCH_ONLY.elf "${OBJECTS[@]}"
readelf -S build/arm/md30_RESEARCH_ONLY.elf > reports/arm_sections.txt
llvm-objdump -d -j .md30_callback build/arm/md30_RESEARCH_ONLY.elf > reports/arm_callback_disasm.txt
nm -u build/arm/md30_RESEARCH_ONLY.elf > reports/unresolved_symbols.txt
test ! -s reports/unresolved_symbols.txt
if grep -q ' \.bss ' reports/arm_sections.txt; then echo 'unexpected .bss'; exit 1;fi
python3 tools/md30_static_gate_check.py build/arm/md30_RESEARCH_ONLY.elf reports/arm_callback_disasm.txt
printf 'V29.1: host ASAN+UBSAN + ARM link + callback disassembly PASS; NOT FLASHABLE\n'
