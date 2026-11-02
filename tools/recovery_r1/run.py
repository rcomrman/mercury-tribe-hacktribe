#!/usr/bin/env python3
"""Rebuild R1 evidence from MD45 sources and two read-only original VSBs."""
import argparse,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args,**kw):return subprocess.run(list(map(str,args)),check=True,timeout=90,**kw)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);a=p.parse_args()
 os.chdir(ROOT);build=ROOT/'build/recovery_r1';build.mkdir(parents=True,exist_ok=True)
 out=ROOT/'reports/recovery_r1';out.mkdir(parents=True,exist_ok=True)
 for tool in ('clang','ld.lld','qemu-arm'):
  if not shutil.which(tool):raise SystemExit(f'Missing {tool}: add toolchain to PATH')
 inputs=[]
 for path,expected in zip((a.custom,a.backup),HASHES):
  b=path.read_bytes()
  if len(b)!=0x200100 or sha(b)!=expected:raise SystemExit('Original VSB hash/size mismatch')
  inputs.append((path,b))
 versions={t:run([t,'--version'],capture_output=True,text=True).stdout.splitlines()[0] for t in ('clang','ld.lld','qemu-arm')}
 sources=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
 flags=['-std=c99','-O2','-Wall','-Wextra','-Werror','-Isrc']
 run(['clang',*flags,'-fsanitize=address,undefined','-fno-omit-frame-pointer','tests/recovery_r1/frames.c',*sources,'-o',build/'frames_host'])
 with (build/'frames.bin').open('wb') as f:run([build/'frames_host'],stdout=f)
 frames=(build/'frames.bin').read_bytes();assert len(frames)==32768
 assert len({frames[n*1024:(n+1)*1024] for n in range(32)})==32,'Fixture images must differ'
 # Eight scenes, four images each. Inputs are synthetic, not pattern playback.
 arm=['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm',*flags,'-ffreestanding','-fno-builtin','-fno-stack-protector']
 for name in ('start.S','probe.c'):run([*arm,'-c','tests/recovery_r1/'+name,'-o',build/(name+'.o')])
 run([*arm,'-DR1_NO_PIXEL','-c','tests/recovery_r1/probe.c','-o',build/'no_pixel.o'])
 results=[];raw_results=[]
 for index,(path,blob) in enumerate(inputs):
  image=blob[0x100:];(build/'original.bin').write_bytes(image)
  # Paths are generated relative constants; no user path embedded in assembler.
  asm='.section .rodata\n.balign 4\n.global original\noriginal:\n.incbin "build/recovery_r1/original.bin"\n.global frames\nframes:\n.incbin "build/recovery_r1/frames.bin"\n.section .note.GNU-stack,"",%progbits\n'
  (build/'data.S').write_text(asm);run([*arm,'-c',build/'data.S','-o',build/'data.o'])
  for variant,obj in [('normal','probe.c.o'),('no_pixel','no_pixel.o')]:
   elf=build/f'{index}_{variant}_LINUX_TEST_ONLY.elf'
   run(['ld.lld','-T','tests/recovery_r1/linux_test.ld',build/'start.S.o',build/obj,build/'data.o','-o',elf])
   trace=build/f'{index}_{variant}_trace.log'
   r=subprocess.run(['qemu-arm','-cpu','arm926','-d','in_asm','-D',str(trace),str(elf)],capture_output=True,timeout=60)
   if variant=='no_pixel':
    assert r.returncode==5,('pixel suppression not detected',r.returncode,r.stderr);continue
   assert r.returncode==0,(r.returncode,r.stderr.decode(errors='replace'))
   native_trace=trace.read_text()
   executed=['c0015824','c0015b50','c001531c','c00153c8','c0015428']
   assert all('0x'+addr+':' in native_trace for addr in executed),'Missing native execution trace'
   raw=r.stdout;raw_results.append(raw);(build/f'{index}_records.bin').write_bytes(raw)
  assert len(raw)==70*1056,len(raw)
  rows=[];previous=None
  for off in range(0,len(raw),1056):
   values=struct.unpack_from('<8I',raw,off);fid,mode,calls,on,offcount,mis,guard,full=values
   fb=raw[off+32:off+1056]
   target=frames[fid*1024:(fid+1)*1024] if fid<32 else (frames[31*1024:32*1024] if fid==32 else bytes(~b&255 for b in frames[31*1024:32*1024]) if fid==33 else bytes((i*37+13)&255 for i in range(1024)))
   expected_calls=8192 if full else sum((x^y).bit_count() for x,y in zip(previous,target))
   assert calls==expected_calls and on+offcount==calls and guard==0
   actual_mis=sum(x!=y for x,y in zip(fb,target));assert mis==actual_mis==(1 if fid==35 else 0)
   if fid==35:assert fb[3]^target[3]==128
   assert full==(mode==0 or fid==0 or fid==36)
   previous=target
   rows.append(dict(zip(['frame','mode','calls','on','off','mismatched_bytes','guard_errors','full'],values),framebuffer_sha256=sha(fb)))
  total=sum(r['calls'] for r in rows if r['mode']==1 and r['frame']<32)
  assert rows[64]['calls']==0 and rows[65]['calls']==8192 and rows[67]['calls']==0 and rows[68]['calls']==8192 and rows[69]['calls']==0
  results.append({'name':path.name,'sha256':sha(blob),'pixel_and_helpers_sha256':sha(image[0x1531c:0x15ba0]),'full_calls':32*8192,'differential_calls':total,'saved_percent':100*(1-total/(32*8192)),'records':rows,'suppressed_pixel_exit':5,'native_entries_executed':executed})
  assert sha(path.read_bytes())==HASHES[index],'Original changed'
 assert raw_results[0]==raw_results[1],'Different ARM outputs between VSBs'
 report={'scope':'RESEARCH_ONLY Linux QEMU; not hardware validation','versions':versions,'frames_sha256':sha(frames),'frames':32,'presets':8,'images_per_preset':4,'same_results_both_vsbs':True,'source_sha256':{s:sha((ROOT/s).read_bytes()) for s in sources},'results':results}
 (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('results','source_sha256')},indent=2))
 for r in results:print(r['name'],r['differential_calls'],'differential calls;',round(r['saved_percent'],2),'% saved; all 70 records verified')
 # Visual reference generated from the actual test inputs, not historical captures.
 from PIL import Image
 sheet=Image.new('1',(128*4,64*8))
 for n in range(32):
  b=frames[n*1024:(n+1)*1024];im=Image.new('1',(128,64));im.putdata([255*((b[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);sheet.paste(im,((n%4)*128,(n//4)*64))
 sheet.save(out/'presets.png')
if __name__=='__main__':main()
