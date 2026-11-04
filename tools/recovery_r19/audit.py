#!/usr/bin/env python3
"""R19 bounded native ownership audit. No instruction patches or exhaustive alias claim."""
import gzip,hashlib,json,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r19';BUILD=ROOT/'build/recovery_r19';BASE=0xc0000000
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
RANGES={'state_ctor':(0x6e6ec,0x6e8bc),'state_base_dtor':(0x6e6b0,0x6e6ec),'ui_ctor_dtor':(0x83898,0x83920),'state_transition':(0x6e8bc,0x6ea10),'state_tick':(0x6eae0,0x6eb78),'page_delete':(0x6efd0,0x6f040),'periodic_ctor_dtor':(0x82620,0x82728),'periodic_notify':(0x82728,0x827c0),'associated_ctor_dtor':(0x82394,0x824a0),'associated_update':(0x824a0,0x82620),'subject_vtables':(0xe4ad0,0xe4b78),'observer_protocol':(0x705dc,0x70818),'inverse_dtor':(0x41b74,0x41bc4),'irq_helpers':(0x40,0x68),'semaphores':(0xca8,0xe9c),'allocator_extension_boundary':(0xa3b0,0xa3f0),'sample_subscriber_ctor':(0x852b0,0x85408),'sample_subscriber_dtor':(0x851b4,0x85218),'sample_subscriber_vtable':(0xe4da0,0xe4dd8),'sample_page_registration':(0x652bc,0x65370)}
def main():
 assert len(sys.argv)==3;BUILD.mkdir(parents=True,exist_ok=True);imgs=[]
 for p,h in zip(sys.argv[1:],HASHES):
  blob=Path(p).read_bytes();assert len(blob)==0x200100 and hashlib.sha256(blob).hexdigest()==h;imgs.append(blob[256:])
 b=imgs[0];word=lambda pc:struct.unpack_from('<I',b,pc-BASE)[0]
 expected={0xc006e728:0xe3a00fe2,0xc006e734:0xeb004fdb,0xc006e738:0xe5856000,0xc006e744:0xe5843024,0xc006e768:0xe59f0138,0xc006e774:0xeb004f28,0xc006e778:0xe5856000,0xc006e784:0xe584302c,0xc006e89c:0xc0691244,0xc006e8a4:0xc0348844,0xc006e8a8:0x428,0xc006eb6c:0xe5940024,0xc00707a8:0xe58c4000,0xc00707c8:0xe5cc3014,0xc00707cc:0xe5943008,0xc00707ec:0xe5843008,0xc0070814:0xe8bd8030,0xc00e4b58:0xc0082620,0xc00e4b5c:0xc0082654,0xc000a3c4:0xe5843000,0xc000a3ec:0xc06a293c,0xc0085388:0xe2848038,0xc0085394:0xe525400c,0xc0085398:0xe1a01008,0xc00853a4:0xe3a0200a,0xc0085400:0xc0085078,0xc00851cc:0xe5a03038,0xc00851d0:0xebfef267,0xc00851ec:0xe2400038}
 for pc,w in expected.items():assert word(pc)==w and struct.unpack_from('<I',imgs[1],pc-BASE)[0]==w,hex(pc)
 targets=[0xc00826a8,0xc008241c,0xc006e6ec,0xc0083898,0xc0082620,0xc0082654,0xc0082394,0xc00823c8,0xc0041b74];roots=[0xc0691244,0xc0348844]
 refs={hex(t):{'branches':[],'aligned_pointers':[]} for t in targets+roots};loads={hex(t):[] for t in roots};windows=[]
 for off in range(0,len(b),4):
  pc=BASE+off;w=word(pc)
  if w in targets+roots:refs[hex(w)]['aligned_pointers'].append(hex(pc))
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   n=w&0xffffff;n-=0x1000000 if n&0x800000 else 0;t=(pc+8+4*n)&0xffffffff
   if t in targets:refs[hex(t)]['branches'].append(hex(pc))
  if w&0x0f7f0000==0x051f0000 and w>>28!=15:
   literal=pc+8+(1 if w&0x800000 else -1)*(w&4095)
   if BASE<=literal<BASE+len(b)-3 and word(literal) in roots:
    t=word(literal);loads[hex(t)].append({'pc':hex(pc),'literal':hex(literal),'destination_register':(w>>12)&15});windows.append((f'root_{t:08x}_{pc:08x}',max(0,off-64),min(len(b),off+96)))
 assert len(refs['0xc00826a8']['branches'])==8 and len(refs['0xc008241c']['branches'])==8
 (BUILD/'image.bin').write_bytes(b);(BUILD/'image.S').write_text('.text\n.global image\nimage:\n.incbin "build/recovery_r19/image.bin"\n')
 def run(a):return subprocess.check_output(a,cwd=ROOT,text=True)
 run(['clang','--target=arm-none-eabi','-c',BUILD/'image.S','-o',BUILD/'image.o']);elf=BUILD/'STATIC_ONLY.elf';run(['ld.lld','-Ttext=0xc0000000','-e','image',BUILD/'image.o','-o',elf])
 txt=[];ranges=[]
 for name,lo,hi in [(n,*r) for n,r in RANGES.items()]+windows:
  assert imgs[0][lo:hi]==imgs[1][lo:hi],name
  ranges.append({'name':name,'start':hex(BASE+lo),'end_exclusive':hex(BASE+hi),'sha256':hashlib.sha256(b[lo:hi]).hexdigest()});txt.append(name+'\n'+run(['llvm-objdump','-D',f'--start-address={BASE+lo}',f'--stop-address={BASE+hi}',elf]))
 graph=[{'from':'subscriber constructed C00852B0','to':'inline key at object+0x38, callback this=whole object, direct method C0085078, period10','status':'PROUVÉ local native dataflow','evidence':['C0085388','C0085394','C0085398','C00853A4','C00853A8','C0085400']},{'from':'subscriber destructor C00851B4','to':'C0041B74(object+0x38), then deleting variant C00851F4 can free outer object','status':'PROUVÉ static; no callback join','evidence':['C00851CC','C00851D0','C00851F4','C0085204']},{'from':'UI manager+0x10','to':'state','status':'PROUVÉ','evidence':['C0083900','C0083904']},{'from':'state+0x24','to':'*C0691244','status':'PROUVÉ','evidence':['C006E73C','C006E744']},{'from':'lazy creator','to':'periodic allocation904/ctor C00826A8/global root','status':'PROUVÉ','evidence':['C006E71C','C006E728','C006E72C','C006E734','C006E738']},{'from':'state+0x2C','to':'*C0348844','status':'PROUVÉ','evidence':['C006E758','C006E774','C006E778','C006E784']},{'from':'associated allocation1064','to':'C008241C ctor','status':'PROUVÉ','evidence':['C006E768','C006E76C','C006E774','C006E8A8']},{'from':'state destructor','to':'C0041B74(state key), not a direct free of state+24/+2C','status':'PROUVÉ local body','evidence':['C006E6B0','C006E6C0']},{'from':'all global/alias roots','to':'exclusive owner and last destruction authority','status':'INCONNU','evidence':[]},{'from':'lazy shared root','to':'process-lifetime singleton hypothesis','status':'PARTIEL','evidence':['eight constructor call candidates','no synchronization in inspected lazy branches']}]
 data={'base':'6808871b54c10e130e085ab4e658bc8bf3cbf1bb','vsb_sha256':HASHES,'ranges':ranges,'contracts':{hex(p):hex(w) for p,w in expected.items()},'references':refs,'root_load_candidates':loads,'ownership_graph':graph,'limits':['Aligned ARM/literal candidates only, not exhaustive indirect/Thumb/IRQ/FIQ/DMA','Global storage and borrowing proven locally; unique owner and no future free not proven','Allocator, whole UI constructor/destructor not dynamically qualified']}
 (OUT/'ownership.json').write_text(json.dumps(data,indent=2)+'\n');(OUT/'native-ownership.txt.gz').write_bytes(gzip.compress('\n'.join(txt).encode(),mtime=0));print('PASS',len(ranges),'identical ownership/transaction ranges; 8 lazy ctor branches each; global roots and aliases recorded')
if __name__=='__main__':main()
