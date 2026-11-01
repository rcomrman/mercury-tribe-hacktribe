#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
clang -DMD31_HOST_TEST -std=c99 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -Isrc src/*.c tests/test_md43_portability.c -o build/test_md43_portability
ASAN_OPTIONS=detect_leaks=1 build/test_md43_portability
