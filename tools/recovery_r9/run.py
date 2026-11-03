#!/usr/bin/env python3
"""R9 LCD experiments. Read-only original VSB; never map peripheral addresses."""
import argparse,gzip,hashlib,json,os,resource,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def run(cmd,**kw):return subprocess.run(list(map(str,cmd)),check=True,timeout=90,**kw)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);p.add_argument('--explore',action='store_true');a=p.parse_args()
 os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r9');out=Path('reports/recovery_r9');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o'])
 rows=[]
 for vi,(path,h) in enumerate(zip((a.custom,a.backup),HASHES)):
  blob=path.read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r9/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(20):
   run([*arm,f'-DR9_CASE={case}','-c','tests/recovery_r9/lcd.c','-o',build/'probe.o'])
   elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/f'{vi}_{case}.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout;err=r.stderr
   except subprocess.TimeoutExpired as ex:rc='timeout';raw=ex.stdout or b'';err=ex.stderr or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
   events=[]
   assert len(raw)%2112==0,(vi,case,len(raw))
   for pos in range(0,len(raw),2112):
    h0=struct.unpack_from('<16I',raw,pos);assert h0[0]==0x52394c43 and h0[1]==case and h0[6:8]==(0x39,0xc5)
    src=raw[pos+64:pos+1088];shadow=raw[pos+1088:pos+2112]
    events.append({'header':h0,'source_sha256':hashlib.sha256(src).hexdigest(),'shadow_sha256':hashlib.sha256(shadow).hexdigest(),'different_bytes':sum(x!=y for x,y in zip(src,shadow))})
   text=trace.read_text();faults=[e['header'][3] for e in events if e['header'][2]==90]
   print(vi,case,'exit',rc,'faults',[hex(x) for x in faults], 'stages',[e['header'][2] for e in events],flush=True)
   if not a.explore:
    expected_fault={4:0xbc,5:0x01e260bc,7:0xbc,9:0xbc,10:0xbc,11:0x01e260bc,12:0x01c41010,15:0xbc,18:0xbc}
    assert rc==(88 if case in expected_fault else 0),(vi,case,rc,err)
    assert faults==([expected_fault[case]] if case in expected_fault else [])
    assert not any(e['header'][2]==99 for e in events)
   if not a.explore:
    states={}
    for pos in range(0,len(raw),2112):
     stage=struct.unpack_from('<16I',raw,pos)[2]
     states[stage]=(raw[pos+64:pos+1088],raw[pos+1088:pos+2112])
    initial=bytes((i*37+13)&255 for i in range(1024));changed=bytearray(initial);changed[401]^=0x80;changed=bytes(changed)
    if case in (4,10,11,15):assert states[90]==(changed,changed)
    if case==5:
     assert states[90]==(bytes(1024),bytes(1024))
     assert events[-1]['header'][13:16]==(0xc031bb20,0x01e26000,0x01c41000)
    if case==3:assert states[20]==(changed,initial)
    if case==14:assert states[20]==(b'\xee'*1024,b'\x11'*128+b'\xee'*896)
    if case==15:assert states[91]==(changed,changed) and events[-1]['header'][3:5]==(0,1)
    if case in (1,6,8,17,19):assert '0xc0015ab4:' not in text
    if case in (2,3,6,8,16,17,19):assert '0xc001613c:' not in text
    if case==2:assert '0xc0015ab4:' in text and all(e['header'][9]&0xff00==0x100 for e in events if e['header'][2]>=2)
    if case in (4,7,10,11,15,18):assert '0xc001613c:' in text
    if case==9:assert '0xc0016c18:' in text and '0xc0015ab4:' not in text
    if case==12:assert '0xc00117c8:' in text
   rows.append({'vsb':vi,'case':case,'exit':rc,'events':events,'fault_addresses':faults})
  assert hashlib.sha256(path.read_bytes()).hexdigest()==h
 if not a.explore:
  for x,y in zip(rows[:20],rows[20:]):assert x['events']==y['events'] and x['exit']==y['exit']
 (out/'lcd_results.json').write_text(json.dumps({'exploratory':a.explore,'vsb_sha256':HASHES,'cases':rows},indent=2)+'\n')
if __name__=='__main__':main()
