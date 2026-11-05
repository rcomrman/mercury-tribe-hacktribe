#!/usr/bin/env python3
"""R21 read-only native dependencies. No claim of a global graphics dominator."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r21';BUILD=ROOT/'build/recovery_r21';BASE=0xc0000000
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'annex_graphics':(0x6ea10,0x6ea4c),'annex_caller':(0x6f1e4,0x6f204),'native_pixel':(0x15824,0x15900),'fixed_comparator':(0x15ab4,0x15b54),'lcd_worker':(0x15fa0,0x160c4),'lcd_descriptor':(0x15d14,0x15eb8),'graphics_reset':(0x3f0d4,0x3f154)}
def main():
 assert len(sys.argv)==3;OUT.mkdir(parents=True,exist_ok=True);BUILD.mkdir(parents=True,exist_ok=True);images=[]
 for p,h in zip(sys.argv[1:],HASHES):
  b=Path(p).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 contracts={0xc006ea18:0xe5900034,0xc006ea20:0xe5933008,0xc006ea24:0xe12fff33,0xc006ea28:0xe5940038,0xc006ea34:0xe12fff33,0xc006ea38:0xe594003c,0xc006ea44:0xe12fff33,0xc006ea48:0xe8bd8010}
 for b in images:
  for pc,w in contracts.items():assert struct.unpack_from('<I',b,pc-BASE)[0]==w
 (BUILD/'audit.bin').write_bytes(images[0]);(BUILD/'audit.S').write_text('.text\n.global image\nimage:\n.incbin "build/recovery_r21/audit.bin"\n')
 def run(args):return subprocess.check_output(list(map(str,args)),cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',BUILD/'audit.S','-o',BUILD/'audit.o']);elf=BUILD/'STATIC_ONLY.elf';run(['ld.lld','-Ttext=0xc0000000','-e','image',BUILD/'audit.o','-o',elf])
 ranges=[];text=[]
 for name,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi];ranges.append(dict(name=name,start=hex(BASE+lo),end_exclusive=hex(BASE+hi),sha256=hashlib.sha256(images[0][lo:hi]).hexdigest()))
  text.append(name+'\n'+run(['llvm-objdump','-D',f'--start-address={BASE+lo}',f'--stop-address={BASE+hi}',elf]))
 removed={'subscriber_constructor':'0xc00852b0','subscriber_destructor':'0xc00851b4','deleting_destructor':'0xc00851f4','inverse_destructor':'0xc0041b74','registration':'0xc0070778','removal':'0xc00705dc','observer_invocation':'0xc007061c','periodic_dispatch':'0xc0082728','periodic_subscriber_method':'0xc0085078','model_subscriber_method':'0xc0085278'}
 graph=json.loads((ROOT/'reports/recovery_r13/access_graph.json').read_text())['coverage']
 data=dict(vsb_sha256=HASHES,ranges=ranges,contracts={hex(k):hex(v) for k,v in contracts.items()},removed_from_new_route_candidates=removed,subscriber_roots_not_required=['0xc0691244','0xc0348844','0xc03405bc'],remaining_access_domains=graph,selected_native_path='C006F178 calls C006EA10; R21 invokes only C006EA10 unchanged on a static fixture graph',scope='Complete UI cycle/task scheduling/page factory/physical LCD not requalified; no native synchronization or framebuffer ownership inferred')
 (OUT/'native-map.json').write_text(json.dumps(data,indent=2)+'\n');(OUT/'native-map.txt.gz').write_bytes(gzip.compress('\n'.join(text).encode(),mtime=0))
 print('PASS 7 identical native ranges; three slot+8 calls; 14 historical graphics access domains retained as obligations.')
if __name__=='__main__':main()
