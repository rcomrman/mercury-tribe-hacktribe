#!/usr/bin/env python3
"""Bounded read-only audit; aligned ARM branch candidates are not exhaustive xrefs."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
hashes=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
assert len(sys.argv)==3
images=[]
for p,h in zip(sys.argv[1:],hashes):
 raw=Path(p).read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h;images.append(raw[256:])
ranges={'packet_decode':(0x2814c,0x282a0),'byte_assembly':(0x282d8,0x28544),'event_task':(0x2a38c,0x2a598),'input_state_repeat':(0x8241c,0x82620),'repeat_tables':(0xe4af8,0xe4b40),'type1_producer':(0x839f0,0x83a18),'graphics_manager':(0x6e6ec,0x6f178),'navigation':(0x700d8,0x705dc),'extension':(0x170b80,0x170ca8),'extension_service':(0x170170,0x1702f8)}
build=root/'build/recovery_r6';out=root/'reports/recovery_r6';build.mkdir(exist_ok=True,parents=True);out.mkdir(exist_ok=True,parents=True)
rows=[]
for name,(a,z) in ranges.items():
 assert images[0][a:z]==images[1][a:z],name
 rows.append({'name':name,'start':hex(0xc0000000+a),'end_exclusive':hex(0xc0000000+z),'sha256':hashlib.sha256(images[0][a:z]).hexdigest(),'identical':True})
refs={}
for target in [0xc00824c8,0xc00839f0,0xc002814c,0xc0170b80]:
 hits=[]
 for i in range(0,len(images[0]),4):
  w=struct.unpack_from('<I',images[0],i)[0]
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   imm=w&0xffffff;imm=imm-0x1000000 if imm&0x800000 else imm
   if (0xc0000000+i+8+4*imm)&0xffffffff==target:hits.append(hex(0xc0000000+i))
 refs[hex(target)]=hits
assert refs['0xc00824c8']==['0xc0082600']
assert images[0][0xe4af8:0xe4af8+35]==b'\xff'*35
assert images[0][0xe4b1c:0xe4b1c+35]==b'\xff'*35
(build/'inspect.bin').write_bytes(images[0]);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r6/inspect.bin"\n')
subprocess.run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')],cwd=root,check=True)
subprocess.run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',str(build/'STATIC_INSPECTION_ONLY.elf')],check=True)
with (out/'native_disassembly.txt').open('w') as f:
 for name,(a,z) in ranges.items():
  f.write('\n'+name+'\n');subprocess.run(['llvm-objdump','-D',f'--start-address={0xc0000000+a}',f'--stop-address={0xc0000000+z}',str(build/'STATIC_INSPECTION_ONLY.elf')],stdout=f,check=True)
(out/'static_audit.json').write_text(json.dumps({'vsb_sha256':hashes,'ranges':rows,'aligned_branch_candidates':refs,'caveat':'Data can decode as instructions; indirect calls, Thumb and calculated targets not exhaustive.','thresholds':[-1]*35},indent=2)+'\n')
print('PASS: 10 identical ranges, branch candidates and two signed repeat tables verified')
