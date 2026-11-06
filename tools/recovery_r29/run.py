#!/usr/bin/env python3
"""EXIT injection at ARM boundaries, serialized drain; synthetic peripherals."""
import gzip,hashlib,importlib.util,json,os,socket,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];B=R/'build/recovery_r29';O=R/'reports/recovery_r29'
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
S=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
sp=importlib.util.spec_from_file_location('rsp',R/'tools/recovery_r17/rsp.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60)
def main():
 assert len(sys.argv)==3;os.chdir(R);B.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Isrc','-Wno-unused-function'];objs=[]
 for n,src in enumerate(['tests/recovery_r2/start.S',*S]):
  o=B/f'{n}.o';run([*arm,'-c',src,'-o',o]);objs.append(o)
 rows=[]
 for vi,(path,h) in enumerate(zip(sys.argv[1:],H)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (B/'original.bin').write_bytes(blob[256:]);(B/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r29/original.bin"\n.section .note.GNU-stack,"",%progbits\n');run([*arm,'-c',B/'original.S','-o',B/'original.o'])
  for case in range(8):
   run([*arm,f'-DCASE={case}','-c','tests/recovery_r29/controller.c','-o',B/'probe.o'])
   elf=B/'LINUX_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',objs[0],B/'probe.o',*objs[1:],B/'original.o','-o',elf])
   sym={}
   for line in run(['llvm-objdump','-t',elf]).stdout.decode().splitlines():
    f=line.split()
    if f and f[-1] in ('r29_injected_action','r29_injected_return','r29_injection_stack'):sym[f[-1]]=int(f[0],16)
   assert len(sym)==3
   with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   with (B/'out').open('wb') as out,(B/'err').open('wb') as err:
    p=subprocess.Popen(['qemu-arm','-cpu','arm926','-g',str(port),str(elf)],stdout=out,stderr=err)
    try:
     g=mod.RSP(port);g.s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);assert g.cmd('?').startswith(('T05','S05'))
     target={1:0xc0015b38,2:0xc0015b3c,3:0xc001613c,4:0xc00160a4,5:0xc001862c,6:0xc00160a4,7:0xc001862c}.get(case)
     points=set((0xc00184a4,0xc001862c,0xc00163b8));
     if target:points.add(target)
     for x in points:g.bp(x)
     data=[];ticks=0;ndata=0;injected=False;injection=None
     while True:
      stop=g.resume()
      if stop.startswith('W'):break
      assert stop.startswith(('T05','S05')),stop
      raw=bytearray.fromhex(g.regs());reg=struct.unpack_from('<16I',raw);pc=reg[15];assert pc in points
      if pc==0xc00163b8:
       ticks+=1;struct.pack_into('<I',raw,12,ticks*1500);assert g.cmd('G'+raw.hex())=='OK'
      if pc in (0xc00184a4,0xc001862c):
       data.append((pc,reg[3]+0x3c,reg[2]));ndata+=pc==0xc001862c
      due=target==pc and not injected and (case not in (4,5,6,7) or ndata=={4:128,5:64,6:1024,7:385}[case])
      if due:
       injection=g.inject(2 if case==7 else 1,sym['r29_injected_action'],sym['r29_injected_return'],sym['r29_injection_stack']+8192);assert injection['register_restore_exact'];injected=True
       if case==7:
        data.pop();ndata-=1;break # do not execute interrupted store; no native recovery asserted
      g.bp(pc,False);assert g.cmd('s').startswith(('T05','S05'));g.bp(pc)
      assert len(data)<=2112 and ticks<1000
     g.s.close()
     if case==7:p.kill();p.wait()
     else:assert p.wait(timeout=10)==0
    finally:
     if p.poll() is None:p.kill();p.wait()
   raw=(B/'out').read_bytes();assert len(raw)%2112==0
   headers=[struct.unpack_from('<16I',raw,i) for i in range(0,len(raw),2112)]
   assert all(x[0]==0x52394c43 and x[1]==2900+case and x[2]!=99 for x in headers)
   assert [x[2] for x in headers]==([101,102,103,106] if case==7 else [101,102,103,104,110,105,101,120])
   assert (case==0 or injected) and len(data)==(400 if case==7 else 1056 if case==0 else 2112)
   outwrites=b''.join(struct.pack('<III',*w) for w in data)
   (O/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(O/f'{vi}_{case}.writes.gz').write_bytes(gzip.compress(outwrites,mtime=0))
   rows.append({'vsb':vi,'case':case,'exit_pc':hex(target) if target else 'before_worker','data_writes':ndata,'writes':len(data),'injected':injected,'register_restore_exact':bool(injection and injection['register_restore_exact']),'timer_reads':ticks})
   print('EXIT',vi,case,'writes',len(data),'injected',injected,flush=True)
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
 (O/'results.json').write_text(json.dumps({'cases':rows,'scope':'synthetic timer and sequential debugger injection; no native halt or real concurrency'},indent=2)+'\n')
 print('PASS 14 ARM EXIT runs and 2 controlled fault stops; fault recovery BLOCKED')
if __name__=='__main__':main()
