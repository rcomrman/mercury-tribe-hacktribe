#!/usr/bin/env python3
"""Read-only, bounded static audit of routines used by R2 experiments."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RANGES={
 'graphics_init':(0xc003f0d4,0xc003f104),'line_clipping':(0xc003f2b4,0xc003f310),
 'factory':(0xc006e664,0xc006e690),'page25_constructor':(0xc006d518,0xc006d600),
 'page25_destructors':(0xc006d464,0xc006d49c),'vector_grow_append':(0xc006144c,0xc0061530),
 'page_destructor':(0xc0060f10,0xc0060fcc),'observer_destructor':(0xc0041b74,0xc0041bc4),
 'original_iteration':(0xc006f240,0xc006f2a0),'background_constructor':(0xc008b424,0xc008b478),
 'background_cleanup':(0xc006ddcc,0xc006dec0),'text_constructor':(0xc008ccd4,0xc008cd7c),
 'text_cleanup_thunk':(0xc008c990,0xc008c9d4),'text_deleting_thunk':(0xc008cab8,0xc008cb10),
 'heap_wrappers':(0xc0008f30,0xc0008f70),'heap_extension':(0xc002cefc,0xc002cf40),
 'page25_vtable':(0xc00e3e08,0xc00e3e30),'background_vtable':(0xc00e52d8,0xc00e52f4),
 'text_vtable_subobject':(0xc00e5454,0xc00e5470)}
def main():
 images=[Path(p).read_bytes()[256:] for p in sys.argv[1:]];assert len(images)==2
 out=ROOT/'reports/recovery_r2';build=ROOT/'build/recovery_r2';rows=[]
 for name,(start,end) in RANGES.items():
  parts=[b[start-0xc0000000:end-0xc0000000] for b in images];assert parts[0]==parts[1],name
  rows.append({'name':name,'start':hex(start),'end_exclusive':hex(end),'bytes':end-start,'sha256':hashlib.sha256(parts[0]).hexdigest(),'same_both_vsbs':True})
 image=images[0]
 checks={0xc0060f3c:0xeafffffe,0xc0060f50:0xe5933010,0xc0060f6c:0xe5933004,0xc006f280:0xe5933008,0xc006f288:0xe12fff33}
 for addr,word in checks.items():assert int.from_bytes(image[addr-0xc0000000:addr-0xc0000000+4],'little')==word
 (build/'inspect.S').write_text('.section .text\n.global korg_image\nkorg_image:\n.incbin "build/recovery_r2/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')],cwd=ROOT,check=True)
 subprocess.run(['ld.lld','-Ttext=0xc0000000','-e','korg_image',str(build/'inspect.o'),'-o',str(build/'STATIC_INSPECTION_ONLY.elf')],check=True)
 with (out/'native_disassembly.txt').open('w') as f:
  for name,(start,end) in RANGES.items():
   if 'vtable' in name:continue
   f.write('\n'+name+'\n')
   r=subprocess.run(['llvm-objdump','-D',f'--start-address={start}',f'--stop-address={end}',str(build/'STATIC_INSPECTION_ONLY.elf')],capture_output=True,text=True,check=True);f.write(r.stdout)
 (out/'static_audit.json').write_text(json.dumps({'ranges':rows,'checked_opcodes':{hex(k):hex(v) for k,v in checks.items()}},indent=2)+'\n')
 print('Static R2:',len(rows),'identical native ranges; five opcode contracts checked')
if __name__=='__main__':main()
