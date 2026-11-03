#!/usr/bin/env python3
"""R15 exact dispatch/argument/lifetime/stop boundaries. No code patches."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'ui_boundary':(0x2d030,0x2d048),'service_dispatch':(0x2d684,0x2d844),'lcd_callback_setup':(0x2a71c,0x2a978),'service_message_copy':(0x3b7b4,0x3b898),'service_publish_handles':(0x2d5b0,0x2d684),'service_consume_stop':(0x2d844,0x2d944),'service_stop_flag':(0x2de48,0x2de84),'ui_publisher':(0x83fe8,0x8403c),'ui_consumer_main':(0x83848,0x83898),'ui_consumer_alternate':(0x833f0,0x834fc),'ui_messages':(0x70a60,0x70b90),'task4':(0x2b144,0x2b220),'task5':(0x2a598,0x2a63c),'kernel_wake_clear':(0xacc,0xb78),'kernel_exit':(0x66c,0x6a0),'kernel_dormant':(0x1a24,0x1a64),'worker':(0x15fa0,0x160c4),'poll':(0x15cdc,0x15d14),'fatal':(0x298bc,0x29a10)}
def main():
 out=ROOT/'reports/recovery_r15';build=ROOT/'build/recovery_r15';build.mkdir(parents=True,exist_ok=True)
 images=[]
 for path,h in zip(sys.argv[1:],HASHES):
  b=Path(path).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 assert len(images)==2
 ranges=[]
 for n,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi],n
  ranges.append(dict(name=n,start=hex(0xc0000000+lo),end_exclusive=hex(0xc0000000+hi),sha256=hashlib.sha256(images[0][lo:hi]).hexdigest()))
 b=images[0];word=lambda a:struct.unpack_from('<I',b,a-0xc0000000)[0]
 expected={0xc002d030:0xe5900004,0xc002d03c:0xe593300c,0xc002d040:0xe12fff33,0xc002d68c:0xe5918008,0xc002d69c:0xe1d150d4,0xc002d6ac:0xe594400c,0xc002d6cc:0xe7934105,0xc002d6e8:0xe593300c,0xc002d790:0xe5933008,0xc002d7a4:0xe5933010,0xc002d7b8:0xe586300c,0xc002d81c:0xe5c63010,0xc002de78:0xe3a03001,0xc002de7c:0xe5c03019,0xc002a720:0xe3a01003,0xc002a724:0xe3a02000,0xc002a970:0xc002a71c,0xc003b7e4:0xe5912008,0xc003b7ec:0xe591200c,0xc002d5c8:0xe5922004}
 for a,w in expected.items():assert word(a)==w,hex(a)
 targets=[0xc002d030,0xc002d684,0xc002a71c,0xc002d88c,0xc002de78,0xc003b7d4,0xc002d5b0,0xc0000acc]
 refs={hex(t):{'direct_branch_candidates':[],'aligned_pointer_candidates':[]} for t in targets}
 for p in range(0,len(b),4):
  w=struct.unpack_from('<I',b,p)[0];pc=0xc0000000+p
  if w in targets:refs[hex(w)]['aligned_pointer_candidates'].append(hex(pc))
  if w&0xe000000==0xa000000 and w>>28!=15:
   i=w&0xffffff;i=i-(1<<24) if i&(1<<23) else i;t=(pc+8+4*i)&0xffffffff
   if t in targets:refs[hex(t)]['direct_branch_candidates'].append(hex(pc))
 assert refs['0xc002d030']['direct_branch_candidates']==['0xc002b1ec']
 assert refs['0xc002d684']['direct_branch_candidates']==['0xc002d87c']
 assert refs['0xc002a71c']['aligned_pointer_candidates']==['0xc002a970']
 (build/'inspect.bin').write_bytes(b);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r15/inspect.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')]);elf=str(build/'STATIC_INSPECTION_ONLY.elf');run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',elf])
 txt=[]
 for n,(lo,hi) in RANGES.items():txt.append(n+'\n'+run(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',elf]))
 (out/'native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(txt).encode(),mtime=0))
 (out/'audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':ranges,'instruction_contracts':{hex(a):hex(w) for a,w in expected.items()},'references':refs,'scope':'Bounded ARM aligned candidates. No exhaustive indirect/Thumb/IRQ/FIQ/DMA coverage or quiescence claim.'},indent=2)+'\n')
 print('PASS',len(ranges),'identical ranges; exact UI/service/timer boundaries; shallow service words and stop-request store')
if __name__=='__main__':main()
