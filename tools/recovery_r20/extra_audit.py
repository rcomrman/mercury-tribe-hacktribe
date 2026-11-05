#!/usr/bin/env python3
"""Supplement phase-1 evidence without replacing it. Bounded static audit."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=0xc0000000
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'native_allocation_site':(0x65298,0x652bc),'subscriber_full_constructor':(0x852b0,0x85408),'model_callback':(0x85278,0x852b0),'model_constructor':(0x82848,0x828e0),'model_root_getter':(0x30d28,0x30d5c),'destructors':(0x851b4,0x85218),'inverse':(0x41b74,0x41bc4),'retained_callback':(0x85078,0x85098),'invocation':(0x705dc,0x70818)}
def main():
 assert len(sys.argv)==3;images=[]
 for path,h in zip(sys.argv[1:],HASHES):
  b=Path(path).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 contracts={0xc0065298:0xe3a0004c,0xc00652a4:0xeb008001,0xc00853a4:0xe3a0200a,0xc00853a8:0xebffacf2,0xc00853d0:0xe2820004,0xc00853d4:0xe1a01008,0xc00853e0:0xebfface4,0xc0085400:0xc0085078,0xc0085404:0xc0085278,0xc0030d58:0xc03405bc,0xc0085280:0xebfeaea8,0xc00852a0:0x15c43048}
 for image in images:
  for pc,w in contracts.items():assert struct.unpack_from('<I',image,pc-BASE)[0]==w,hex(pc)
 build=ROOT/'build/recovery_r20';build.mkdir(parents=True,exist_ok=True)
 (build/'supplement.bin').write_bytes(images[0]);(build/'supplement.S').write_text('.text\n.global image\nimage:\n.incbin "build/recovery_r20/supplement.bin"\n')
 def run(a):return subprocess.check_output(list(map(str,a)),cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',build/'supplement.S','-o',build/'supplement.o']);elf=build/'SUPPLEMENT_STATIC_ONLY.elf';run(['ld.lld','-Ttext=0xc0000000','-e','image',build/'supplement.o','-o',elf])
 ranges=[];text=[]
 for name,(lo,hi) in RANGES.items():
  assert images[0][lo:hi]==images[1][lo:hi];ranges.append(dict(name=name,start=hex(BASE+lo),end_exclusive=hex(BASE+hi),sha256=hashlib.sha256(images[0][lo:hi]).hexdigest()))
  text.append(name+'\n'+run(['llvm-objdump','-D',f'--start-address={BASE+lo}',f'--stop-address={BASE+hi}',elf]))
 out=ROOT/'reports/recovery_r20';(out/'supplement.txt.gz').write_bytes(gzip.compress('\n'.join(text).encode(),mtime=0))
 (out/'supplement.json').write_text(json.dumps(dict(vsb_sha256=HASHES,contracts={hex(k):hex(v) for k,v in contracts.items()},ranges=ranges,native_owner_allocation_bytes=76,relations=[dict(subject='*C0691244',key='owner+0x38',context='owner',method='C0085078',period=10),dict(subject='(*C03405BC)+4',key='owner+0x38',context='owner',method='C0085278',period=0)],authority='Unknown last-owner authority on all three globals; no free certificate',limits=['Local instruction contracts only','Runtime model fixture is seeded explicitly, not a native heap allocation','No exhaustive computed aliases/callers/context coverage']),indent=2)+'\n')
 print('PASS 9 identical ranges; native allocation76 and second relation to model+4 distinguished from associated UI root')
if __name__=='__main__':main()
