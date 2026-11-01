#!/usr/bin/env python3
"""Read-only ARM firmware inspection, not a patcher or a hardware validation.
Requires two original Korg firmware VSB paths. Does not write them or build images.
Analyzes a restricted set of fixed ARM opcodes whose intent was checked via
llvm-objdump. Raw BL scans identify candidate call sites, not runtime frequency.
"""
from pathlib import Path
import hashlib, struct, sys, json
BASE=0xC0000000
HEADER=0x100
SIZE=0x200000
TARGETS=(0xC002A8D4, 0xC002A7EC, 0xC002814C, 0xC0015DD0, 0xC0015AB4)

def word(img,addr):
    off=addr-BASE
    if not (0 <= off <= len(img)-4):raise ValueError(f'outside ARM image {addr:#x}')
    return struct.unpack_from('<I',img,off)[0]

def dest(a,op):
    if ((op>>25)&7)!=5:return None
    off=op&0xffffff
    if off&0x800000:off-=0x1000000
    return (a+8+(off<<2))&0xffffffff

def examine(p):
    blob=p.read_bytes()
    assert len(blob)==HEADER+SIZE, f'{p.name}: invalid size'
    img=blob[HEADER:]
    conditions={
      'callback literal value':word(img,0xC002A970)==0xC002A71C,
      'initializer loads callback via PC-relative literal':word(img,0xC002A918)==0xE59F3050,
      'initializer stores callback in object at +0xC':word(img,0xC002A928)==0xE580300C,
      'scheduler loads callback from object at +0xC':word(img,0xC002A80C)==0xE590300C,
      'scheduler BLX register':word(img,0xC002A810)==0xE12FFF33,
      'scheduler reload count from +0x8':word(img,0xC002A804)==0xE5903008,
      'initializer count 20 is calls, not ms':word(img,0xC002A8F8)==0xE3A05014,
      'callback argument opcode3':word(img,0xC002A720)==0xE3A01003,
      'callback tail to dispatcher':dest(0xC002A728,word(img,0xC002A728))==0xC0015DD0,
      'LCD opcode2 marks +5 dirty':word(img,0xC0015E68)==0xE5C32005,
      'comparator receives source via helper':dest(0xC0015AE8,word(img,0xC0015AE8))==0xC0015A60,
      'comparator loads source page from C031B710':word(img,0xC0015A94)==0xC031B710,
      'comparator loads shadow page from C031B310':word(img,0xC0015B4C)==0xC031B310,
      'comparator compares 128 bytes':word(img,0xC0015B0C)==0xE3A02080 and dest(0xC0015B10,word(img,0xC0015B10))==0xC00097A8,
      'comparator copies 128 bytes to shadow':word(img,0xC0015B34)==0xE3A02080 and dest(0xC0015B38,word(img,0xC0015B38))==0xC000985C,
      'LCD page loop calls native sender':dest(0xC00160A0,word(img,0xC00160A0))==0xC001613C,
      'panel decoder known entry opcode':word(img,0xC002814C)==0xE92D4038,
    }
    missing=[k for k,v in conditions.items() if not v]
    if missing:raise RuntimeError(f'{p.name}: static opcode mismatch: {missing}')
    callsites={a:[] for a in TARGETS}
    for off in range(0,len(img)-3,4):
        op=struct.unpack_from('<I',img,off)[0]
        if (op>>28)!=0xE or ((op>>25)&7)!=5:continue
        target=dest(BASE+off,op)
        if target in callsites:
            callsites[target].append({'address':hex(BASE+off),'operation':'BL' if op&(1<<24) else 'B'})
    return {'name':p.name, 'sha256':hashlib.sha256(blob).hexdigest(),
            'checked_instructions':len(conditions), 'passed':sum(conditions.values()),
            'scheduler_initializer_callsites':callsites[0xC002A8D4],
            'scheduler_tick_callsites':callsites[0xC002A7EC],
            'panel_decoder_callsites':callsites[0xC002814C],
            'lcd_dispatcher_direct_branches':callsites[0xC0015DD0],
            'native_comparator_callsites':callsites[0xC0015AB4]}

def main():
    if len(sys.argv)!=3:
        raise SystemExit('usage: python3 tools/md34_arm_inspection_readonly.py user_custom.VSB user_backup.VSB')
    firmwares=[examine(Path(p)) for p in sys.argv[1:]]
    print(json.dumps({'evidence':'STATIC ARM INSPECTION, READ ONLY',
      'callback_pointer_literal_not_live_writeable_pointer':True,
      'runtime_RAM_safe':False,'initialization_hook_validated':False,
      'physical_BUTTON_IDS_validated':False,'SPI_timing_validated':False,
      'firmware_ready_to_flash':False,'firmwares':firmwares},indent=2))

if __name__=='__main__':main()
