#!/usr/bin/env python3
"""Read-only LCD dependency audit, both exact VSBs; no peripheral emulation."""
import argparse,gzip,hashlib,json,os,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'board_configuration':(0x163c8,0x16478),'counter_configuration':(0x19040,0x191e0),'spi_configuration':(0x18d24,0x18ddc),'other_block_configuration':(0x1932c,0x193c0),'auxiliary_object':(0x119ac,0x11ab8),'lcd_helpers':(0x15c48,0x15c98),'countdowns_and_tasks':(0x2a7ac,0x2ab48),'startup':(0x2ab7c,0x2ac64),'task_table':(0xa37a8,0xa38a8),'type0_and_dispatch':(0x834fc,0x839f0),'ui_vtable':(0xe4c50,0xe4ca0),'fatal_path':(0x298bc,0x29a10),'irq_and_context':(0x40,0x68),'task_identifier':(0x1480,0x14ec),'dirty_rectangle':(0x1531c,0x154c8),'contrast_adapter':(0x9a8c8,0x9a900),'progress_lcd':(0x6038c,0x6040c)}
TARGETS=[0xc0015c48,0xc00163c8,0xc002a7ec,0xc00298bc,0xc0015dd0]
def main():
 p=argparse.ArgumentParser();p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);a=p.parse_args();os.chdir(ROOT)
 build=Path('build/recovery_r10');out=Path('reports/recovery_r10');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 images=[]
 for f,h in zip((a.custom,a.backup),HASHES):
  raw=f.read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h;images.append(raw[256:])
 rows=[]
 for name,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi],name
  rows.append({'name':name,'start':hex(0xc0000000+lo),'end_exclusive':hex(0xc0000000+hi),'sha256':hashlib.sha256(images[0][lo:hi]).hexdigest(),'identical':True})
 (build/'inspect.bin').write_bytes(images[0]);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r10/inspect.bin"\n')
 subprocess.run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')],check=True)
 elf=build/'STATIC_INSPECTION_ONLY.elf';subprocess.run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',str(elf)],check=True)
 with (out/'native_disassembly.txt').open('w') as stream:
  for name,(lo,hi) in RANGES.items():
   stream.write('\n'+name+'\n');stream.flush()
   subprocess.run(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',str(elf)],stdout=stream,check=True)
 refs={hex(t):[] for t in TARGETS}
 for i in range(0,len(images[0]),4):
  w=struct.unpack_from('<I',images[0],i)[0]
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   imm=w&0xffffff;imm=imm-0x1000000 if imm&0x800000 else imm;target=(0xc0000000+i+8+imm*4)&0xffffffff
   if target in TARGETS:refs[hex(target)].append(hex(0xc0000000+i))
 assert '0xc002a728' in refs['0xc0015dd0']
 assert struct.unpack_from('<I',images[0],0xe4c68)[0]==0xc00836e4
 assert struct.unpack_from('<I',images[0],0x2a96c)[0]==0xc00839c8
 assert struct.unpack_from('<I',images[0],0x2a970)[0]==0xc002a71c
 # These small getters return original constants; no arbitrary addresses are supplied.
 assert struct.unpack_from('<I',images[0],0x16594)[0]==0x01e26000
 assert struct.unpack_from('<I',images[0],0x16680)[0]==0x01c41000
 prior=[{'mission':9,'commit':'43a57b986478992c7082e0615578e7a5c573c7d2','reused':'loader, records, fault diagnostics only; prior scripts unchanged'}]
 (out/'static_audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':rows,'aligned_branch_candidates':refs,'caveat':'Aligned ARM candidate scan, not exhaustive indirect/Thumb call graph. Data may decode as instructions.','previous_evidence_checked_without_rerunning':prior},indent=2)+'\n')
 print('PASS:',len(rows),'identical R10 ranges; countdown callback literals and UI slot checked')
if __name__=='__main__':main()
