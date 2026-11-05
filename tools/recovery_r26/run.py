#!/usr/bin/env python3
"""Build unchanged V30 for Linux ARM926; compare all frames with host."""
import gzip,hashlib,json,os,struct,subprocess,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r26';O=R/'reports/recovery_r26'
S=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
def run(a,**kw):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60,**kw)
def main():
 assert len(sys.argv)==3
 os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 run(['clang','-std=c99','-O2','-Isrc','tests/recovery_r1/frames.c',*S,'-o',B/'host'])
 host=run([B/'host']).stdout
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Isrc']
 objects=[]
 for idx,src in enumerate(['tests/recovery_r2/start.S','tests/recovery_r26/frames_arm.c',*S]):
  obj=B/f'{idx}.o';run([*arm,'-fstack-usage','-c',src,'-o',obj]);objects.append(obj)
 elf=B/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',*objects,'-o',elf])
 t=time.perf_counter_ns();p=run(['qemu-arm','-cpu','arm926',elf]);elapsed=time.perf_counter_ns()-t
 assert len(host)==32768 and p.stdout==host
 (O/'arm-frames.bin').write_bytes(p.stdout)
 size=run(['llvm-objdump','-h',elf]).stdout.decode()
 stack=[]
 for f in B.glob('*.su'):stack.extend(f.read_text().splitlines())
 result={'frames':32,'presets':8,'sha256':hashlib.sha256(host).hexdigest(),'qemu_process_ns':elapsed,'elf_sections':size,'stack_usage':stack,'limits':'whole QEMU process wall time; stack per function only; no instrument cycles'}
 hashes=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052'];records={};rows=[]
 for vi,(path,h) in enumerate(zip(sys.argv[1:],hashes)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (B/'original.bin').write_bytes(blob[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r26/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for scene in range(8):
   run([*arm,f'-DSCENE={scene}','-c','tests/recovery_r26/integration.c','-o',B/'integration.o'])
   native=B/'INTEGRATION_LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',objects[0],B/'integration.o',*objects[2:],B/'original.o','-o',native])
   trace=B/f'{vi}_{scene}.trace';p=run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',trace,native]);raw=p.stdout
   assert len(raw)==13*2112
   for f in range(4):
    before=raw[(3*f)*2112:(3*f+1)*2112];after=raw[(3*f+1)*2112:(3*f+2)*2112];target=host[(scene*4+f)*1024:(scene*4+f+1)*1024]
    assert struct.unpack_from('<I',before,8)[0]==10+f and struct.unpack_from('<I',after,8)[0]==30+f
    assert before[64:1088]==target and after[64:1088]==target and after[1088:2112]==target
    assert struct.unpack_from('<II',raw,(3*f+2)*2112+8)==(50+f,8)
   assert struct.unpack_from('<I',raw,12*2112+8)[0]==20
   text=trace.read_text();assert '0xc0015824:' in text and '0xc0015ab4:' in text and '0xc001851c:' in text
   records[vi,scene]=raw;(O/f'{vi}_{scene}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(O/f'{vi}_{scene}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
   rows.append({'vsb':vi,'preset':scene,'records':13,'sha256':hashlib.sha256(raw).hexdigest()})
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
 for scene in range(8):assert records[0,scene]==records[1,scene]
 result['native_integration']=rows
 (O/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS 32 V30 frames computed directly on ARM926 equal host bytes; QEMU process wall ns:',elapsed)
 print('PASS 16 ARM integration runs, 64 frames, source/shadow/host equal; direct C001851C to RAM double, last octet checked')
if __name__=='__main__':main()
