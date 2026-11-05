#!/usr/bin/env python3
"""Native eight-page forced comparator, no worker, sender, or MMIO."""
import gzip,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r23_4';O=R/'reports/recovery_r23_4'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,check=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wno-unused-function']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',B/'start.o']);rows=[];outputs={}
 for vi,(name,h) in enumerate(zip(sys.argv[1:],H)):
  raw=Path(name).read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h
  (B/'original.bin').write_bytes(raw[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r23_4/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for c in range(2):
   run([*arm,f'-DCASE={c}','-c','tests/recovery_r23_4/force.c','-o',B/'force.o'])
   elf=B/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',B/'start.o',B/'force.o',B/'original.o','-o',elf])
   trace=B/f'{vi}_{c}.trace';p=run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',trace,elf]);rawout=p.stdout
   assert len(rawout)==10*2112
   for i in range(10):
    h0=struct.unpack_from('<16I',rawout,i*2112);assert h0[:2]==(0x52394c43,2500+c) and h0[5]==i and h0[6:8]==(0x39,0xc5)
    if 1<=i<=8:assert h0[2:5]==(9+i,c,i-1)
    assert rawout[i*2112+64:i*2112+1088]==rawout[i*2112+1088:i*2112+2112]
   t=trace.read_text();assert '0xc0015ab4:' in t and '0xc001613c:' not in t
   (O/f'{vi}_{c}.records.gz').write_bytes(gzip.compress(rawout,mtime=0));(O/f'{vi}_{c}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
   outputs[vi,c]=rawout;rows.append({'vsb':vi,'force':c,'records':10,'sha256':hashlib.sha256(rawout).hexdigest()})
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
 for c in range(2):assert outputs[0,c]==outputs[1,c]
 (O/'results.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
 print('PASS 4 ARM runs: eight equal pages yield 0 without force and 1 with force; no sender')
if __name__=='__main__':main()
