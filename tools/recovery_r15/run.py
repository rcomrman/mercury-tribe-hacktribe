#!/usr/bin/env python3
"""New R15 experiments, unmodified R9 loader and R12-R14 contracts."""
import gzip,hashlib,json,os,resource,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert len(sys.argv)==3;os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r15');out=Path('reports/recovery_r15');build.mkdir(parents=True,exist_ok=True)
 def run(a):return subprocess.run(list(map(str,a)),check=True,timeout=90,capture_output=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror'];run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip(sys.argv[1:],HASHES)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and sha(blob)==h;(build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r15/original.bin"\n.section .note.GNU-stack,"",%progbits\n');run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(29):
   compiled=subprocess.run([*arm,f'-DR15_CASE={case}','-c','tests/recovery_r15/native.c','-o',str(build/'probe.o')],capture_output=True,text=True)
   if compiled.returncode:print(compiled.stderr,flush=True);raise RuntimeError('compile')
   elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/'probe.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout
   except subprocess.TimeoutExpired as e:rc='timeout';raw=e.stdout or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0));assert len(raw)%2112==0;events=[]
   for n in range(0,len(raw),2112):
    h=struct.unpack_from('<16I',raw,n);events.append({'header':list(h),'source_sha256':sha(raw[n+64:n+1088]),'shadow_sha256':sha(raw[n+1088:n+2112])})
   rows.append(dict(vsb=vi,case=case,exit=rc,events=events));print(vi,case,rc,[(e['header'][2],e['header'][3],hex(e['header'][4])) for e in events],flush=True)
   (out/'results.json').write_text(json.dumps({'vsb_sha256':HASHES,'cases':rows},indent=2)+'\n')
  assert sha(Path(path).read_bytes())==HASHES[vi]
 assert len(rows)==58
if __name__=='__main__':main()
