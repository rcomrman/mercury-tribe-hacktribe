#!/usr/bin/env python3
"""Mercury Dust MD45 - ARM relay static pre-audit only.
Does NOT emulate, execute target code, modify VSB, or establish hardware safety.
Usage: python3 md45_static_abi_audit.py path/to/research.elf [--custom X.VSB --backup Y.VSB]
"""
import argparse, hashlib, json, pathlib, re, subprocess, sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('elf', type=pathlib.Path)
parser.add_argument('--custom', type=pathlib.Path)
parser.add_argument('--backup', type=pathlib.Path)
parser.add_argument('--output', type=pathlib.Path)
a = parser.parse_args()

p = subprocess.run(['llvm-objdump','-d',str(a.elf)], capture_output=True,text=True,check=True)
symbols = {}
for header in re.finditer(r'(?m)^([0-9a-f]+) <([^>]+)>:\n', p.stdout):
    next_start = p.stdout.find('\n\n',header.end())
    if next_start < 0: next_start = len(p.stdout)
    body = p.stdout[header.end():next_start]
    words=[]
    for ln in body.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+([0-9a-f]{8})(?:\s|$)',ln)
        if m:
            words.append((int(m.group(1),16),int(m.group(2),16),ln.strip()))
            continue
        # LLVM formats inline literal data as four little-endian byte pairs.
        lit=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+){4}\.word\s+0x([0-9a-f]{8})',ln)
        if lit:
            words.append((int(lit.group(1),16),int(lit.group(2),16),ln.strip()))
    symbols[header.group(2)]={'address':int(header.group(1),16),'words':words}

checks=[]
def check(name,passed,detail):
    checks.append({'check':name,'pass':bool(passed),'detail':detail})

def words(name,n):
    sym=symbols.get(name)
    check('symbol '+name, sym is not None, 'present' if sym is not None else 'absent')
    if sym is None: return [(0,0,'')]*n
    check(name+' instruction count', len(sym['words'])>=n, f"found={len(sym['words'])}, expected>={n}")
    return (sym['words'] + [(0,0,'')]*n)[:n]

def exact(name, index, word, label):
    got=words_cache[name][index][1]
    check(label,got==word,f'got=0x{got:08X}; expected=0x{word:08X}')

def bl(name,index,callee):
    address, opcode,_=words_cache[name][index]
    signed=opcode & 0xffffff
    if signed & 0x800000: signed -= 0x1000000
    target=(address+8+(signed<<2)) & 0xffffffff
    expected=symbols.get(callee,{}).get('address')
    check(f'{name} BL {callee}', (opcode & 0xff000000)==0xeb000000 and target==expected,
          f'encoded target=0x{target:08X}; symbol='+('absent' if expected is None else f'0x{expected:08X}'))

words_cache={
 'md30_callback_bridge':words('md30_callback_bridge',5),
 'md20_key_veneer':words('md20_key_veneer',8),
 'md31_compare_veneer':words('md31_compare_veneer',3),
}
# Opcode masks derive from actual ARM state assembly in MD44, not from a QEMU run.
exact('md30_callback_bridge',0,0xe92d500f,'LCD saves r0-r3,r12,lr (24 bytes)')
bl('md30_callback_bridge',1,'md30_callback_visit')
exact('md30_callback_bridge',2,0xe8bd500f,'LCD restores original arguments / LR')
exact('md30_callback_bridge',3,0xe51ff004,'LCD ARM-state tail branch through PC literal')
exact('md30_callback_bridge',4,0xc002a71c,'LCD original callback address')
exact('md20_key_veneer',0,0xe92d500f,'KEY saves r0-r3,r12,lr (24 bytes)')
bl('md20_key_veneer',1,'md23_route_key')
exact('md20_key_veneer',2,0xe3500000,'KEY tests route result')
exact('md20_key_veneer',3,0xe8bd500f,'KEY restores input arguments / LR')
check('KEY conditional branch after compare', (words_cache['md20_key_veneer'][4][1] & 0xff000000)==0x1a000000,
      f'opcode=0x{words_cache["md20_key_veneer"][4][1]:08X}')
exact('md20_key_veneer',5,0xe59ff000,'KEY original publisher tail branch')
exact('md20_key_veneer',6,0xe12fff1e,'KEY consumed path BX LR')
exact('md20_key_veneer',7,0xc00839f0,'KEY original publisher address')
exact('md31_compare_veneer',0,0xe92d4010,'COMPARE saves r4,lr (8 bytes)')
bl('md31_compare_veneer',1,'md31_compare_visit')
exact('md31_compare_veneer',2,0xe8bd8010,'COMPARE restores r4 and returns via PC')
for name, byte_count in [('md30_callback_bridge',24),('md20_key_veneer',24),('md31_compare_veneer',8)]:
    check(f'{name}: 8-byte entry SP stays aligned at BL', byte_count % 8 == 0,
          f'stack delta={byte_count} bytes; assumes entry SP 8-byte aligned')
for name in words_cache:
    addr=symbols.get(name,{}).get('address',0)
    check(name+' ARM 4-byte address alignment',addr%4==0,f'0x{addr:08X}')
# Current VSB integrity / comparison, without copying firmware contents into output.
vsb={}
if (a.custom is None)!=(a.backup is None): parser.error('provide both VSBs or neither')
if a.custom:
    bufs=[path.read_bytes() for path in (a.custom,a.backup)]
    vsb={'files':[{'name':path.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for path,b in zip((a.custom,a.backup),bufs)],
         'headers_equal':bufs[0][:256]==bufs[1][:256],
         'differing_bytes':sum(x!=y for x,y in zip(*bufs)),
         'expected_file_bytes':0x100+0x200000}
    for item in vsb['files']:
        check(item['name']+' expected VSB length',item['bytes']==0x100+0x200000,str(item['bytes']))
result={'method':'STATIC disassembly checks; no emulation, no runtime ABI, no device validation',
        'elf':str(a.elf),'passed':sum(x['pass'] for x in checks),'total':len(checks),
        'tests':checks,'vsb':vsb, 'limitations':['Entry stack state and IRQ/task context unknown',
        'Preservation of callee-saved registers by compiled C not dynamically validated',
        'ARM/Thumb interworking and real Korg call-site ABI not exercised',
        'No proof of free RAM, SPI completion, or debrick recovery']}
encoded=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
if a.output:a.output.write_text(encoded,encoding='utf-8')
print(f'Static ARM relay check: {result["passed"]}/{result["total"]}')
for t in checks:
    if not t['pass']:print('FAIL',t['check'],t['detail'])
if a.output:print('JSON:',a.output)
if result['passed']!=result['total']:sys.exit(1)
