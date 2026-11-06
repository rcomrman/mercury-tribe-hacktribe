#!/usr/bin/env python3
"""QEMU isolated worker: capture SPI STRs and supply synthetic timer reads."""
import gzip,hashlib,importlib.util,json,os,socket,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r28';O=R/'reports/recovery_r28'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
S=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
spec=importlib.util.spec_from_file_location('rsp',R/'tools/recovery_r17/rsp.py');rsp=importlib.util.module_from_spec(spec);spec.loader.exec_module(rsp)
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Isrc','-Wno-unused-function'];objs=[]
 for n,src in enumerate(['tests/recovery_r2/start.S',*S]):
  obj=B/f'{n}.o';run([*arm,'-c',src,'-o',obj]);objs.append(obj)
 refs=(R/'reports/recovery_r26/arm-frames.bin').read_bytes();rows=[]
 for vi,(name,h) in enumerate(zip(sys.argv[1:],H)):
  blob=Path(name).read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (B/'original.bin').write_bytes(blob[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r28/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for scene in range(8):
   run([*arm,f'-DSCENE={scene}','-c','tests/recovery_r28/native.c','-o',B/'probe.o'])
   elf=B/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',objs[0],B/'probe.o',*objs[1:],B/'original.o','-o',elf])
   with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   with (B/'stdout').open('wb') as out,(B/'stderr').open('wb') as err:
    p=subprocess.Popen(['qemu-arm','-cpu','arm926','-g',str(port),str(elf)],stdout=out,stderr=err)
    try:
     g=rsp.RSP(port);g.s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);assert g.cmd('?').startswith(('T05','S05'))
     points=(0xc00184a4,0xc001862c,0xc00163b8)
     for pc in points:g.bp(pc)
     writes=[];ticks=0
     while True:
      stop=g.resume()
      if stop.startswith('W'):break
      assert stop.startswith(('T05','S05')),stop
      raw=bytearray.fromhex(g.regs());regs=struct.unpack_from('<16I',raw);pc=regs[15];assert pc in points
      if pc==0xc00163b8:
       ticks+=1;struct.pack_into('<I',raw,12,ticks*1500);assert g.cmd('G'+raw.hex())=='OK'
      else:writes.append([pc,regs[3]+0x3c,regs[2]])
      g.bp(pc,False);assert g.cmd('s').startswith(('T05','S05'));g.bp(pc)
      assert len(writes)<=3168 and ticks<1000
     g.s.close();assert p.wait(timeout=10)==0
    finally:
     if p.poll() is None:p.kill();p.wait()
   raw=(B/'stdout').read_bytes();assert len(raw)==7*2112 and len(writes)==3168
   stages=[struct.unpack_from('<16I',raw,i*2112) for i in range(7)];assert [x[2] for x in stages]==[10,20,11,21,30,40,50]
   images=[raw[64:1088],raw[2*2112+64:2*2112+1088],raw[5*2112+64:5*2112+1088]]
   assert images[:2]==[refs[scene*4096:scene*4096+1024],refs[scene*4096+1024:scene*4096+2048]]
   assert images[2]==bytes((i*37+13)&255 for i in range(1024))
   for f in range(3):
    for page in range(8):
     group=writes[(f*8+page)*132:(f*8+page+1)*132]
     assert [v&255 for pc,addr,v in group[:4]]==[0xb0+page,0x40,0x10,0]
     assert all(pc==0xc00184a4 for pc,addr,v in group[:4])
     assert all(pc==0xc001862c for pc,addr,v in group[4:])
     assert bytes(v&255 for pc,addr,v in group[4:])==images[f][128*page:128*(page+1)]
   (O/f'{vi}_{scene}.records.gz').write_bytes(gzip.compress(raw,mtime=0))
   (O/f'{vi}_{scene}.writes.gz').write_bytes(gzip.compress(b''.join(struct.pack('<III',*w) for w in writes),mtime=0))
   rows.append({'vsb':vi,'scene':scene,'writes':len(writes),'timer_reads_simulated':ticks})
   print('worker capture',vi,scene,len(writes),'timer reads',ticks,flush=True)
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
 (O/'results.json').write_text(json.dumps({'cases':rows,'timer':'GDB supplies synthetic r3 after timer register read; no VSB instruction changed'},indent=2)+'\n')
 print('PASS 16 workers: 2 V30 frames and 8-page Korg restoration; simulated GPIO/SPI/time')
if __name__=='__main__':main()
