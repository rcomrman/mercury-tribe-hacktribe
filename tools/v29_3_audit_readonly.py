#!/usr/bin/env python3
"""Mercury Dust V29.3 — static audit, NEVER writes firmware.
Usage: python tools/v29_3_audit_readonly.py firmware1.VSB firmware2.VSB [--elf RESEARCH.elf]

Static evidence only. In particular NO proof of actual RAM usage, interrupt/task
context, LCD SPI timing, or physical button codes. Nothing here can make a
firmware safe to flash.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,subprocess
from pathlib import Path

BASE=0xC0000000
H=0x100
IMG=0x200000
CORE_START=0xC01D0000
BRIDGE_START=0xC01E0000
SHADOW=0xC031B310
KORG_FRAME=0xC031B710
DESC=0xC031BB2C

class StaticAuditError(RuntimeError): pass

def w(image:bytes,at:int)->int:
    if not(BASE<=at<=BASE+IMG-4):raise StaticAuditError(f'Address outside image: {at:#x}')
    return struct.unpack_from('<I',image,at-BASE)[0]

def branch_target(a:int,op:int):
    if (op>>25)&7 != 0b101:return None
    off=op&0xffffff
    if off&0x800000:off-=0x1000000
    return (a+8+(off<<2))&0xffffffff

def exact(image,at,value):return w(image,at)==value

def branches(image,at,to,link=True):
    op=w(image,at)
    return branch_target(at,op)==to and bool((op>>24)&1)==link

def layout_from_elf(elf:Path):
    s=subprocess.run(['nm','-n',str(elf)],capture_output=True,text=True,check=True).stdout
    syms={}
    for line in s.splitlines():
        v=line.split()
        if len(v)==3 and all(c in '0123456789abcdefABCDEF' for c in v[0]):
            syms[v[2]]=int(v[0],16)
    needed=['__md30_core_start','__md30_core_end','md30_callback_bridge',
            '__md30_bridge_end','md31_compare_veneer','md31_compare_visit']
    if any(k not in syms for k in needed):raise StaticAuditError('Missing ARM symbols')
    if syms['__md30_core_start']!=CORE_START or syms['md30_callback_bridge']!=BRIDGE_START:
        raise StaticAuditError('Linked entry addresses differ from audit')
    if not(CORE_START<syms['md31_compare_veneer']<syms['__md30_core_end']<=BRIDGE_START):
        raise StaticAuditError('ARM core layout/compare trampoline invalid')
    if not(BRIDGE_START<syms['__md30_bridge_end']<=BRIDGE_START+0x1000):
        raise StaticAuditError('ARM callback bridge overflow')
    readelf=subprocess.run(['readelf','-S',str(elf)],capture_output=True,text=True,check=True).stdout
    if '.bss ' in readelf:raise StaticAuditError('Unexpected BSS section')
    undefined=subprocess.run(['nm','-u',str(elf)],capture_output=True,text=True,check=True).stdout.strip()
    if undefined:raise StaticAuditError('Unresolved ARM symbols: '+undefined)
    return {
      'sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
      'core_start':CORE_START,'core_end':syms['__md30_core_end'],
      'callback_bridge_start':BRIDGE_START,'callback_bridge_end':syms['__md30_bridge_end'],
      'comparator_veneer':syms['md31_compare_veneer'],
      'bss_required':False,'external_symbols':0
    }

def audit_bytes(fw:bytes,filename:str,layout:dict):
    if len(fw)!=H+IMG:raise StaticAuditError(filename+': invalid VSB length')
    b=fw[H:]
    checks={
      'LCD framebuffer literal: C031B710':exact(b,0xC0015A94,KORG_FRAME),
      'LCD shadow literal: C031B310':exact(b,0xC0015B4C,SHADOW),
      'LCD framebuffer clear target: C031B710':exact(b,0xC0015A5C,KORG_FRAME),
      'LCD framebuffer page-index shift 7 (128 bytes)':exact(b,0xC0015A78,0xE1A02383),
      'LCD comparator entry ARM push':exact(b,0xC0015AB4,0xE92D4800),
      'Korg comparator BL C0016084->C0015AB4':branches(b,0xC0016084,0xC0015AB4),
      'Korg comparator return value tested':exact(b,0xC001608C,0xE3530000),
      'Original comparator shadow memcpy 128':branches(b,0xC0015B38,0xC000985C),
      'Original comparator shadow update size 128':exact(b,0xC0015B34,0xE3A02080),
      'Korg LCD page send call C00160A0':branches(b,0xC00160A0,0xC001613C),
      'Korg page loop 0..7':exact(b,0xC00160B4,0xE3530007),
      'Korg LCD frame driver descriptor C031BB2C':exact(b,0xC002A72C,DESC),
      'Callback pointer literal C002A970':exact(b,0xC002A970,0xC002A71C),
      'Callback opcode 3':exact(b,0xC002A720,0xE3A01003),
      'Callback opcode 3 tail dispatch':branches(b,0xC002A728,0xC0015DD0,link=False),
      'LCD dispatcher opcode 2 sets 1':exact(b,0xC0015E64,0xE3A02001),
      'LCD dispatcher opcode 2 stores flag at +5':exact(b,0xC0015E68,0xE5C32005),
      'LCD descriptor initialization stores count 20':exact(b,0xC002A8F8,0xE3A05014),
      'LCD callback engine tick decrements':exact(b,0xC002A7F4,0xE2433001),
      'LCD callback engine invokes function pointer':exact(b,0xC002A810,0xE12FFF33),
      'Korg shadow framebuffer non-overlapping':SHADOW+1024==KORG_FRAME,
      'LCD frame ends before descriptor':KORG_FRAME+1024<=DESC,
      'Core cave FF all bytes (file-only)':all(x==255 for x in b[CORE_START-BASE:layout['core_end']-BASE]),
      'Callback bridge cave FF all bytes (file-only)':all(x==255 for x in b[BRIDGE_START-BASE:layout['callback_bridge_end']-BASE]),
      'Core and callback cave do not overlap':layout['core_end']<=BRIDGE_START,
      'No static 32-bit literal into reserved region':not any(CORE_START <= struct.unpack_from('<I',b,idx)[0] < BRIDGE_START+0x1000 for idx in range(0,len(b)-3,4)),
      'Entire 64KiB+ bridge region FF':all(v==255 for v in b[CORE_START-BASE:BRIDGE_START+0x1000-BASE]),
      'ARM source not in Korg LCD runtime buffer':layout['callback_bridge_end']<=SHADOW,
    }
    if not all(checks.values()):raise StaticAuditError(filename+': FAILED '+', '.join(k for k,v in checks.items() if not v))
    ptrs=[]
    for idx in range(0,len(b),4):
        p=struct.unpack_from('<I',b,idx)[0]
        if CORE_START<=p<BRIDGE_START+0x1000:ptrs.append({'image_offset':hex(idx),'word_value':hex(p)})
    if ptrs:
        raise StaticAuditError(filename+': static literal collision in linked payload: '+str(ptrs[:3]))
    return {
       'name':filename, 'sha256':hashlib.sha256(fw).hexdigest(),
       'checks':checks,'passed':sum(checks.values()),'total':len(checks),
       'candidate_literal_words_into_cave':ptrs,
       'literal_words_may_be_unrelated_data':True,
       'lcd_frame':hex(KORG_FRAME),'lcd_shadow':hex(SHADOW),'lcd_descriptor':hex(DESC),
       'runtime_memory_ownership_proven':False,
       'real_lcd_task_and_spi_timing_proven':False,
       'safe_to_flash':False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware',type=Path,nargs='+')
    p.add_argument('--elf',type=Path,required=True)
    a=p.parse_args()
    layout=layout_from_elf(a.elf)
    results=[audit_bytes(x.read_bytes(),x.name,layout) for x in a.firmware]
    report={'status':'STATIC EVIDENCE ONLY — NOT A HARDWARE VALIDATION',
            'linked_ARM_layout':layout,
            'firmwares':results,
            'physical_LCD_validated':False,
            'free_RAM_while_audio_plays_validated':False,
            'hardware_key_hook_validated':False,
            'firmware_ready_to_flash':False}
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
