#!/usr/bin/env python3
"""Native page transition experiments. Run R2 first to generate verified inputs."""
import gzip,hashlib,json,os,resource,struct,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2];os.chdir(root);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
build=Path('build/recovery_r4');out=Path('reports/recovery_r4');build.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
hashes=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
def run(c):subprocess.run(list(map(str,c)),check=True,timeout=90)
allresults=[]
for vi,(p,h) in enumerate(zip(sys.argv[1:],hashes)):
 blob=Path(p).read_bytes();assert hashlib.sha256(blob).hexdigest()==h
 Path('build/recovery_r2/original.bin').write_bytes(blob[256:]);run([*arm,'-c','build/recovery_r2/original.S','-o',build/'original.o'])
 for case in range(16):
  run([*arm,f'-DNIGHT_CASE={case}','-c','tests/recovery_r4/events.c','-o',build/'probe.o'])
  elf=build/'LINUX_TEST_ONLY.elf';run(['ld.lld','-T','tests/recovery_r1/linux_test.ld','build/recovery_r2/start.o',build/'probe.o',build/'original.o','-o',elf])
  trace=build/f'{vi}_{case}.trace'
  try:r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),str(elf)],capture_output=True,timeout=5);rc=r.returncode;raw=r.stdout
  except subprocess.TimeoutExpired as e:rc='timeout';raw=e.stdout or b''
  assert rc==(-11 if case==15 else 0),(vi,case,rc)
  print(vi,case,rc,flush=True)
  (out/f'{vi}_{case}.records.gz').write_bytes(gzip.compress(raw,mtime=0));(out/f'{vi}_{case}.trace.gz').write_bytes(gzip.compress(trace.read_bytes(),mtime=0))
  events=[];shots={};pos=0
  while pos<len(raw):
   e=struct.unpack_from('<16I',raw,pos);pos+=64;events.append(e)
   if e[1]==100:shots[e[3]]=raw[pos:pos+1024];pos+=1024
  assert pos==len(raw)
  text=trace.read_text()
  if case!=15:assert '0xc0083848:' in text
  if case in (0,1,2,3,5,6,7,11,12,13,14):assert '0xc0083fe8:' in text
  if case in (0,1,5,6,7,12):assert '0xc006e8bc:' in text
  if case in (6,7):assert '0xc006bc88:' in text and '0xc0083d28:' in text
  row={'vsb':vi,'case':case,'exit':rc,'events':events,'snapshots':{str(k):hashlib.sha256(v).hexdigest() for k,v in shots.items()}}
  allresults.append(row);print(vi,case,rc,'validated',flush=True)
  if vi==0:
   ims=[]
   for stage in [900,0,1,2]:
    if stage not in shots:continue
    b=shots[stage];im=Image.new('1',(128,64));im.putdata([255*((b[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);im=im.resize((512,256));im.save(out/f'case{case}_stage{stage}.png');ims.append(im.convert('P'))
   if case in (1,2,3):ims[0].save(out/f'case{case}.gif',save_all=True,append_images=ims[1:],duration=800,loop=0)
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
for x,y in zip(allresults[:16],allresults[16:]):assert x['events']==y['events'] and x['snapshots']==y['snapshots']
(out/'results.json').write_text(json.dumps(allresults,indent=2)+'\n')
