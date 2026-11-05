#!/usr/bin/env python3
"""Execute original ARM worker in isolated Linux process; no GPIO/SPI substitute."""
import gzip,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'build/recovery_r23_1';OUT=ROOT/'reports/recovery_r23_1'
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def run(cmd):return subprocess.run(list(map(str,cmd)),capture_output=True,check=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(ROOT);BUILD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wno-unused-function']
 images=[Path(p).read_bytes()[256:] for p in sys.argv[1:]]
 for lo,hi in ((0x15a60,0x15b50),(0x15cdc,0x162a8),(0x836e4,0x83714)):
  assert images[0][lo:hi]==images[1][lo:hi],('native range differs',hex(lo),hex(hi))
 run([*arm,'-c','tests/recovery_r2/start.S','-o',BUILD/'start.o']);rows=[];raws={}
 for vi,(path,h) in enumerate(zip(sys.argv[1:],HASHES)):
  raw=Path(path).read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h
  (BUILD/'original.bin').write_bytes(raw[256:]);(BUILD/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r23_1/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',BUILD/'original.S','-o',BUILD/'original.o'])
  for case in range(6):
   run([*arm,f'-DCASE={case}','-c','tests/recovery_r23_1/worker.c','-o',BUILD/'worker.o'])
   elf=BUILD/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',BUILD/'start.o',BUILD/'worker.o',BUILD/'original.o','-o',elf])
   p=subprocess.run(['qemu-arm','-cpu','arm926',str(elf)],capture_output=True,timeout=30)
   assert len(p.stdout)%2112==0 and p.stdout
   records=[struct.unpack_from('<16I',p.stdout,i) for i in range(0,len(p.stdout),2112)]
   assert all(x[0]==0x52394c43 and x[1]==2300+case and x[2]!=99 and x[6:8]==(0x39,0xc5) for x in records)
   assert p.returncode==(88 if case in (3,4) else 0)
   if case in (3,4):assert records[-1][2:5]==(90,0xbc,11)
   else:assert records[-1][2]==20
   raws[vi,case]=p.stdout
   (OUT/f'worker-{vi}-{case}.gz').write_bytes(gzip.compress(p.stdout,mtime=0))
   rows.append({'vsb':vi,'case':case,'exit':p.returncode,'stages':[list(x[:6]) for x in records],'sha256':hashlib.sha256(p.stdout).hexdigest()})
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
 for case in range(6):assert raws[0,case]==raws[1,case]
 (OUT/'worker-results.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
 print('PASS 12 ARM runs: 8 normal, 4 expected GPIO faults; six exact cross-VSB record pairs')
if __name__=='__main__':main()
