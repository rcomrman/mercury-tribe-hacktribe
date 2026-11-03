#!/usr/bin/env python3
"""R10 native configuration and countdown experiments. Read-only original VSB; never map peripheral addresses."""
import argparse,gzip,hashlib,json,os,resource,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def run(cmd,**kw):return subprocess.run(list(map(str,cmd)),check=True,timeout=90,**kw)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);p.add_argument('--explore',action='store_true');a=p.parse_args()
 os.chdir(ROOT);resource.setrlimit(resource.RLIMIT_CORE,(0,0));build=Path('build/recovery_r10');out=Path('reports/recovery_r10');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o'])
 rows=[]
 for vi,(path,h) in enumerate(zip((a.custom,a.backup),HASHES)):
  blob=path.read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h
  (build/'original.bin').write_bytes(blob[256:]);(build/'original.S').write_text('.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r10/original.bin"\n.section .note.GNU-stack,"",%progbits\n')
  run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case in range(13):
   run([*arm,f'-DR10_CASE={case}','-c','tests/recovery_r10/native.c','-o',build/'probe.o'])
   elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf]);trace=build/f'{vi}_{case}.trace'
   try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=3);rc=r.returncode;raw=r.stdout;err=r.stderr
   except subprocess.TimeoutExpired as ex:rc='timeout';raw=ex.stdout or b'';err=ex.stderr or b''
   (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
   events=[]
   assert len(raw)%2112==0,(vi,case,len(raw))
   for pos in range(0,len(raw),2112):
    h0=struct.unpack_from('<16I',raw,pos);assert h0[0]==0x52394c43 and h0[1]==case and h0[6]==0x39 and (h0[7] in (0,0xc5) if case==11 else h0[7]==0xc5)
    src=raw[pos+64:pos+1088];shadow=raw[pos+1088:pos+2112]
    events.append({'header':h0,'source_sha256':hashlib.sha256(src).hexdigest(),'shadow_sha256':hashlib.sha256(shadow).hexdigest(),'different_bytes':sum(x!=y for x,y in zip(src,shadow))})
   text=trace.read_text();faults=[e['header'][3] for e in events if e['header'][2]==90]
   print(vi,case,'exit',rc,'faults',[hex(x) for x in faults], 'stages',[e['header'][2] for e in events],flush=True)
   if not a.explore:
    expected_fault={0:0x01f0d020,1:0x01f0d004,2:0x68000010,3:0x01c41000,4:0x01c42034,5:0x01c21004,7:0x01f0e000,8:0xbc,11:0xc06a2894}
    assert rc==(88 if case in expected_fault else 0),(vi,case,rc,err)
    assert faults==([expected_fault[case]] if case in expected_fault else [])
    assert not any(e['header'][2]==99 for e in events)
    stages={e['header'][2]:e for e in events}
    if case==8:
     assert [e['header'][2] for e in events]==[0,1,2,3,4,5,90]
     assert stages[1]['header'][3:5]==(0,1) and stages[2]['header'][3:5]==(1,20)
     assert stages[3]['header'][3:5]==(1,20) and stages[4]['header'][3:5]==(0,1)
     assert stages[90]['different_bytes']==0 and '0xc002a71c:' in text
    if case in (9,12):assert '0xc001613c:' not in text
    if case==11:
     assert '0xc00298bc:' in text and '0xc00299f4:' not in text
     assert stages[90]['header'][7]==0 and '0xc001531c:' in text
   rows.append({'vsb':vi,'case':case,'exit':rc,'events':events,'fault_addresses':faults})
  assert hashlib.sha256(path.read_bytes()).hexdigest()==h
 if not a.explore:
  for x,y in zip(rows[:13],rows[13:]):assert x['events']==y['events'] and x['exit']==y['exit']
 (out/'results.json').write_text(json.dumps({'exploratory':a.explore,'vsb_sha256':HASHES,'cases':rows},indent=2)+'\n')
if __name__=='__main__':main()
