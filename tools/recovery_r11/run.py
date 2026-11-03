#!/usr/bin/env python3
"""R11 bounded original ARM kernel/UI probes. No full scheduler, MMIO or firmware output."""
import argparse,gzip,hashlib,json,os,resource,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
FAULTS={0:0xc06a2894,4:0,15:0,16:14,17:0,23:0,31:0xabcdef}
def run(cmd):return subprocess.run(list(map(str,cmd)),check=True,timeout=90)
def validate(case,rc,events,trace):
 assert rc==(88 if case in FAULTS else 0),(case,rc)
 assert [e[3] for e in events if e[2]==90]==([FAULTS[case]] if case in FAULTS else []),(case,events)
 assert not any(e[2]==99 for e in events),(case,events)
 if case in (18,19):assert [e[3] for e in events if e[2]==10]==[1,2,3]
 if case in (20,21,22):assert '0xc002d030:' in trace and '0xc0083848:' in trace
 if case==22:assert events[1][23:25]==(1,0) and events[-1][23:25]==(1,1) and '0xc00834fc:' in trace
 if case in (15,17):assert events[-1][11]&0xff==10 and '0xc0001978:' in trace
 if case not in FAULTS and case not in (18,19):assert events[-1][2]==20
 for e in events:
  assert e[26:30]==(0x12345678,)*4 and e[30:34]==(0x39393939,)*4
  if e[6]:assert e[21:23]==(0x13579bdf,0x2468ace0)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);p.add_argument('--explore',action='store_true');a=p.parse_args()
 os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r11');out=Path('reports/recovery_r11');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip((a.custom,a.backup),HASHES)):
  blob=path.read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r11/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(32):
   run([*arm,f'-DR11_CASE={case}','-c','tests/recovery_r11/native.c','-o',build/'probe.o'])
   elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/f'{vi}_{case}.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout
   except subprocess.TimeoutExpired as ex:rc='timeout';raw=ex.stdout or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
   assert len(raw)%160==0,(vi,case,len(raw));events=[struct.unpack_from('<40I',raw,pos) for pos in range(0,len(raw),160)]
   assert all(e[0]==0x5231314b and e[1]==case and e[5]==i for i,e in enumerate(events))
   print(vi,case,rc,[(e[2],hex(e[3])) for e in events],flush=True)
   if not a.explore:validate(case,rc,events,trace.read_text())
   rows.append({'vsb':vi,'case':case,'exit':rc,'events':events})
  assert hashlib.sha256(path.read_bytes()).hexdigest()==h
 if not a.explore:
  for x,y in zip(rows[:32],rows[32:]):assert x['events']==y['events'] and x['exit']==y['exit']
 (out/'results.json').write_text(json.dumps({'exploratory':a.explore,'vsb_sha256':HASHES,'cases':rows},indent=2)+'\n')
if __name__=='__main__':main()
