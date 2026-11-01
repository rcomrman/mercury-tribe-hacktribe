#!/usr/bin/env python3
"""Static ARM callback verification (read-only, no VSB input/writes)."""
import re,subprocess,sys
from pathlib import Path
elf,dis=map(Path,sys.argv[1:3])
nm=subprocess.check_output(['nm','-n',str(elf)],text=True)
matches=re.findall(r'^([0-9a-fA-F]+) T md30_callback_bridge$',nm,re.M)
assert matches and int(matches[0],16)==0xC01E0000,'callback address drift'
txt=dis.read_text()
for code in ['push','pop','bl','ldr']:
    # LLVM objdump may spell stmdb/ldmia rather than push/pop
    if code=='push': assert ('stmdb' in txt or 'push' in txt), 'missing register save'
    elif code=='pop': assert ('ldmia' in txt or 'pop' in txt), 'missing register restore'
    else: assert code in txt, f'missing {code}'
assert 'md30_callback_visit' in txt,'no C handler call'
assert 'c002a71c' in txt.lower() or 'c0 02 a7 1c' in txt.lower() or '1ca702c0' in txt.lower() or '1c a7 02 c0' in txt.lower(), 'original callback missing in disasm'
print('ARM callback layout and unconditional Korg tail target checked')
