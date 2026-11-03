#!/usr/bin/env python3
"""New R14 experiments only, using R9 loader/R12 pool/R13 coordinator unchanged."""
import gzip,hashlib,json,os,resource,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r14');out=Path('reports/recovery_r14');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 def run(a,**kw):return subprocess.run(list(map(str,a)),check=True,timeout=90,**kw)
 # Reuse the already verified R1 generator; no previous experiment rerun.
 sources=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
 run(['clang','-O2','-Wall','-Wextra','-Werror','-Isrc','tests/recovery_r1/frames.c',*sources,'-o',build/'frames_host']);frames=run([build/'frames_host'],capture_output=True).stdout
 assert len(frames)==32768 and sha(frames)==json.loads(Path('reports/recovery_r1/results.json').read_text())['frames_sha256'];(build/'frames.bin').write_bytes(frames)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror'];run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip(sys.argv[1:],HASHES)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and sha(blob)==h;(build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r14/original.bin"\n.global frames\nframes:\n.incbin "build/recovery_r14/frames.bin"\n.section .note.GNU-stack,"",%progbits\n');run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(28):
   run([*arm,f'-DR14_CASE={case}','-c','tests/recovery_r14/native.c','-o',build/'probe.o']);elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/'probe.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout
   except subprocess.TimeoutExpired as e:rc='timeout';raw=e.stdout or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0));assert len(raw)%2112==0;events=[]
   for n in range(0,len(raw),2112):
    h=struct.unpack_from('<16I',raw,n);events.append({'header':list(h),'source_sha256':sha(raw[n+64:n+1088]),'shadow_sha256':sha(raw[n+1088:n+2112])})
   rows.append(dict(vsb=vi,case=case,exit=rc,events=events));print(vi,case,rc,[(e['header'][2],e['header'][3]) for e in events],flush=True)
   (out/'results.json').write_text(json.dumps({'vsb_sha256':HASHES,'frames_sha256':sha(frames),'cases':rows},indent=2)+'\n')
  assert sha(Path(path).read_bytes())==HASHES[vi]
 assert len(rows)==56
if __name__=='__main__':main()
