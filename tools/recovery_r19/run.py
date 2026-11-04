#!/usr/bin/env python3
"""R19 constructor admission and shared UI subject. Native instructions unchanged."""
import gzip,hashlib,json,os,resource,struct,subprocess,sys
from pathlib import Path
import socket
import importlib.util
_spec=importlib.util.spec_from_file_location("r17_rsp",Path(__file__).resolve().parents[1]/"recovery_r17/rsp.py")
_rsp=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_rsp);RSP=_rsp.RSP
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert len(sys.argv)==3;os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r19');out=Path('reports/recovery_r19');build.mkdir(parents=True,exist_ok=True)
 def run(a):return subprocess.run(list(map(str,a)),check=True,timeout=90,capture_output=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror'];run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o']);rows=[]
 for vi,(path,h) in enumerate(zip(sys.argv[1:],HASHES)):
  blob=Path(path).read_bytes();assert len(blob)==0x200100 and sha(blob)==h;(build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r19/original.bin"\n.section .note.GNU-stack,"",%progbits\n');run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(31):
   compiled=subprocess.run([*arm,f'-DR19_CASE={case}','-c','tests/recovery_r19/native.c','-o',str(build/'probe.o')],capture_output=True,text=True)
   if compiled.returncode:print(compiled.stderr,flush=True);raise RuntimeError('compile')
   elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/'probe.trace'
   debug=None
   if case in (1,2,3,4,5,6,7,8,9,14,15,16,30):
    symbols={}
    for line in run(['llvm-objdump','-t',elf]).stdout.decode().splitlines():
     fields=line.split()
     if fields and fields[-1] in ('r19_ready','r19_injected_action','r19_injected_return','r19_injection_stack'):symbols[fields[-1]]=int(fields[0],16)
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    rawpath=build/'raw';errpath=build/'stderr'
    with rawpath.open('wb') as stdout,errpath.open('wb') as stderr:
     proc=subprocess.Popen(['qemu-arm','-g',str(port),'-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],stdout=stdout,stderr=stderr)
     try:
      g=RSP(port);assert g.cmd('?').startswith(('T05','S05'));g.bp(symbols['r19_ready']);assert g.resume().startswith(('T05','S05'));g.bp(symbols['r19_ready'],False)
      pc={1:0xc00707cc,2:0xc00707cc,3:0xc00707a4,4:0xc00707cc,5:0xc0070810,6:0xc00707cc,7:0xc00707cc,8:0xc00707cc,9:0xc00707cc,14:0xc007067c,15:0xc0070650,16:0xc007067c,30:0xc0070778}[case]
      before=g.mem(pc);g.bp(pc);during=g.mem(pc);assert before==during
      assert g.resume().startswith(('T05','S05'))
      regs=bytes.fromhex(g.regs());assert struct.unpack_from('<I',regs,60)[0]==pc
      if case==7:
       saved=g.regs();core=bytearray.fromhex(saved)
       for i,val in {0:4,13:symbols['r19_injection_stack']+8192,14:symbols['r19_injected_return'],15:symbols['r19_injected_action']}.items():struct.pack_into('<I',core,i*4,val)
       assert g.cmd('G'+core.hex())=='OK';stop=g.resume();assert stop.startswith('W57'),stop
       rc=proc.wait(timeout=5);debug={'stop_pc':hex(pc),'code_before':before,'code_breakpoint':during,'commands':g.commands.copy(),'constructor_resumed':False,'register_restore_exact':False,'interleaving':'Controlled exit87 with native constructor still active; no completed-registration claim'}
      else:
       if case==30:g.bp(pc,False)
       debug=g.inject({1:1,2:2,3:3,4:3,5:3,6:3,8:5,9:2,14:6,15:6,16:6,30:7}[case],symbols['r19_injected_action'],symbols['r19_injected_return'],symbols['r19_injection_stack']+8192)
       after=g.mem(pc);assert before==after
       if case!=30:g.bp(pc,False)
       debug.update(stop_pc=hex(pc),code_before=before,code_breakpoint=during,code_after=after,commands=g.commands.copy(),interleaving='Debugger-injected fixture context; not native scheduler')
       # Continue past a deliberate SIGSEGV stop so Linux delivers our handler.
       stop=g.resume()
       if stop.startswith(('T0b','S0b')):stop=g.cmd('C0b')
       assert stop.startswith('W'),stop
       rc=proc.wait(timeout=5)
     finally:
      if proc.poll() is None:proc.kill();proc.wait()
    raw=rawpath.read_bytes()
   else:
    try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=.5 if case==26 else 5);rc=r.returncode;raw=r.stdout
    except subprocess.TimeoutExpired as e:rc='timeout';raw=e.stdout or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0));assert len(raw)%2112==0;events=[]
   for n in range(0,len(raw),2112):
    h=struct.unpack_from('<16I',raw,n);events.append({'header':list(h),'source_sha256':sha(raw[n+64:n+1088]),'shadow_sha256':sha(raw[n+1088:n+2112])})
   rows.append(dict(vsb=vi,case=case,exit=rc,events=events,debugger=debug));print(vi,case,rc,[(e['header'][2],e['header'][3],hex(e['header'][4])) for e in events],flush=True)
   (out/'results.json').write_text(json.dumps({'vsb_sha256':HASHES,'cases':rows},indent=2)+'\n')
  assert sha(Path(path).read_bytes())==HASHES[vi]
 assert len(rows)==62
if __name__=='__main__':main()
