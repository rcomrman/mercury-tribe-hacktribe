#!/usr/bin/env python3
"""Read-only LCD dependency audit, both exact VSBs; no peripheral emulation."""
import argparse,gzip,hashlib,json,os,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'comparator_and_shadow':(0x15a40,0x15b50),'descriptor_to_sender':(0x15d14,0x163c8),'board_getter':(0x1198c,0x119ac),'spi_ready':(0x117c8,0x11804),'hardware_getters':(0x16538,0x1673c),'clock_delay':(0x1673c,0x16880),'gpio_control':(0x16abc,0x16c50),'spi_write':(0x18398,0x186d4),'lcd_startup_task':(0x2ab80,0x2ac64),'task_literals':(0x2b0a4,0x2b0bc),'fatal_lcd_path':(0x298bc,0x29a00),'ui_tick':(0x836e4,0x83714),'graphics_lock_stubs':(0x3f104,0x3f10c)}
TARGETS=[0xc0015dd0,0xc0015fa0,0xc0015ab4,0xc001613c,0xc0015d14,0xc0015eb8,0xc0015cdc]
def main():
 p=argparse.ArgumentParser();p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);a=p.parse_args();os.chdir(ROOT)
 build=Path('build/recovery_r9');out=Path('reports/recovery_r9');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 images=[]
 for f,h in zip((a.custom,a.backup),HASHES):
  raw=f.read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h;images.append(raw[256:])
 rows=[]
 for name,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi],name
  rows.append({'name':name,'start':hex(0xc0000000+lo),'end_exclusive':hex(0xc0000000+hi),'sha256':hashlib.sha256(images[0][lo:hi]).hexdigest(),'identical':True})
 (build/'inspect.bin').write_bytes(images[0]);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r9/inspect.bin"\n')
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
 assert refs['0xc0015ab4']==['0xc0016084'] and refs['0xc001613c']==['0xc00160a0']
 # These small getters return original constants; no arbitrary addresses are supplied.
 assert struct.unpack_from('<I',images[0],0x16594)[0]==0x01e26000
 assert struct.unpack_from('<I',images[0],0x16680)[0]==0x01c41000
 prior=[]
 for mission,n in ((6,17),(7,17),(8,9)):
  folder=Path(f'reports/recovery_r{mission}');records=json.loads((folder/'results.json').read_text());assert len(records)==2*n
  byte_count=0;address_set=set()
  for item in records:
   tag=f'{item["vsb"]}_{item["case"]}';raw=gzip.decompress((folder/f'{tag}.records.gz').read_bytes());trace=gzip.decompress((folder/f'{tag}.trace.gz').read_bytes());byte_count+=len(trace)
   address_set.update(re.findall(rb'0x(c[0-9a-f]{7}):',trace));pos=0;events=[];shots={}
   while pos<len(raw):
    h=struct.unpack_from('<16I',raw,pos);pos+=64;assert h[0]==0x52325549;events.append(list(h))
    if h[1]==100:
     frame=raw[pos:pos+1024];pos+=1024;assert len(frame)==1024;shots[str(h[3])]=hashlib.sha256(frame).hexdigest()
   assert pos==len(raw) and events==item['events'] and shots==item['snapshots']
   if mission==7 and item['case']==11:assert b'si_addr=0x000000bc' in trace
   if mission==8 and item['case']==0:assert b'0xc0060f3c:' in trace
  prior.append({'mission':mission,'cases':len(records),'trace_bytes_read':byte_count,'unique_native_instruction_addresses':len(address_set),'records_verified':True})
 (out/'static_audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':rows,'aligned_branch_candidates':refs,'caveat':'Aligned ARM candidate scan, not exhaustive indirect/Thumb call graph. Data may decode as instructions.','previous_evidence_checked_without_rerunning':prior},indent=2)+'\n')
 print('PASS:',len(rows),'identical LCD ranges; 86 prior archived cases checked without replay')
if __name__=='__main__':main()
