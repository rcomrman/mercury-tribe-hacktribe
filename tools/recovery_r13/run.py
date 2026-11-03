#!/usr/bin/env python3
"""R13 coordination coverage probes. Reuse R9 loader, R12 pool and R1 oracle."""
import argparse,gzip,hashlib,json,os,resource,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
FAULTS={c:0x01e260bc for c in (4,8,10,12,16,17,19)}
def sha(b):return hashlib.sha256(b).hexdigest()
def command(args,**kw):return subprocess.run(list(map(str,args)),check=True,timeout=90,**kw)
def decode(raw,case):
 assert len(raw)%2112==0;events=[]
 for pos in range(0,len(raw),2112):
  h=struct.unpack_from('<16I',raw,pos);assert h[0]==0x52394c43 and h[1]==200+case and h[5]==len(events) and h[6]==0x39
  a=raw[pos+64:pos+1088];b=raw[pos+1088:pos+2112];events.append({'header':list(h),'source_sha256':sha(a),'shadow_sha256':sha(b),'different_bytes':sum(x!=y for x,y in zip(a,b))})
 return events
def validate(case,rc,events,trace,frames):
 assert rc==(88 if case in FAULTS else 0),(case,rc)
 assert not any(e['header'][2]==99 for e in events)
 stages={e['header'][2]:e for e in events}
 assert [e['header'][3] for e in events if e['header'][2]==90]==([FAULTS[case]] if case in FAULTS else [])
 if case not in FAULTS:assert events[-1]['header'][2]==20
 if case==0:
  shots=[e for e in events if e['header'][2]==1];assert len(shots)==32
  for n,e in enumerate(shots):assert e['source_sha256']==e['shadow_sha256']==sha(frames[n*1024:(n+1)*1024])
 if case in (2,9):assert stages[1]['shadow_sha256']==sha(bytes([0xee])*384+bytes([0x11])*640)
 if case in (6,14):assert stages[1]['shadow_sha256']==sha(bytes([0x11])*384+bytes([0xee])*640)
 if case==7:assert stages[1]['source_sha256']==sha(bytes(1024)) and '0xc0015f84:' in trace
 if case in (3,4,16):assert '0xc006038c:' in trace
 if case in (5,6,18):
  assert all('0x'+s+':' in trace for s in ('c002d030','c0083428','c00833f0','c0083374'))
  assert '0xc006f178:' not in trace
 if case==5:assert stages[1]['source_sha256']==stages[1]['shadow_sha256']==sha(frames[:1024])
 if case in (4,8,12,16,17):assert stages[90]['shadow_sha256']==sha(bytes([0xee])*128+bytes([0x11])*896)
 if case==10:assert stages[90]['shadow_sha256']==sha(bytes([0x11])*1024) and '0xc00162c4:' in trace
 if case in FAULTS:assert stages[89]['header'][3]==(4 if case==19 else (2 if case in (12,17) else 1))
 if case==11:assert '0xc0015fa0:' in trace and '0xc001613c:' not in trace
 if case in (0,1,2,3,5,6,7,9,13,14,15,18):assert '0xc001613c:' not in trace
 if case==15:assert stages[1]['header'][3]==3 and (stages[1]['header'][4]>>16&255)!=3
 if case==17:assert '0xc002a7ec:' in trace and stages[1]['header'][3]==1 and stages[2]['header'][3]==2 and stages[1]['shadow_sha256']==sha(bytes([0x11])*1024)
 if case==18:assert stages[1]['header'][3]==0 and stages[1]['header'][4]>>24==1 and stages[1]['shadow_sha256']==sha(bytes([0x11])*1024) and '0xc0015fa0:' not in trace
 if case==19:
  oracle=bytearray([0x11])*1024
  for x in range(9,65):oracle[7*128+x]=0x71
  assert stages[90]['source_sha256']==stages[90]['shadow_sha256']==sha(oracle) and '0xc006038c:' in trace
 if case==3:assert stages[1]['source_sha256']!=sha(bytes([0xee])*384+bytes([0x11])*640)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);p.add_argument('--explore',action='store_true');a=p.parse_args();os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 build=Path('build/recovery_r13');out=Path('reports/recovery_r13');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 sources=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
 command(['clang','-O2','-Wall','-Wextra','-Werror','-Isrc','tests/recovery_r1/frames.c',*sources,'-o',build/'frames_host']);frames=command([build/'frames_host'],capture_output=True).stdout
 assert len(frames)==32768 and sha(frames)==json.loads(Path('reports/recovery_r1/results.json').read_text())['frames_sha256'];(build/'frames.bin').write_bytes(frames)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror'];command([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip((a.custom,a.backup),HASHES)):
  blob=path.read_bytes();assert len(blob)==0x200100 and sha(blob)==h;(build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r13/original.bin"\n.global frames\nframes:\n.incbin "build/recovery_r13/frames.bin"\n.section .note.GNU-stack,"",%progbits\n');command([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(20):
   command([*arm,f'-DR13_CASE={case}','-c','tests/recovery_r13/native.c','-o',build/'probe.o']);elf=build/'LINUX_TEST_ONLY.elf';command(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/f'{vi}_{case}.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout
   except subprocess.TimeoutExpired as ex:rc='timeout';raw=ex.stdout or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0));events=decode(raw,case);print(vi,case,rc,[(e['header'][2],hex(e['header'][3])) for e in events],flush=True)
   if not a.explore:validate(case,rc,events,trace.read_text(),frames)
   rows.append({'vsb':vi,'case':case,'exit':rc,'events':events})
  assert sha(path.read_bytes())==h
 if not a.explore:
  for x,y in zip(rows[:20],rows[20:]):assert x['events']==y['events'] and x['exit']==y['exit']
 (out/'results.json').write_text(json.dumps({'exploratory':a.explore,'vsb_sha256':HASHES,'frames_sha256':sha(frames),'cases':rows},indent=2)+'\n')
if __name__=='__main__':main()
