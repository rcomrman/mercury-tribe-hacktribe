#!/usr/bin/env python3
"""New R20 laboratory only. Read-only native image, guarded free boundaries."""
import gzip,hashlib,importlib.util,json,os,resource,socket,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('rsp',ROOT/'tools/recovery_r17/rsp.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class RSP(module.RSP):
 def __init__(self,port):self.wire_commands=[];super().__init__(port)
 def cmd(self,command):
  self.wire_commands.append('G<registers>' if command.startswith('G') else command)
  return super().cmd(command)
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
# (instruction at which execution is suspended, fixture action, final controlled exit)
PLANS={1:[(0xc00707a4,1,False)],2:[(0xc00707cc,1,False)],3:[(0xc0070810,1,False)],
 4:[(0xc007067c,2,False)],5:[(0xc007067c,3,False)],6:[(0xc0041bb4,6,True)],
 7:[(0xc0085204,7,True)],8:[(0xc00851d0,4,False),(0xc0041bb4,6,True)],
 9:[(0xc00851d0,5,False)],21:[(0xc00853a8,8,False),(0xc0041bb4,6,True)],23:[(0xc0070650,3,False)]}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert len(sys.argv)==3;os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 build=ROOT/'build/recovery_r20';out=ROOT/'reports/recovery_r20';build.mkdir(parents=True,exist_ok=True)
 def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,timeout=60)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip(sys.argv[1:],HASHES)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and sha(blob)==h
  (build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r20/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(24):
   try:run([*arm,f'-DR20_CASE={case}','-c','tests/recovery_r20/native.c','-o',build/'probe.o'])
   except subprocess.CalledProcessError as e:print(e.stderr.decode(),flush=True);raise
   elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf])
   symbols={}
   for line in run(['llvm-objdump','-t',elf]).stdout.decode().splitlines():
    f=line.split()
    if f and f[-1] in ('r20_ready','r20_injected_action','r20_injected_return','r20_injection_stack'):symbols[f[-1]]=int(f[0],16)
   with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   trace=build/'probe.trace';rawpath=build/'raw';errpath=build/'stderr';debug=[]
   with rawpath.open('wb') as stdout,errpath.open('wb') as stderr:
    proc=subprocess.Popen(['qemu-arm','-g',str(port),'-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],stdout=stdout,stderr=stderr)
    try:
     g=RSP(port);assert g.cmd('?').startswith(('T05','S05'))
     # A native free entry is always forbidden, even for purportedly quiet objects.
     g.bp(0xc0028dd4);g.bp(symbols['r20_ready']);assert g.resume().startswith(('T05','S05'));g.bp(symbols['r20_ready'],False)
     assert struct.unpack_from('<I',bytes.fromhex(g.regs()),60)[0]==symbols['r20_ready']
     controlled=False
     for pc,action,last in PLANS.get(case,[]):
      before=g.mem(pc);g.bp(pc);assert g.mem(pc)==before
      stop=g.resume();assert stop.startswith(('T05','S05')),stop
      saved=g.regs();assert struct.unpack_from('<I',bytes.fromhex(saved),60)[0]==pc,('unexpected stop',vi,case,g.regs())
      if last:
       core=bytearray.fromhex(saved)
       for i,v in {0:action,13:symbols['r20_injection_stack']+8192,14:symbols['r20_injected_return'],15:symbols['r20_injected_action']}.items():struct.pack_into('<I',core,i*4,v)
       assert g.cmd('G'+core.hex())=='OK';assert g.resume().startswith('W57');controlled=True
       debug.append(dict(pc=hex(pc),action=action,code_before=before,register_restore_exact=False,resumed=False,core=list(struct.unpack_from('<16I',bytes.fromhex(saved)))))
      else:
       entry=g.inject(action,symbols['r20_injected_action'],symbols['r20_injected_return'],symbols['r20_injection_stack']+8192)
       assert g.mem(pc)==before;g.bp(pc,False);entry.update(pc=hex(pc),action=action,code_before=before,code_after=g.mem(pc),resumed=True);debug.append(entry)
     if not controlled:
      if case==13:
       # RSP timeout is host termination, never native cessation. Keep final records.
       g.s.settimeout(1)
       try:stop=g.resume();raise AssertionError(('unexpected timeout-case stop',stop))
       except socket.timeout:proc.kill();proc.wait();rc='timeout'
      else:
       stop=g.resume()
       if stop.startswith(('T0b','S0b')):stop=g.cmd('C0b')
       assert stop.startswith('W'),('unexpected stop or forbidden free',vi,case,stop,g.regs())
       rc=proc.wait(timeout=5)
     else:rc=proc.wait(timeout=5)
     commands=g.commands.copy();wire_commands=g.wire_commands.copy();g.s.close()
    finally:
     if proc.poll() is None:proc.kill();proc.wait()
   raw=rawpath.read_bytes();assert raw and len(raw)%2112==0
   events=[]
   for offset in range(0,len(raw),2112):
    header=list(struct.unpack_from('<16I',raw,offset));events.append(dict(header=header,source_sha256=sha(raw[offset+64:offset+1088]),shadow_sha256=sha(raw[offset+1088:offset+2112])))
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0));(out/f'{vi}_{case}.stderr.gz').write_bytes(gzip.compress(errpath.read_bytes(),mtime=0))
   row=dict(vsb=vi,case=case,exit=rc,events=events,debugger=debug,commands=commands,wire_commands=wire_commands,free_entry_guard='0xc0028dd4',fixture_sha256=sha(elf.read_bytes()))
   rows.append(row);(out/'results.json').write_text(json.dumps(dict(vsb_sha256=HASHES,cases=rows),indent=2)+'\n')
   print(vi,case,rc,[(e['header'][2],e['header'][3],hex(e['header'][4])) for e in events if e['header'][2]<100],flush=True)
   assert not any(e['header'][2]==99 for e in events),('fixture assertion',vi,case)
  assert sha(Path(path).read_bytes())==h
 assert len(rows)==48
if __name__=='__main__':main()
