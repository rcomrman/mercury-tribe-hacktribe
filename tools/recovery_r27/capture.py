#!/usr/bin/env python3
"""Capture ARM store operands at C001862C with QEMU GDB breakpoints, no code writes."""
import gzip,hashlib,importlib.util,json,os,socket,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r27';O=R/'reports/recovery_r27'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
S=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
spec=importlib.util.spec_from_file_location('rsp',R/'tools/recovery_r17/rsp.py');rsp=importlib.util.module_from_spec(spec);spec.loader.exec_module(rsp)
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Isrc','-Wno-unused-function'];objs=[]
 for n,src in enumerate(['tests/recovery_r2/start.S',*S]):
  obj=B/f'{n}.o';run([*arm,'-c',src,'-o',obj]);objs.append(obj)
 rows=[];allwrites={}
 for vi,(name,h) in enumerate(zip(sys.argv[1:],H)):
  blob=Path(name).read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (B/'original.bin').write_bytes(blob[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r27/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for scene in range(8):
   run([*arm,f'-DSCENE={scene}','-c','tests/recovery_r27/capture.c','-o',B/'probe.o'])
   elf=B/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',objs[0],B/'probe.o',*objs[1:],B/'original.o','-o',elf])
   with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   with (B/'stdout').open('wb') as out,(B/'stderr').open('wb') as err:
    p=subprocess.Popen(['qemu-arm','-cpu','arm926','-g',str(port),str(elf)],stdout=out,stderr=err)
    try:
     g=rsp.RSP(port);g.s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);assert g.cmd('?').startswith(('T05','S05'));g.bp(0xc001862c)
     writes=[]
     while True:
      stop=g.resume()
      if stop.startswith('W'):break
      assert stop.startswith(('T05','S05')),stop
      regs=struct.unpack_from('<16I',bytes.fromhex(g.regs()));assert regs[15]==0xc001862c
      writes.append([regs[3]+0x3c,regs[2]])
      assert len(writes)<=1024
      g.bp(0xc001862c,False);assert g.cmd('s').startswith(('T05','S05'));g.bp(0xc001862c)
     g.s.close();assert p.wait(timeout=10)==0
    finally:
     if p.poll() is None:p.kill();p.wait()
   output=(B/'stdout').read_bytes();assert len(output)==4224 and len(writes)==1024
   frame=output[64:1088];base=struct.unpack_from('<I',output,12)[0]
   assert all(addr==base+0x3c for addr,_ in writes)
   assert bytes(v&255 for _,v in writes)==frame
   assert output[1088:2112]==frame
   (O/f'{vi}_{scene}.records.gz').write_bytes(gzip.compress(output,mtime=0))
   (O/f'{vi}_{scene}.writes.gz').write_bytes(gzip.compress(b''.join(struct.pack('<II',*w) for w in writes),mtime=0))
   allwrites[vi,scene]=writes;rows.append({'vsb':vi,'scene':scene,'writes':len(writes),'port':base+0x3c,'sha256':hashlib.sha256(frame).hexdigest()})
   print('captured',vi,scene,len(writes),'writes',flush=True)
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
 for scene in range(8):
  assert [x[1] for x in allwrites[0,scene]]==[x[1] for x in allwrites[1,scene]]
 (O/'results.json').write_text(json.dumps({'cases':rows,'mechanism':'QEMU gdb breakpoint before original STR, operands R2 and R3; no code writes'},indent=2)+'\n')
 print('PASS 16 runs: 16384 ordered SPI register store operands, 8 presets and two VSB; RAM only')
if __name__=='__main__':main()
