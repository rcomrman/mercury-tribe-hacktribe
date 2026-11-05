#!/usr/bin/env python3
"""Run original wait/probe against RAM doubles; no MMIO or instrument."""
import gzip,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r23_3';O=R/'reports/recovery_r23_3'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',B/'start.o']);rows=[];images=[]
 for vi,(name,h) in enumerate(zip(sys.argv[1:],H)):
  raw=Path(name).read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h;images.append(raw[256:])
  (B/'original.bin').write_bytes(raw[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r23_3/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for case in range(5):
   run([*arm,f'-DCASE={case}','-c','tests/recovery_r23_3/spi.c','-o',B/'spi.o'])
   elf=B/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',B/'start.o',B/'spi.o',B/'original.o','-o',elf])
   trace=B/f'{vi}_{case}.trace'
   try:
    p=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),str(elf)],capture_output=True,timeout=2);rc=p.returncode;output=p.stdout
   except subprocess.TimeoutExpired as e:rc='host_timeout';output=e.stdout or b''
   records=[list(struct.unpack_from('<4I',output,i)) for i in range(0,len(output),16)];assert all(x[:2]==[0x52323333,case] for x in records)
   assert records[0]==[0x52323333,case,0,1 if case in (1,3,4) else 0]
   assert rc==('host_timeout' if case==2 else 0)
   assert len(records)==(3 if case==4 else 2 if case==3 else 1)
   if case==4:assert records[1:]==[[0x52323333,4,2,1],[0x52323333,4,3,0x00fe007f]]
   (O/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
   rows.append({'vsb':vi,'case':case,'exit':rc,'records':records})
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
 for lo,hi in ((0x117c8,0x117fc),(0x15cdc,0x15d14),(0x18398,0x186d4),(0x16100,0x16230)):
  assert images[0][lo:hi]==images[1][lo:hi]
 assert [{k:v for k,v in x.items() if k!='vsb'} for x in rows[:5]]==[{k:v for k,v in x.items() if k!='vsb'} for x in rows[5:]]
 (O/'results.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
 print('PASS 10 ARM RAM-double runs; 2 host timeouts, 2 wait returns, 2 128-byte loops; no physical ACK')
if __name__=='__main__':main()
