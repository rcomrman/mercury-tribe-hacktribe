#!/usr/bin/env python3
"""Read-only ARM evidence, task/IRQ/cyclic tables and direct branch references."""
import argparse,gzip,hashlib,json,struct,subprocess
from pathlib import Path
from run import HASHES,ROOT
RANGES=[(0,0x40),(0x40,0x84),(0xf4,0x144),(0x144,0x22c),(0x2b4,0x454),(0x454,0x59c),(0x5a0,0x7ac),(0x7ac,0xacc),(0x1394,0x1480),(0x1480,0x1504),(0x1504,0x18f0),(0x18f0,0x1a64),(0x1bc8,0x1cd4),(0x2114,0x2164),(0x25300,0x25814),(0x298bc,0x29a40),(0x2a598,0x2aacc),(0x2ab7c,0x2b220),(0x2d030,0x2d238),(0x834fc,0x835c0),(0x83848,0x83898),(0x839c8,0x83a10),(0x83fe8,0x8403c),(0xa3640,0xa3900),(0xe4c50,0xe4c70),(0xf9320,0xf9340),(0x170b60,0x170b78)]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);a=p.parse_args();out=ROOT/'reports/recovery_r11';build=ROOT/'build/recovery_r11';audits=[]
 for vi,(path,h) in enumerate(zip((a.custom,a.backup),HASHES)):
  vsb=path.read_bytes();assert hashlib.sha256(vsb).hexdigest()==h;b=vsb[256:];rows=[];txt=[]
  for lo,hi in RANGES:
   rows.append({'start':hex(0xc0000000+lo),'end_exclusive':hex(0xc0000000+hi),'sha256':hashlib.sha256(b[lo:hi]).hexdigest()})
   # Disassemble exact original bytes as a standalone ARM ELF. No installation image.
   (build/'slice.bin').write_bytes(b[lo:hi]);(build/'slice.S').write_text('.section .text\n.global slice\nslice:\n.incbin "'+str(build/'slice.bin')+'"\n')
   subprocess.run(['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-c',str(build/'slice.S'),'-o',str(build/'slice.o')],check=True)
   subprocess.run(['ld.lld','-Ttext='+hex(0xc0000000+lo),'--entry=slice',str(build/'slice.o'),'-o',str(build/'slice.elf')],check=True)
   txt.append(subprocess.run(['llvm-objdump','-D','--section=.text',str(build/'slice.elf')],capture_output=True,text=True,check=True).stdout)
  (out/f'{vi}_native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(txt).encode(),mtime=0))
  tasks=[]
  for i in range(10):
   w=struct.unpack_from('<8I',b,0xa37a8+32*i);tasks.append({'id':i+1,'record':hex(0xc00a37a8+32*i),'words':[hex(x) for x in w],'entry':hex(w[2]),'initial_priority':w[3]&255,'stack_bytes':w[4],'stack_base':hex(w[5])})
  refs=[];targets={0xc0000a00,0xc0000928,0xc000066c,0xc0000454,0xc002d030,0xc00298bc,0xc0000144}
  for pos in range(0,len(b)-4,4):
   w=struct.unpack_from('<I',b,pos)[0]
   if w&0x0e000000==0x0a000000:
    imm=w&0xffffff;imm=imm-(1<<24) if imm&(1<<23) else imm;target=(0xc0000000+pos+8+imm*4)&0xffffffff
    if target in targets:refs.append({'from':hex(0xc0000000+pos),'target':hex(target),'word':hex(w)})
  audits.append({'vsb':vi,'ranges':rows,'tasks':tasks,'irq_record':[hex(x) for x in struct.unpack_from('<3I',b,0xa3668)],'task_count':struct.unpack_from('<I',b,0xa38e8)[0],'cyclic_record':[hex(x) for x in struct.unpack_from('<5I',b,0xa36c0)],'direct_branch_candidates':refs})
 assert audits[0]['irq_record']==audits[1]['irq_record']==['0x15','0x0','0xc0025798'];assert audits[0]['ranges']==audits[1]['ranges'];assert audits[0]['tasks']==audits[1]['tasks'];assert audits[0]['cyclic_record']==['0x2','0x0','0xc002572c','0x2','0x0']
 (out/'static_audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'range_count':len(RANGES),'evidence':audits,'warning':'Direct branch candidates include data decoded as instructions; inspect call context before attributing function semantics.'},indent=2)+'\n');print('PASS: 27 original ranges and ten task records identical across VSB; cyclic callback verified')
if __name__=='__main__':main()
