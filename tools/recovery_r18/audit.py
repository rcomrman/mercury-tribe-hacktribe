#!/usr/bin/env python3
"""R18 conservative instruction-CFG reachability; candidates never prove execution or ownership."""
import gzip,hashlib,json,struct,subprocess,sys
from collections import deque,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r18';BUILD=ROOT/'build/recovery_r18';BASE=0xc0000000
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert len(sys.argv)==3;BUILD.mkdir(parents=True,exist_ok=True)
 imgs=[]
 for p,h in zip(sys.argv[1:],HASHES):
  b=Path(p).read_bytes();assert len(b)==0x200100 and sha(b)==h;imgs.append(b[256:])
 b=imgs[0];word=lambda pc:struct.unpack_from('<I',b,pc-BASE)[0]
 old=json.loads((ROOT/'reports/recovery_r17/audit.json').read_text());targets={int(t,16):v for t,v in old['references'].items()}
 def branch(pc,w):
  off=w&0xffffff;off-=0x1000000 if off&0x800000 else 0
  return (pc+8+4*off)&0xffffffff
 refs={t:[] for t in targets};indirect_all=[]
 def indirect(w):
  return w&0x0ffffff0 in (0x012fff10,0x012fff30) or (w&0x0e100000==0x08100000 and w&0x8000) or (w&0x0c100000==0x04100000 and w>>12&15==15) or (w&0x0c000000==0 and w>>12&15==15 and w>>21&15 not in (8,9,10,11))
 for off in range(0,len(b),4):
  pc=BASE+off;w=word(pc)
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   t=branch(pc,w)
   if t in refs:refs[t].append(pc)
 for t,x in targets.items():assert list(map(hex,refs[t]))==x['direct_branch_candidates']
 # Actual task records preserved from R11; reachability below is purely syntactic.
 seeds={f'task_{i+1}':struct.unpack_from('<8I',b,0xa37a8+32*i)[2] for i in range(10)}
 seeds.update(irq_15=0xc0025798,ui_virtual_consumer=0xc0083848,services_dispatch=0xc002d684,periodic_observer=0xc0082728)
 allsites={p for sites in refs.values() for p in sites};reaches={};witnesses={};summaries={}
 for name,start in seeds.items():
  todo=deque([start]);parent={start:None};hits={};holes=[]
  while todo:
   pc=todo.popleft()
   if not BASE<=pc<BASE+len(b) or pc%4:continue
   w=word(pc);cond=w>>28
   if pc in allsites:
    path=[];p=pc
    while p is not None:path.append(p);p=parent[p]
    hits[pc]=list(reversed(path))
   if cond==15:continue # unconditional extension encodings not decoded here
   edges=[]
   if w&0x0e000000==0x0a000000:
    edges.append(branch(pc,w))
    if w&0x01000000 or cond!=14:edges.append(pc+4)
   elif indirect(w):
    holes.append(pc)
    # Known LR return / indirect jump ends; BLX-register can return, target unresolved.
    if w&0x0ffffff0==0x012fff30 or cond!=14:edges.append(pc+4)
   else:edges.append(pc+4)
   for p in edges:
    if BASE<=p<BASE+len(b) and p%4==0 and p not in parent:parent[p]=pc;todo.append(p)
  reaches[name]=set(hits);witnesses[name]={hex(p):[hex(x) for x in path] for p,path in hits.items()}
  summaries[name]={'root':hex(start),'visited':len(parent),'observer_candidate_sites':len(hits),'unresolved_pc_transfers':list(map(hex,holes)),'status':'SYNTACTIC_POSSIBILITY_ONLY'}
 # One disassembly for all snippets, not heuristic semantic class labels.
 (BUILD/'image.bin').write_bytes(b);(BUILD/'image.S').write_text('.text\n.global image\nimage:\n.incbin "build/recovery_r18/image.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',BUILD/'image.S','-o',BUILD/'image.o']);elf=BUILD/'STATIC_ONLY.elf';run(['ld.lld','-Ttext=0xc0000000','-e','image',BUILD/'image.o','-o',elf])
 text=run(['llvm-objdump','-D',elf]);lines={int(m[1],16):m[2] for line in text.splitlines() if (m:=__import__('re').match(r'^\s*([0-9a-f]{8}):\s*(.*)',line))}
 rows=[];snippets=[]
 for t,sites in refs.items():
  for pc in sites:
   lo=max(BASE,pc-48);hi=pc+20;assert imgs[0][lo-BASE:hi-BASE]==imgs[1][lo-BASE:hi-BASE]
   roots=[n for n,s in reaches.items() if pc in s]
   prologue=None
   for p in range(pc, max(BASE,pc-2048)-1,-4):
    if word(p)&0xffff4000==0xe92d4000:prologue=p;break
   row={'target':hex(t),'site':hex(pc),'instruction':hex(word(pc)),'kind':'BL' if word(pc)&0x01000000 else 'B','local_window_sha256':sha(b[lo-BASE:hi-BASE]),'syntactic_roots':roots,'task_attribution':'POSSIBLE_NOT_EXCLUSIVE' if any(n.startswith('task_') for n in roots) else 'UNKNOWN','owner':'UNKNOWN','nearest_push_lr_hint':hex(prologue) if prologue else None,'coverage':'NO_INSTALLED_GUARD'};rows.append(row)
   snippets.append(f"target={t:08x} site={pc:08x} roots={','.join(roots) or 'UNKNOWN'} owner=UNKNOWN\n"+'\n'.join(f'{p:08x}: {lines.get(p,"UNDECODED")}' for p in range(lo,hi,4)))
 ranges=[(0x40,0x68),(0xca8,0xe9c),(0x705dc,0x70818),(0x82728,0x827c0),(0x41b74,0x41bc4),(0x6e9a0,0x6ea10)]
 for lo,hi in ranges:assert imgs[0][lo:hi]==imgs[1][lo:hi]
 snippets+=['native synchronization / observer bodies\n'+'\n'.join(f'{BASE+p:08x}: {lines.get(BASE+p,"UNDECODED")}' for p in range(lo,hi,4)) for lo,hi in ranges]
 (OUT/'coverage.json').write_text(json.dumps({'vsb_sha256':HASHES,'counts':{hex(t):len(s) for t,s in refs.items()},'rows':rows,'roots':summaries,'aligned_observer_pointers':{t:x['aligned_pointer_candidates'] for t,x in old['references'].items()},'limits':['CFG is context-insensitive and ignores condition feasibility and return matching','Indirect edges unresolved; BL assumes possible return','Nearest push is a hint, never a proven function boundary','No class owner, exclusive task, IRQ/FIQ/DMA absence or global coverage proof']},indent=2)+'\n')
 (OUT/'coverage-witnesses.json.gz').write_bytes(gzip.compress(json.dumps(witnesses).encode(),mtime=0));(OUT/'native-contexts.txt.gz').write_bytes(gzip.compress('\n\n'.join(snippets).encode(),mtime=0))
 print('PASS static candidates:',{hex(t):len(s) for t,s in refs.items()});print('Syntactic candidate root classes:',dict(Counter(r['task_attribution'] for r in rows)))
if __name__=='__main__':main()
