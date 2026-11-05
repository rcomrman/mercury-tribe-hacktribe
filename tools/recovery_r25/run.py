#!/usr/bin/env python3
"""Generate V30 reference frames and exercise native ARM in isolated QEMU."""
import gzip,hashlib,json,os,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r25';O=R/'reports/recovery_r25'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
SRC=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
def run(a):return subprocess.run(list(map(str,a)),capture_output=True,check=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 run(['clang','-std=c99','-O2','-Isrc','tests/recovery_r1/frames.c',*SRC,'-o',B/'frames_host'])
 frames=run([B/'frames_host']).stdout;assert len(frames)==32768;(B/'frames.bin').write_bytes(frames)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wno-unused-function']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',B/'start.o']);rows=[];results={}
 for vi,(path,expected) in enumerate(zip(sys.argv[1:],H)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==expected
  (B/'original.bin').write_bytes(blob[256:]);(B/'data.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r25/original.bin"\n.global frames\nframes:\n.incbin "build/recovery_r25/frames.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'data.S','-o',B/'data.o'])
  for scene in range(8):
   for worker in range(2):
    run([*arm,f'-DSCENE={scene}',f'-DWORKER={worker}','-c','tests/recovery_r25/integration.c','-o',B/'probe.o'])
    elf=B/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',B/'start.o',B/'probe.o',B/'data.o','-o',elf])
    trace=B/f'{vi}_{scene}_{worker}.trace';p=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),str(elf)],capture_output=True,timeout=30)
    raw=p.stdout;assert raw and len(raw)%2112==0
    records=[raw[i:i+2112] for i in range(0,len(raw),2112)];headers=[struct.unpack_from('<16I',r) for r in records]
    assert p.returncode==(88 if worker else 0) and all(h[0]==0x52394c43 and h[1]==2500+2*scene+worker and h[2]!=99 and h[5]==i for i,h in enumerate(headers))
    assert records[0][64:1088]==frames[scene*4096:scene*4096+1024]
    if worker:assert headers[-1][2:5]==(90,0xbc,11)
    else:assert len(records)==10 and records[-1][1088:2112]==records[-1][64:1088]
    t=trace.read_text();assert '0xc0015824:' in t and '0xc0015ab4:' in t
    if worker:assert '0xc0015fa0:' in t and '0xc001613c:' in t
    (O/f'{vi}_{scene}_{worker}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(O/f'{vi}_{scene}_{worker}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
    results[vi,scene,worker]=raw;rows.append({'vsb':vi,'scene':scene,'worker':worker,'exit':p.returncode,'stages':[list(h[:6]) for h in headers]})
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
 for s in range(8):
  for w in range(2):assert results[0,s,w]==results[1,s,w]
 (O/'results.json').write_text(json.dumps({'frame_sha256':hashlib.sha256(frames).hexdigest(),'cases':rows},indent=2)+'\n')
 print('PASS 32 ARM runs, 16 expected GPIO faults, 16 exact cross-VSB record pairs; no physical transmission')
if __name__=='__main__':main()
