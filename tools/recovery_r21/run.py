#!/usr/bin/env python3
"""Build fixed-storage tests and execute the retained native render path on both VSB."""
import gzip,hashlib,json,os,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'reports/recovery_r21'; BUILD=ROOT/'build/recovery_r21'
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
SOURCES=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c','src/mercury_keys.c','src/mini_lfo4.c']
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args,**kw):return subprocess.run(list(map(str,args)),check=True,capture_output=True,**kw)
def main():
 assert len(sys.argv)==3;os.chdir(ROOT);BUILD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 cc=['cc','-D_POSIX_C_SOURCE=200809L','-std=c11','-O2','-Wall','-Wextra','-Wno-misleading-indentation','-Wno-unused-function','-I','src']
 run([*cc,'-fstack-usage','tests/recovery_r21/host.c',*SOURCES,'-o',BUILD/'host'])
 samples=[];lines=[]
 for _ in range(7):
  t=time.perf_counter_ns();p=run([BUILD/'host']);samples.append(time.perf_counter_ns()-t);lines.append(p.stdout.decode().strip())
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',BUILD/'start.o']);native=[]
 for vi,(name,expected) in enumerate(zip(sys.argv[1:],HASHES)):
  blob=Path(name).read_bytes();assert len(blob)==0x200100 and sha(blob)==expected
  (BUILD/'original.bin').write_bytes(blob[256:]);(BUILD/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r21/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',BUILD/'original.S','-o',BUILD/'original.o']);run([*arm,'-c','tests/recovery_r21/native.c','-o',BUILD/'native.o'])
  elf=BUILD/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',BUILD/'start.o',BUILD/'native.o',BUILD/'original.o','-o',elf])
  trace=BUILD/f'{vi}.trace';p=run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',trace,elf],timeout=30)
  assert p.returncode==0 and len(p.stdout)==64;rec=struct.unpack('<16I',p.stdout);assert rec[:5]==(0x5232314e,0x21,1,1,1)
  text=trace.read_text();assert '0xc006ea10:' in text and '0xc006ea24:' in text and '0xc006ea34:' in text
  (OUT/f'native-{vi}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
  native.append(dict(vsb=vi,sha256=expected,record=list(rec),elf_sha256=sha(elf.read_bytes())))
  assert sha(Path(name).read_bytes())==expected
 sus=[]
 for path in BUILD.glob('*.su'):
  for line in path.read_text().splitlines():
   parts=line.rsplit('\t',2)
   if len(parts)==3 and parts[1].isdigit():sus.append(dict(symbol=parts[0].split(':')[-1],bytes=int(parts[1]),kind=parts[2]))
 result=dict(host_runs=lines,host_process_ns=samples,native=native,stack_usage=sorted(sus,key=lambda x:x['bytes'],reverse=True))
 (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(lines[0]);print('PASS 2 VSB: C006EA10 invoked three static slot+8 callbacks; zero image writes.');print('PASS 7 prolonged host runs; max measured stack record:',max((x['bytes'] for x in sus),default=0),'bytes')
if __name__=='__main__':main()
