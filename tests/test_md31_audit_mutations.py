#!/usr/bin/env python3
"""Read-only negative tests, mutating copies in MEMORY, not VSB files."""
import importlib.util
from pathlib import Path
import subprocess,struct
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('md31_audit',root/'tools/md31_audit_lcd_path_readonly.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
elf=root/'build/arm/md31_RESEARCH_ONLY.elf'
sym=a.elf_symbols(elf)
p=Path('/mnt/data/firmware_input/user_custom.VSB')
if not p.exists():
 print('SKIP readonly supplied firmware not mounted')
 raise SystemExit(0)
base=p.read_bytes()
mutations=[
 ('comparator_callsite', a.COMPARE_CALL),
 ('lcd_callback_pointer', a.POINTER),
 ('opcode2_refresh_bit_store', 0xC0015E68),
 ('LCD descriptor literal', a.CALLBACK+16),
 ('unused core candidate', a.CORE_START+20),
 ('unused bridge candidate', a.BRIDGE_START+12),
]
for name,addr in mutations:
 b=bytearray(base)
 b[a.HEADER+addr-a.BASE]^=0x01
 try:
  a.assertions(b,sym['__md30_bridge_end'],sym['__md30_core_end'])
 except ValueError:
  continue
 raise AssertionError('Mutation NOT rejected: '+name)
print('V29.2 readonly audit rejects %d/%d mutated VSB byte patterns' % (len(mutations),len(mutations)))
