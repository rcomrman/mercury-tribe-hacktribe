#!/usr/bin/env python3
"""Fail-closed exact-insn + linker layout audit on supplied VSBs. NEVER patches.
USAGE: python tools/md31_audit_lcd_path_readonly.py <ARM ELF> <VSB1> <VSB2>
"""
from __future__ import annotations
import hashlib,json,struct,subprocess,sys
from pathlib import Path
BASE=0xC0000000
HEADER=0x100
IMG=0x200000
ORIG_COMPARE=0xC0015AB4
COMPARE_CALL=0xC0016084
LCD_DISPATCH=0xC0015DD0
CALLBACK=0xC002A71C
POINTER=0xC002A970
CORE_START=0xC01D0000
BRIDGE_START=0xC01E0000

def word(binary, addr):
    return struct.unpack_from('<I',binary,HEADER+addr-BASE)[0]

def bl_destination(addr,opcode):
    if (opcode>>24)&0xf not in (0xA,0xB):
        return None
    off=opcode&0x00ffffff
    if off&0x00800000:off-=0x01000000
    return (addr+8+(off<<2))&0xffffffff

def assertions(b,bridge_end,core_end):
    assert len(b)==HEADER+IMG, "Wrong VSB envelope size"
    checks={
       'comparator sole callsite BL at C0016084':bl_destination(COMPARE_CALL,word(b,COMPARE_CALL))==ORIG_COMPARE and ((word(b,COMPARE_CALL)>>24)&0xf)==0xB,
       'LCD callback address pointer stable':word(b,POINTER)==CALLBACK,
       'LCD callback loads descriptor':word(b,CALLBACK)==0xE59F0008,
       'LCD callback opcode 3':word(b,CALLBACK+4)==0xE3A01003,
       'LCD callback arg zero':word(b,CALLBACK+8)==0xE3A02000,
       'LCD callback tail calls dispatcher':bl_destination(CALLBACK+12,word(b,CALLBACK+12))==LCD_DISPATCH,
       'LCD descriptor literal':word(b,CALLBACK+16)==0xC031BB2C,
       'LCD opcode2 store byte 1 at descriptor+5':word(b,0xC0015E68)==0xE5C32005,
       'LCD opcode2 value is 1':word(b,0xC0015E64)==0xE3A02001,
       'CORE unoccupied in VSB image (not RAM proof)':all(v==0xff for v in b[HEADER+CORE_START-BASE:HEADER+core_end-BASE]),
       'callback bridge unoccupied in VSB image':all(v==0xff for v in b[HEADER+BRIDGE_START-BASE:HEADER+bridge_end-BASE])
    }
    if not all(checks.values()):
        raise ValueError('ASSERTION FAILED: '+', '.join(k for k,v in checks.items() if not v))
    return checks

def elf_symbols(path):
    s=subprocess.check_output(['nm','-n',str(path)],text=True)
    symbols={}
    for line in s.splitlines():
        words=line.split()
        if len(words)==3 and words[0].isalnum():symbols[words[2]]=int(words[0],16)
    required=['__md30_core_start','__md30_core_end','__md30_bridge_end',
              'md30_callback_bridge','md31_compare_veneer','md31_compare_visit']
    missing=[k for k in required if k not in symbols]
    if missing:raise ValueError('Missing symbols: '+repr(missing))
    assert symbols['__md30_core_start']==CORE_START
    assert CORE_START<=symbols['md31_compare_veneer']<symbols['__md30_core_end']<=BRIDGE_START
    assert symbols['md30_callback_bridge']==BRIDGE_START
    assert symbols['__md30_bridge_end']<=BRIDGE_START+0x1000
    return symbols

def main(argv):
    if len(argv)!=4:raise SystemExit(__doc__)
    elf,*paths=map(Path,argv[1:]);symbols=elf_symbols(elf)
    out={'lab_elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'lcd_compare_veneer':hex(symbols['md31_compare_veneer']),
         'core_end':hex(symbols['__md30_core_end']),
         'callback_bridge':hex(symbols['md30_callback_bridge']),
         'flashable':False,'hardware_safe_verified':False,'firmwares':[]}
    for p in paths:
        b=p.read_bytes()
        checks=assertions(b,symbols['__md30_bridge_end'],symbols['__md30_core_end'])
        out['firmwares'].append({'name':p.name,'sha256':hashlib.sha256(b).hexdigest(),
            'checks':checks,'passed':sum(checks.values()),'total':len(checks)})
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main(sys.argv)
