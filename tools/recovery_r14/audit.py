#!/usr/bin/env python3
"""Bounded R14 native audit; no inference from a pointer alone to task exclusivity."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'spi_status':(0x117c8,0x11804),'ready_selection':(0x18f0,0x1a24),'task5':(0x2a598,0x2a63c),'service_manager':(0x2d65c,0x2de48),'service17':(0x30f00,0x31398),'service34':(0x38d80,0x38e88),'service34_ctor':(0x392a4,0x392d0),'service_tables17':(0xa7608,0xa7628),'service_tables34':(0xa7b58,0xa7b78),'progress_io':(0x4d598,0x4de94),'progress_leaf':(0x60360,0x60424),'startup_call':(0x2ae84,0x2ae94),'lcd_worker':(0x15d14,0x160c4),'spi_poll':(0x15cdc,0x15d14),'fatal':(0x298bc,0x29a00),'terminal':(0x144,0x22c),'kernel_timer':(0x1394,0x14a0),'irq':(0x1560,0x18f0),'wait_semaphore':(0x1bc8,0x1e10),'kernel_semaphore':(0xca8,0xe9c)}
def main():
 out=ROOT/'reports/recovery_r14';build=ROOT/'build/recovery_r14';build.mkdir(parents=True,exist_ok=True)
 images=[]
 for p,h in zip(sys.argv[1:],HASHES):
  b=Path(p).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 assert len(images)==2
 ranges=[]
 for n,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi],n
  ranges.append(dict(name=n,start=hex(0xc0000000+lo),end_exclusive=hex(0xc0000000+hi),sha256=hashlib.sha256(images[0][lo:hi]).hexdigest()))
 b=images[0];word=lambda a:struct.unpack_from('<I',b,a-0xc0000000)[0]
 expected={0xc002db70:0xe3a01011,0xc002db78:0xeb000cef,0xc002db80:0xe5845044,0xc002dd08:0xe3a01022,0xc002dd10:0xeb002d63,0xc002dd18:0xe5845088,0xc004d808:0xe59d7024,0xc004d810:0x0a000002,0xc00a7610:0xc003128c,0xc00a7b60:0xc0038d80,0xc0031250:0xeb007182,0xc0031248:0xe3a00000,0xc003124c:0xe1a01000,0xc0038e38:0xe1a00007,0xc0038e3c:0xe1a01007,0xc004d864:0xe2517000,0xc004d898:0xe1570006,0xc004d91c:0x0affffeb,0xc004dcf0:0xe1a02007,0xc004dd78:0xe1a02007,0xc0030ff8:0xc00a7608,0xc00392cc:0xc00a7b58}
 for a,w in expected.items():assert word(a)==w,hex(a)
 targets=[0xc0031234,0xc003128c,0xc0038d80,0xc004d860,0xc004d5cc,0xc006038c,0xc006040c,0xc002d844,0xc002d684]
 refs={hex(t):{'branches':[],'aligned_pointers':[]} for t in targets}
 for p in range(0,len(b),4):
  w=struct.unpack_from('<I',b,p)[0];pc=0xc0000000+p
  if w in targets:refs[hex(w)]['aligned_pointers'].append(hex(pc))
  if w&0xe000000==0xa000000 and w>>28!=15:
   i=w&0xffffff;i=i-(1<<24) if i&(1<<23) else i;t=(pc+8+4*i)&0xffffffff
   if t in targets:refs[hex(t)]['branches'].append(hex(pc))
 (build/'inspect.bin').write_bytes(b);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r14/inspect.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')]);elf=str(build/'STATIC_INSPECTION_ONLY.elf');run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',elf])
 text=[]
 for n,(lo,hi) in RANGES.items():text.append(n+'\n'+run(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',elf]))
 (out/'native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(text).encode(),mtime=0))
 (out/'audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':ranges,'instruction_contracts':{hex(k):hex(v) for k,v in expected.items()},'references':refs,'contexts':[{'service':17,'table':'C00A7608','slot8':'C003128C','chain':'task5 C002A598→C002D844→C002D684→slot8→C003128C→C0031234','progress_argument':0},{'service':34,'table':'C00A7B58','slot8':'C0038D80','chain':'task5 C002A598→C002D844→C002D684→slot8→C0038D80','progress_argument':0}],'scope':'Configured task5 dispatch routes established; additional indirect callers/aliases and side effects of all callees not excluded. No global lock or recovery authority established.'},indent=2)+'\n')
 print('PASS',len(ranges),'identical ranges; service17/task5 and service34/task5 routes; progress disabled at both open callsites')
if __name__=='__main__':main()
