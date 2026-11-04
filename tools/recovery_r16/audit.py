#!/usr/bin/env python3
"""R16 native codecs, observer links and lifetime boundaries. No code patches."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'lcd_dispatch':(0x15dd0,0x15eb8),'lcd_contrast_input':(0x15f44,0x15f84),'lcd_worker':(0x15fa0,0x160c4),'lcd_poll':(0x15cdc,0x15d14),'lcd_controls':(0x16230,0x163c8),'ui_messages':(0x70a60,0x70b80),'ui_publication':(0x83fe8,0x8403c),'ui_wrapper':(0x2d030,0x2d048),'ui_alternate_cycle':(0x83374,0x834fc),'service_dispatch':(0x2d684,0x2d844),'temporary_cleanup':(0x2d434,0x2d454),'progress':(0x60360,0x60424),'observer_remove_invoke':(0x705dc,0x706c8),'observer_register':(0x70778,0x70818),'observer_base_destructor':(0x41b74,0x41bc4),'graphics_append':(0x614fc,0x61530),'secondary_replace':(0x6e9a0,0x6ea10),'graphics_destroy':(0x60f10,0x60f90),'secondary_delete':(0x6efd0,0x6f040),'main_cycle':(0x6f178,0x6f370)}

def main():
 out=ROOT/'reports/recovery_r16';build=ROOT/'build/recovery_r16';build.mkdir(parents=True,exist_ok=True)
 images=[]
 for path,h in zip(sys.argv[1:],HASHES):
  b=Path(path).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 assert len(images)==2
 ranges=[]
 for n,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi],n
  ranges.append(dict(name=n,start=hex(0xc0000000+lo),end_exclusive=hex(0xc0000000+hi),sha256=hashlib.sha256(images[0][lo:hi]).hexdigest()))
 b=images[0];word=lambda a:struct.unpack_from('<I',b,a-0xc0000000)[0]
 expected={0xc0015f5c:0xe5d33000,0xc0015f68:0xe5832008,0xc0015f74:0xe5c3200c,0xc0015e68:0xe5c32005,0xc0015ea8:0xe3a03000,0xc0070790:0xe1500004,0xc0070794:0x0a00001d,0xc00707a8:0xe58c4000,0xc00707c8:0xe5cc3014,0xc00707ec:0xe5843008,0xc00705f4:0xe5c03014,0xc00705f8:0xe5803000,0xc0070608:0xe12fff1e,0xc00706b4:0xebffffd8,0xc0041ba0:0xeb00ba8d,0xc006e9cc:0xe5843014,0xc006e9f0:0xe5840014,0xc0061514:0x15821000,0xc0061520:0xe5802004}

 for a,w in expected.items():assert word(a)==w,hex(a)
 targets=[0xc0015f44,0xc0015dd0,0xc0070778,0xc00705dc,0xc0070688,0xc007061c,0xc0041b74,0xc00614fc,0xc006e9a0,0xc006efd0,0xc002d030]

 refs={hex(t):{'direct_branch_candidates':[],'aligned_pointer_candidates':[]} for t in targets}
 for p in range(0,len(b),4):
  w=struct.unpack_from('<I',b,p)[0];pc=0xc0000000+p
  if w in targets:refs[hex(w)]['aligned_pointer_candidates'].append(hex(pc))
  if w&0xe000000==0xa000000 and w>>28!=15:
   i=w&0xffffff;i=i-(1<<24) if i&(1<<23) else i;t=(pc+8+4*i)&0xffffffff
   if t in targets:refs[hex(t)]['direct_branch_candidates'].append(hex(pc))
 (build/'inspect.bin').write_bytes(b);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r16/inspect.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')]);elf=str(build/'STATIC_INSPECTION_ONLY.elf');run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',elf])
 txt=[]
 for n,(lo,hi) in RANGES.items():txt.append(n+'\n'+run(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',elf]))
 (out/'native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(txt).encode(),mtime=0))
 (out/'audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':ranges,'instruction_contracts':{hex(a):hex(w) for a,w in expected.items()},'references':refs,'scope':'Bounded ARM aligned candidates. No exhaustive indirect/Thumb/IRQ/FIQ/DMA coverage or quiescence claim.'},indent=2)+'\n')
 print('PASS',len(ranges),'identical ranges; one-byte contrast, observer register/dedup/remove/invoke and page ownership contracts')
if __name__=='__main__':main()
