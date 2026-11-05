#!/usr/bin/env python3
"""QEMU native ARM fixture; no GPIO or LCD success emulation."""
import gzip,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r23_2';O=R/'reports/recovery_r23_2'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wno-unused-function']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',B/'start.o']);rows=[];allraw={}
 for vi,(name,h) in enumerate(zip(sys.argv[1:],H)):
  raw=Path(name).read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h
  (B/'original.bin').write_bytes(raw[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r23_2/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for c in range(4):
   run([*arm,f'-DCASE={c}','-c','tests/recovery_r23_2/worker.c','-o',B/'worker.o'])
   elf=B/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',B/'start.o',B/'worker.o',B/'original.o','-o',elf])
   p=subprocess.run(['qemu-arm','-cpu','arm926',str(elf)],capture_output=True,timeout=30);assert len(p.stdout)%2112==0 and p.stdout
   headers=[struct.unpack_from('<16I',p.stdout,i) for i in range(0,len(p.stdout),2112)]
   assert all(x[0]==0x52394c43 and x[1]==2400+c and x[2]!=99 and x[6:8]==(0x39,0xc5) for x in headers)
   assert p.returncode==(88 if c==2 else 0)
   if c==2:assert headers[-1][2:5]==(90,0xbc,11)
   else:assert headers[-1][2]==20
   allraw[vi,c]=p.stdout;(O/f'{vi}_{c}.records.gz').write_bytes(gzip.compress(p.stdout,mtime=0))
   rows.append({'vsb':vi,'case':c,'exit':p.returncode,'stages':[list(x[:6]) for x in headers],'sha256':hashlib.sha256(p.stdout).hexdigest()})
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
 for c in range(4):assert allraw[0,c]==allraw[1,c]
 (O/'results.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
 print('PASS 8 native ARM runs; 2 expected GPIO faults; 4 exact cross-VSB pairs')
if __name__=='__main__':main()
