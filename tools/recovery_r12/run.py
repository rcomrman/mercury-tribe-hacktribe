#!/usr/bin/env python3
"""R12 role-pool and native semaphore/framebuffer probes; limited serial fixtures."""
import argparse,gzip,hashlib,json,os,resource,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
FAULTS={16:0,19:0x01e260bc}
def command(args,**kw):return subprocess.run(list(map(str,args)),check=True,timeout=90,**kw)
def sha(b):return hashlib.sha256(b).hexdigest()
def decode(raw,case):
 assert len(raw)%2112==0;events=[]
 for pos in range(0,len(raw),2112):
  h=struct.unpack_from('<16I',raw,pos);assert h[0]==0x52394c43 and h[1]==100+case and h[5]==len(events) and h[6:8]==(0x39,0xc5)
  src=raw[pos+64:pos+1088];shadow=raw[pos+1088:pos+2112]
  events.append({'header':list(h),'source_sha256':sha(src),'shadow_sha256':sha(shadow),'different_bytes':sum(x!=y for x,y in zip(src,shadow))})
 return events
def validate(case,rc,events,trace,raw,frames):
 assert rc==(88 if case in FAULTS else 0),(case,rc)
 assert [e['header'][3] for e in events if e['header'][2]==90]==([FAULTS[case]] if case in FAULTS else [])
 assert not any(e['header'][2]==99 for e in events)
 if case not in FAULTS:assert events[-1]['header'][2]==20
 stages={e['header'][2]:e for e in events}
 if case in (3,4,5,6,17,18,19,20,24):assert '0xc0015ab4:' in trace
 if case in (12,13,14,15,16,17,18):assert '0xc0000c4c:' in trace
 if case==16:assert stages[89]['header'][3:5]==[50,0] and '0xc0001d14:' in trace
 if case in (4,17):
  h=stages[1];assert h['shadow_sha256']==sha(bytes([0xee])*384+bytes([0x11])*640) and h['different_bytes']==0
 if case==24:assert stages[1]['shadow_sha256']==sha(bytes([0xee])*64+bytes([0x11])*960)
 if case in (5,4,17):assert events[-1]['shadow_sha256']==sha(bytes([0xee])*1024)
 if case==6:
  shots=[e for e in events if e['header'][2]==1];assert len(shots)==32
  for n,e in enumerate(shots):assert e['source_sha256']==e['shadow_sha256']==sha(frames[n*1024:(n+1)*1024])
 if case in (3,4,5,6,17,18,20,24):assert '0xc001613c:' not in trace
 if case==0:assert events[-1]['source_sha256']==events[-1]['shadow_sha256']==sha(frames[31*1024:32*1024])
 if case==3:assert events[-1]['source_sha256']==events[-1]['shadow_sha256']==sha(bytes([0x11])*1024)
 if case==18:assert stages[1]['shadow_sha256']==sha(bytes([255])*128+bytes([0x11])*896)
 if case==19:
  assert stages[90]['shadow_sha256']==sha(frames[:128]+bytes([0x11])*896)
  assert stages[91]['header'][3]==0 and '0xc001613c:' in trace
 if case==21:assert stages[1]['header'][3:5]==[0,1] and '0xc0015900:' in trace
 if case==25:assert stages[1]['header'][3:5]==[0,1] and stages[2]['header'][3:5]==[8,0] and '0xc00006a0:' in trace
 if case==23:assert stages[1]['header'][3:5]==[1,3]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);p.add_argument('--explore',action='store_true');a=p.parse_args()
 os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r12');out=Path('reports/recovery_r12');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 # Reuse R1 generator and verify its published oracle, without rerunning R1 experiments.
 sources=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
 command(['clang','-O2','-Wall','-Wextra','-Werror','-Isrc','tests/recovery_r1/frames.c',*sources,'-o',build/'frames_host'])
 frames=command([build/'frames_host'],capture_output=True).stdout;assert len(frames)==32768 and sha(frames)==json.loads(Path('reports/recovery_r1/results.json').read_text())['frames_sha256'];(build/'frames.bin').write_bytes(frames)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 command([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip((a.custom,a.backup),HASHES)):
  blob=path.read_bytes();assert len(blob)==0x200100 and sha(blob)==h
  (build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r12/original.bin"\n.global frames\nframes:\n.incbin "build/recovery_r12/frames.bin"\n.section .note.GNU-stack,"",%progbits\n')
  command([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(26):
   command([*arm,f'-DR12_CASE={case}','-c','tests/recovery_r12/native.c','-o',build/'probe.o'])
   elf=build/'LINUX_TEST_ONLY.elf';command(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/f'{vi}_{case}.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout
   except subprocess.TimeoutExpired as ex:rc='timeout';raw=ex.stdout or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0));events=decode(raw,case)
   print(vi,case,rc,[(e['header'][2],hex(e['header'][3])) for e in events],flush=True)
   if not a.explore:validate(case,rc,events,trace.read_text(),raw,frames)
   rows.append({'vsb':vi,'case':case,'exit':rc,'events':events})
  assert sha(path.read_bytes())==h
 if not a.explore:
  for x,y in zip(rows[:26],rows[26:]):assert x['events']==y['events'] and x['exit']==y['exit']
 (out/'results.json').write_text(json.dumps({'exploratory':a.explore,'vsb_sha256':HASHES,'frames_sha256':sha(frames),'cases':rows},indent=2)+'\n')
if __name__=='__main__':main()
