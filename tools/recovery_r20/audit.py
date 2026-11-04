#!/usr/bin/env python3
"""R20 local destruction capabilities and bounded shared-root effects. No patches."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r20';BUILD=ROOT/'build/recovery_r20';BASE=0xc0000000
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'subscriber_ctor':(0x852b0,0x85408),'native_callback':(0x85078,0x85098),'subscriber_destructors':(0x851b4,0x85218),'inverse_destructor':(0x41b74,0x41bc4),'invoke_remove_register':(0x705dc,0x70818),'subscriber_vtable':(0xe4da0,0xe4dd8),'shared_deleters':(0x82394,0x824a0),'periodic_deleters':(0x82620,0x82728),'shared_state_owner':(0x6e6b0,0x6e8bc),'page_transition':(0x6e9a0,0x6ea10),'page_delete':(0x6efd0,0x6f040),'allocator_gate':(0x28dcc,0x28ddc),'model_getter':(0x30d28,0x30d5c),'irq_gate':(0x40,0x68),'semaphores':(0xca8,0xe9c)}
def main():
 assert len(sys.argv)==3;BUILD.mkdir(parents=True,exist_ok=True);images=[]
 for p,h in zip(sys.argv[1:],HASHES):
  data=Path(p).read_bytes();assert len(data)==0x200100 and hashlib.sha256(data).hexdigest()==h;images.append(data[256:])
 b=images[0];word=lambda pc:struct.unpack_from('<I',b,pc-BASE)[0]
 contracts={0xc0085078:0xe5d03048,0xc0085088:0x15c03049,0xc0085090:0x15c03014,0xc00851cc:0xe5a03038,0xc00851d0:0xebfef267,0xc00851ec:0xe2400038,0xc0085204:0xebfe8ef2,0xc0085210:0xe2400038,0xc0041ba0:0xeb00ba8d,0xc0041bb4:0xebff9c86,0xc007067c:0xe12fff3c,0xc00e4da8:0xc00851b4,0xc00e4dac:0xc00851f4,0xc00e4dd0:0xc00851ec,0xc00e4dd4:0xc0085210}
 for pc,w in contracts.items():assert word(pc)==w and struct.unpack_from('<I',images[1],pc-BASE)[0]==w,hex(pc)
 targets=[0xc00852b0,0xc00851b4,0xc00851f4,0xc00851ec,0xc0085210,0xc0041b74,0xc00705dc,0xc007061c,0xc0085078,0xc0082654,0xc00823c8]
 refs={hex(t):{'branch_candidates':[],'pointer_candidates':[]} for t in targets};roots=[0xc0691244,0xc0348844];loads=[]
 for off in range(0,len(b),4):
  pc=BASE+off;w=word(pc)
  if w in targets:refs[hex(w)]['pointer_candidates'].append(hex(pc))
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   n=w&0xffffff;n-=0x1000000 if n&0x800000 else 0;t=(pc+8+4*n)&0xffffffff
   if t in targets:refs[hex(t)]['branch_candidates'].append(hex(pc))
  if w&0x0f7f0000==0x051f0000 and w>>28!=15:
   lit=pc+8+(1 if w&0x800000 else -1)*(w&4095)
   if BASE<=lit<BASE+len(b)-3 and word(lit) in roots:loads.append((pc,word(lit),(w>>12)&15))
 # Deliberately local symbolic windows; ABI preservation assumed, branch feasibility unresolved.
 effects=[];windows=[]
 for pc,root,reg in loads:
  regs={reg:'ROOT_ADDRESS'};steps=[];end=min(pc+384,BASE+len(b))
  for p in range(pc+4,end,4):
   w=word(p);rn=w>>16&15;rd=w>>12&15
   if w&0x0f7f0000==0x051f0000:
    lit=p+8+(1 if w&0x800000 else -1)*(w&4095);regs[rd]='ROOT_ADDRESS' if BASE<=lit<BASE+len(b)-3 and word(lit)==root else 'UNKNOWN'
   elif w&0x0e000000==0x0a000000:
    if w&0x1000000:
     for r in (0,1,2,3,12,14):regs[r]='UNKNOWN'
    elif w>>28==14:end=p+4;break
   elif w&0x0ffffff0 in (0x012fff10,0x012fff30):
    if w&0x0ffffff0==0x012fff10:end=p+4;break
    for r in (0,1,2,3,12,14):regs[r]='UNKNOWN'
   elif w&0x0c000000==0x04000000 and not w&0x02000000:
    offset=w&4095
    if w&0x100000:
     if regs.get(rn)=='ROOT_ADDRESS' and offset==0:steps.append({'pc':hex(p),'word':hex(w),'effect':'READ_ROOT_VALUE'});regs[rd]='ROOT_VALUE'
     else:regs[rd]='UNKNOWN'
    elif regs.get(rn)=='ROOT_ADDRESS' and offset==0:steps.append({'pc':hex(p),'word':hex(w),'effect':'WRITE_ROOT_CANDIDATE','value':regs.get(rd,'UNKNOWN')})
    elif regs.get(rd) in ('ROOT_VALUE','ROOT_ADDRESS'):steps.append({'pc':hex(p),'word':hex(w),'effect':'PUBLISH_ALIAS_CANDIDATE','offset':offset,'value':regs[rd]})
   elif w&0x0fe00ff0==0x01a00000:regs[rd]=regs.get(w&15,'UNKNOWN')
   elif w&0x0fe00000==0x03a00000:regs[rd]='ZERO' if w&4095==0 else 'UNKNOWN'
   elif w&0x0e100000==0x08100000 and w&0x8000:end=p+4;break
   else:
    # Unknown writes are killed conservatively; no inference across arithmetic.
    if w&0x0c000000==0 and (w>>21&15) not in (8,9,10,11):regs[rd]='UNKNOWN'
  effects.append({'load':hex(pc),'root':hex(root),'steps':steps,'status':'LOCAL_CANDIDATES_NOT_EXHAUSTIVE'});windows.append((f'root_effect_{pc:08x}',pc-BASE,end-BASE))
 (BUILD/'image.bin').write_bytes(b);(BUILD/'image.S').write_text('.text\n.global image\nimage:\n.incbin "build/recovery_r20/image.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',BUILD/'image.S','-o',BUILD/'image.o']);elf=BUILD/'STATIC_ONLY.elf';run(['ld.lld','-Ttext=0xc0000000','-e','image',BUILD/'image.o','-o',elf])
 ranges=[];txt=[]
 for name,lo,hi in [(n,*v) for n,v in RANGES.items()]+windows:
  assert images[0][lo:hi]==images[1][lo:hi],name
  ranges.append({'name':name,'start':hex(BASE+lo),'end_exclusive':hex(BASE+hi),'sha256':hashlib.sha256(b[lo:hi]).hexdigest()});txt.append(name+'\n'+run(['llvm-objdump','-D',f'--start-address={BASE+lo}',f'--stop-address={BASE+hi}',elf]))
 (OUT/'native-map.json').write_text(json.dumps({'vsb_sha256':HASHES,'contracts':{hex(p):hex(w) for p,w in contracts.items()},'ranges':ranges,'references':refs,'root_effect_candidates':effects,'authority':{'native_deleting_paths_exist':'PROUVÉ statique','all_callers_mediated':'INCONNU','unique_shared_owner':'INCONNU','global_last_access':'INCONNU','root_lifetime':'PARTIEL'},'limitations':['ARM aligned/literal windows only','Linear effects assume callee-saved ABI and ignore branch feasibility','No exhaustive indirect/computed/Thumb/IRQ/FIQ/DMA roots','A free-capable path is not destruction authority']},indent=2)+'\n');(OUT/'native-map.txt.gz').write_bytes(gzip.compress('\n'.join(txt).encode(),mtime=0));print('PASS',len(ranges),'identical ranges; two free boundaries and native callback; root effects remain candidates');print('Native destructor references:',{t:{k:len(v) for k,v in r.items()} for t,r in refs.items()})
if __name__=='__main__':main()
