#!/usr/bin/env python3
"""Host-only; mutates in-memory copies, never VSB files or machine."""
import importlib.util
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',root/'tools/v29_3_audit_readonly.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
if len(sys.argv)!=3: raise SystemExit('Usage: python tests/test_v29_3_mutations.py <VSB> <lab-ARM-ELF>')
original=Path(sys.argv[1]).read_bytes()
elf=Path(sys.argv[2])
layout=m.layout_from_elf(elf)
assert m.audit_bytes(original,'valid.VSB',layout)['passed']==28

cases={
 'frame pointer':0xC0015A94,
 'shadow pointer':0xC0015B4C,
 'comparator BL':0xC0016084,
 'comparator memcpy':0xC0015B38,
 'callback literal':0xC002A970,
 'callback opcode':0xC002A720,
 'callback dispatcher':0xC002A728,
 'refresh flag':0xC0015E68,
 'callback tick':0xC002A810,
 'FF core target':layout['core_start']+0x20,
 'FF callback target':layout['callback_bridge_start'],
 'Inserted static pointer into payload':None,
 'Inserted static pointer into unused reservation':-1,
}
for title,where in cases.items():
    b=bytearray(original)
    if where is None or where==-1:
        # Invent a reference into either actual payload or reserved growth room.
        import struct
        target=layout['core_start']+0x100 if where is None else layout['core_end']+0x100
        struct.pack_into('<I',b,256+0x000FB730,target)
    else:
        i=256+where-m.BASE
        b[i]^=1
    try:m.audit_bytes(bytes(b),title,layout)
    except m.StaticAuditError: pass
    else:raise AssertionError('Modification not detected: '+title)
try:m.audit_bytes(original[:-1],'truncated.VSB',layout)
except m.StaticAuditError:pass
else:raise AssertionError('Truncated firmware not rejected')
print(f'V29.3 PASS: {len(cases)+1}/{len(cases)+1} independent static corruption tests caught (in RAM only)')
