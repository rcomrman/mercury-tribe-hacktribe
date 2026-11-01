#!/usr/bin/env python3
"""Read-only VSB code-cave & callback literal audit. NO PATCH, NO OUTPUT VSB.
Caution: FF in file does not prove runtime RAM safety. No flash guarantee.
"""
import hashlib,json,struct,sys
from pathlib import Path
HEAD=0x100
BASE=0xC0000000
IMAGE=0x200000
PTR=0xC002A970
ORIG=0xC002A71C
CORE_START=0xC01D0000
CORE_END=0xC01D8004 # conservative ARM payload extent; prefer V29.4 ELF-derived audit
BRIDGE_START=0xC01E0000
BRIDGE_END=0xC01E0014

def inspect(p):
 b=Path(p).read_bytes()
 assert len(b)==HEAD+IMAGE,f'not 2MiB+header: {p}'
 off=lambda a:HEAD+a-BASE
 assert struct.unpack_from('<I',b,off(PTR))[0]==ORIG,f'callback pointer drift: {p}'
 for start,end in ((CORE_START,CORE_END),(BRIDGE_START,BRIDGE_END)):
  assert b[off(start):off(end)]==b'\xff'*(end-start),f'nonempty candidate: {p}'
 return {'file':Path(p).name,'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),
         'original_callback':hex(ORIG),'pointer_slot':hex(PTR),
         'core_filled_FF':True,'bridge_filled_FF':True,
         'RAM_free_at_runtime_proven':False,'safe_to_flash':False}
if __name__=='__main__':
 assert len(sys.argv)>=3,'usage: script IMAGE1.VSB IMAGE2.VSB (read-only)'
 print(json.dumps([inspect(p) for p in sys.argv[1:]],indent=2,ensure_ascii=False))
