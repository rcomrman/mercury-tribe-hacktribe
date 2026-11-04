#!/usr/bin/env python3
"""R17 observer selection, invocation and withdrawal boundaries. No code patches."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'observer_register':(0x70778,0x70818),'observer_notify':(0x70688,0x706c8),'observer_invoke_remove':(0x705dc,0x70688),'observer_inverse_destructor':(0x41b74,0x41bc4),'alternate_notify':(0x82728,0x827c0),'alternate_subject_ctor':(0x826a0,0x82728),'sample_destructor_a':(0x841a0,0x841f4),'sample_destructor_b':(0x551ec,0x55238),'irq_mask_helpers':(0x40,0x60),'semaphores':(0xca8,0xe9c),'ui_wrapper':(0x2d030,0x2d048),'page_replace':(0x6e9a0,0x6ea10),'page_delete':(0x6efd0,0x6f040),'lcd_controls':(0x16230,0x163c8),'lcd_poll':(0x15cdc,0x15d14)}

def main():
 out=ROOT/'reports/recovery_r17';build=ROOT/'build/recovery_r17';build.mkdir(parents=True,exist_ok=True)
 images=[]
 for path,h in zip(sys.argv[1:],HASHES):
  b=Path(path).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 assert len(images)==2
 ranges=[]
 for n,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi],n
  ranges.append(dict(name=n,start=hex(0xc0000000+lo),end_exclusive=hex(0xc0000000+hi),sha256=hashlib.sha256(images[0][lo:hi]).hexdigest()))
 b=images[0];word=lambda a:struct.unpack_from('<I',b,a-0xc0000000)[0]
 expected={0xc007061c:0xe5913000,0xc007062c:0xe5913004,0xc0070650:0xe2810008,0xc0070654:0xe8900003,0xc007066c:0x179310c0,0xc0070670:0xe08300c0,0xc0070674:0x1791c00c,0xc007067c:0xe12fff3c,0xc00705f4:0xe5c03014,0xc00705f8:0xe5803000,0xc0070794:0x0a00001d,0xc00706b4:0xebffffd8,0xc0082770:0xebffb7a9,0xc0041ba0:0xeb00ba8d,0xc0016594:0x01e26000,0xc0016b54:0xe5832004}

 for a,w in expected.items():
  assert word(a)==w and struct.unpack_from("<I",images[1],a-0xc0000000)[0]==w,hex(a)
 targets=[0xc0070778,0xc0070688,0xc007061c,0xc00705dc,0xc0041b74,0xc0082728,0xc0082788]

 refs={hex(t):{'direct_branch_candidates':[],'aligned_pointer_candidates':[]} for t in targets}
 for p in range(0,len(b),4):
  w=struct.unpack_from('<I',b,p)[0];pc=0xc0000000+p
  if w in targets:refs[hex(w)]['aligned_pointer_candidates'].append(hex(pc))
  if w&0xe000000==0xa000000 and w>>28!=15:
   i=w&0xffffff;i=i-(1<<24) if i&(1<<23) else i;t=(pc+8+4*i)&0xffffffff
   if t in targets:refs[hex(t)]['direct_branch_candidates'].append(hex(pc))
 assert refs['0xc007061c']['direct_branch_candidates']==['0xc00706b4','0xc0082770']
 (build/'inspect.bin').write_bytes(b);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r17/inspect.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')]);elf=str(build/'STATIC_INSPECTION_ONLY.elf');run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',elf])
 txt=[]
 for n,(lo,hi) in RANGES.items():txt.append(n+'\n'+run(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',elf]))
 (out/'native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(txt).encode(),mtime=0))
 (out/'audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':ranges,'instruction_contracts':{hex(a):hex(w) for a,w in expected.items()},'references':refs,'scope':'Bounded ARM aligned candidates. No exhaustive indirect/Thumb/IRQ/FIQ/DMA coverage or quiescence claim.'},indent=2)+'\n')
 print('PASS',len(ranges),'identical ranges; observer ABI; exact pre-load/partial-tuple/BLX boundaries; two native invocation routes')
if __name__=='__main__':main()
