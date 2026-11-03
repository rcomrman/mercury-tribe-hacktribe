#!/usr/bin/env python3
"""Native page transition experiments. Run R2 first to generate verified inputs."""
import gzip,hashlib,json,os,resource,struct,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
if len(sys.argv)!=3:raise SystemExit('usage: run.py custom.VSB backup.VSB')
root=Path(__file__).resolve().parents[2];os.chdir(root);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
build=Path('build/recovery_r8');out=Path('reports/recovery_r8');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
hashes=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-fstack-usage']
def run(c):subprocess.run(list(map(str,c)),check=True,timeout=90)
allresults=[]
for vi,(p,h) in enumerate(zip(sys.argv[1:],hashes)):
 blob=Path(p).read_bytes();assert hashlib.sha256(blob).hexdigest()==h
 Path('build/recovery_r2/original.bin').write_bytes(blob[256:]);run([*arm,'-c','build/recovery_r2/original.S','-o',build/'original.o'])
 for case in range(9):
  run([*arm,f'-DR8_CASE={case}','-c','tests/recovery_r8/interleave.c','-o',build/'probe.o'])
  usage=build/'probe.su'
  if usage.exists():(out/f'{vi}_{case}.stack_usage.txt').write_bytes(usage.read_bytes())
  elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld','build/recovery_r2/start.o',build/'probe.o',build/'original.o','-o',elf])
  trace=build/f'{vi}_{case}.trace'
  try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),'-strace',str(elf)],capture_output=True,timeout=2 if case==0 else 10);rc=r.returncode;raw=r.stdout;err=r.stderr
  except subprocess.TimeoutExpired as e:rc='timeout';raw=e.stdout or b'';err=e.stderr or b''
  print(vi,case,rc,err[-150:],flush=True)
  (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
  events=[];shots={};pos=0
  while pos<len(raw):
   e=struct.unpack_from('<16I',raw,pos);pos+=64;events.append(e)
   if e[1]==100:shots[e[3]]=raw[pos:pos+1024];pos+=1024
  assert pos==len(raw)
  text=trace.read_text()
  assert rc==('timeout' if case==0 else 0),(vi,case,rc)
  if case==0:assert '0xc0060f3c:' in text
  else:
   assert shots[1]==Path('build/recovery_r1/frames.bin').read_bytes()[:1024]
   assert '0xc006f178:' in text
  if case==1:
   assert '0xc006e8bc:' in text
   r7=json.loads(Path('reports/recovery_r7/results.json').read_text())[7]
   assert hashlib.sha256(shots[2]).hexdigest()==r7['snapshots']['2']
  if rc==0:
   summary=next(e for e in events if e[1]==26)
   assert summary[3]==12
   assert summary[4]==(1 if case in (1,3,4,7) else 0)
   assert summary[5]==(1 if case==3 else (64 if case==8 else 0))
  if case==6:assert next(e for e in events if e[1]==25)[3:6]==(0,1,0)
  if case==7:assert next(e for e in events if e[1]==25)[3:6]==(1,1,1)
  row={'vsb':vi,'case':case,'exit':rc,'events':events,'snapshots':{str(k):hashlib.sha256(v).hexdigest() for k,v in shots.items()}}
  allresults.append(row);print(vi,case,rc,'validated',flush=True)
  if vi==0:
   ims=[]
   for stage in [0,1,2,3]:
    if stage not in shots:continue
    b=shots[stage];im=Image.new('1',(128,64));im.putdata([255*((b[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);im=im.resize((512,256));im.save(out/f'case{case}_stage{stage}.png');ims.append(im.convert('P'))
   if ims and case in (1,):ims[0].save(out/f'case{case}.gif',save_all=True,append_images=ims[1:],duration=800,loop=0)
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
for x,y in zip(allresults[:9],allresults[9:]):assert x['events']==y['events'] and x['snapshots']==y['snapshots']
(out/'results.json').write_text(json.dumps(allresults,indent=2)+'\n')

symbols=subprocess.run(['llvm-objdump','-t',str(elf)],capture_output=True,text=True,check=True).stdout
(out/'guard_symbols.txt').write_text('\n'.join(line for line in symbols.splitlines() if 'guarded_' in line or 'gate.' in line)+'\n')
