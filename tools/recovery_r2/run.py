#!/usr/bin/env python3
"""R2 native UI lifecycle experiments, Linux ARM926 only; VSB read-only."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,resource,struct,subprocess
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
NAMES=['native_heap','native_page','mixed_mercury','vector_growth','duplicate_alias','active_destroy','append_in_draw','destroy_in_draw','null_child','native_repeat','nondeleting','native_heap_cycles','native_heap_mercury','missing_deleting_callback','native_heap_readonly_data','native_data_without_heap','uninitialized_graphics']
def run(cmd,**kwargs):return subprocess.run(list(map(str,cmd)),check=True,timeout=90,**kwargs)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);p.add_argument('--explore',action='store_true');a=p.parse_args()
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 os.chdir(ROOT);build=ROOT/'build/recovery_r2';out=ROOT/'reports/recovery_r2'
 build.mkdir(parents=True,exist_ok=True);(out/'traces').mkdir(parents=True,exist_ok=True)
 frames=(ROOT/'build/recovery_r1/frames.bin').read_bytes();assert len(frames)==32768
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-std=c99','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror']
 run([*arm,'-c','tests/recovery_r2/start.S','-o',build/'start.o'])
 results=[]
 for vi,(path,expected) in enumerate(zip((a.custom,a.backup),HASHES)):
  blob=path.read_bytes();assert sha(blob)==expected and len(blob)==0x200100
  image=blob[256:];(build/'original.bin').write_bytes(image)
  asm='''.syntax unified
.cpu arm926ej-s
.arm
.text
.global r2_iteration
.type r2_iteration,%function
r2_iteration:
 push {r4-r8,lr}
 sub sp,sp,#8
 mov r5,r0
 mov r3,#1
 strb r3,[r5,#28]
 .incbin "build/recovery_r2/original.bin",0x6f240,96
 add sp,sp,#8
 pop {r4-r8,pc}
.section .rodata
.balign 4
.global original
original:
 .incbin "build/recovery_r2/original.bin"
.global frames
frames:
 .incbin "build/recovery_r1/frames.bin"
.section .note.GNU-stack,"",%progbits
'''
  (build/'original.S').write_text(asm);run([*arm,'-c',build/'original.S','-o',build/'original.o'])
  for case,name in enumerate(NAMES):
   tag=f'{vi}_{case}_{name}';trace=build/(tag+'.trace');elf=build/(tag+'_LINUX_TEST_ONLY.elf')
   run([*arm,f'-DR2_CASE={case}','-c','tests/recovery_r2/lifecycle.c','-o',build/'probe.o'])
   run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.o',build/'probe.o',build/'original.o','-o',elf])
   cmd=['qemu-arm','-cpu','arm926','-strace','-d','in_asm','-D',str(trace),str(elf)]
   try:
    r=subprocess.run(cmd,capture_output=True,timeout=2 if case in (0,5,7) else 30);rc=r.returncode;raw=r.stdout;err=r.stderr
   except subprocess.TimeoutExpired as ex:rc='timeout';raw=ex.stdout or b'';err=ex.stderr or b''
   (build/(tag+'.records')).write_bytes(raw)
   (out/'traces'/(tag+'.records.gz')).write_bytes(gzip.compress(raw,mtime=0))
   text=trace.read_text();(out/'traces'/(tag+'.log.gz')).write_bytes(gzip.compress(text.encode(),mtime=0))
   (out/'traces'/(tag+'.stderr.txt')).write_bytes(err)
   offset=0;events=[];shots=[]
   while offset<len(raw):
    fields=struct.unpack_from('<16I',raw,offset);offset+=64;assert fields[0]==0x52325549 and fields[2]==case
    ev=dict(zip(['magic','type','case','a','b','c','d','allocs','frees','live','draws','cleanups','deletes','pixels','sequence','reserved'],fields));events.append(ev)
    if ev['type']==100:
     fb=raw[offset:offset+1024];offset+=1024;assert len(fb)==1024
     ev['framebuffer_sha256']=sha(fb);shots.append((ev['a'],fb))
   assert offset==len(raw)
   result={'vsb':vi,'case':case,'name':name,'exit':rc,'trace_sha256':sha(text.encode()),'trace_bytes':len(text),'stderr':err.decode(errors='replace'),'events':events}
   result['heap_mode']='native' if case in (0,11,12,14,15) else 'laboratory'
   result['snapshot_bitcounts']={str(stage):sum(x.bit_count() for x in fb) for stage,fb in shots}
   if case in (2,12):
    ss=dict(shots);result['cleanup_changed_bytes']=sum(x!=y for x,y in zip(ss[202],ss[9]));result['cleanup_changed_bits']=sum((x^y).bit_count() for x,y in zip(ss[202],ss[9]))
   results.append(result)
   print(vi,case,name,'exit=',rc,'events=',len(events),'last=',events[-1] if events else None,flush=True)
   if not a.explore:
    expected_exit={0:-11,4:84,5:'timeout',7:'timeout',8:-11,14:-11,15:-11}.get(case,0)
    assert rc==expected_exit,(tag,rc,expected_exit)
    assert not any(e['type']==99 for e in events) or case==4
    if case==15:assert 'si_addr=0xc06a293c' in (err.decode()+text)
    if case==14:assert 'si_addr=0xc00f9268' in (err.decode()+text) and 'si_code=2' in (err.decode()+text)
    if case==0:assert 'si_addr=0xc06a293c' in (err.decode()+text)
    if case==8:assert any(e['type']==100 and e['b']==2 for e in events)
    if rc=='timeout':assert '0xc0060f3c:' in text
    if rc==0:
     assert events[-1]['live']==(1 if case in (10,13) else 0)
     if case in (2,12):
      for stage,fb in shots:
       if 100<=stage<132:assert fb==frames[(stage-100)*1024:(stage-99)*1024]
      expected_fb=bytearray(dict(shots)[202])
      for yy in range(22,42):
       for xx in range(1,127):expected_fb[(yy//8)*128+xx]&=~(1<<(yy%8))&255
      assert bytes(expected_fb)==dict(shots)[9],'native text cleanup rectangle differs'
     if case==1:
      ss=dict(shots);assert sum(v.bit_count() for v in ss[1])==601 and sum(v.bit_count() for v in ss[2])==324
      text_alloc=next(e['a'] for e in events if e['type']==1 and e['b']==156)
      children=next(e for e in events if e['type']==7);assert children['c']==text_alloc+16
     if case==3:
      assert [e['b'] for e in events if e['type']==8]==[1,2,4,4,8,8,8,8,16,16,16,16,16,16,16,16]
      assert events[-1]['draws']==16 and events[-1]['cleanups']==16 and events[-1]['deletes']==16
     if case==16:
      ss=dict(shots);assert sum(v.bit_count() for v in ss[1])==278 and sum(v.bit_count() for v in ss[2])==1
     if case==9:
      ss=dict(shots);assert ss[1]!=ss[10] and ss[10]==ss[11] and ss[1]==ss[12]
     if case==11:
      cycles=[e for e in events if e['type']==10];assert len(cycles)==64
      assert len({e['b'] for e in cycles})==1 and len({e['c'] for e in cycles})==1
      assert '0xc000ee6c:' in text and '0xc0008f70:' in text and '0xc002cefc:' in text
     if case==12:
      assert events[-1]['cleanups']==1 and events[-1]['deletes']==1
      assert '0xc000ee6c:' in text and '0xc0008f70:' in text
     if case==13:assert events[-1]['deletes']==0 and events[-1]['cleanups']==1
     if case==6:
      assert events[-1]['draws']==3 and events[-1]['cleanups']==2
    if case in (1,2,9,10,11,12):assert '0xc006d518:' in text and '0xc008ccd4:' in text
    if case in (1,2,3,6,9,10,11,12):assert '0xc0060f10:' in text
   if vi==0:
    from PIL import Image
    for stage,fb in shots:
     if case in (1,9,16) or (case in (2,12) and stage in (100,103,116,131,9,202,300,301,302)):
      im=Image.new('1',(128,64));im.putdata([255*((fb[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);im.resize((512,256)).save(out/f'{name}_{stage}.png')
    if case==12:
     ims=[];sheet=Image.new('1',(512,512))
     for stage,fb in shots:
      if 100<=stage<132:
       im=Image.new('1',(128,64));im.putdata([255*((fb[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);ims.append(im.resize((512,256)).convert('P'));i=stage-100;sheet.paste(im,((i%4)*128,(i//4)*64))
     ims[0].save(out/'mercury_native_iteration.gif',save_all=True,append_images=ims[1:],duration=180,loop=0);sheet.save(out/'native_heap_v30_presets.png')
  assert sha(path.read_bytes())==expected
 if not a.explore:
  # Addresses and counters are deterministic across both images for identical builds.
  first=results[:len(NAMES)];second=results[len(NAMES):]
  for x,y in zip(first,second):assert x['events']==y['events'] and x['exit']==y['exit'],x['name']
 report={'scope':'RESEARCH_ONLY; no hardware validation','vsb_sha256':HASHES,'frames_sha256':sha(frames),'exploratory':a.explore,'source_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for folder in ('tests/recovery_r2','tools/recovery_r2','src') for p in sorted((ROOT/folder).glob('*')) if p.is_file()},'results':results}
 (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
