#!/usr/bin/env python3
"""R12 readonly original evidence plus explicit missing MD53/54 inventory."""
import argparse,gzip,hashlib,json,struct,subprocess
from pathlib import Path
from run import ROOT,HASHES
BASE='f565a58b198fe317dc84fd6ea2123c3e64412b0c'
RANGES={'irq_save_restore':(0x40,0x68),'priority_change':(0x6a0,0x7ac),'semaphores':(0xc4c,0xe44),'semaphore_wait':(0x1d14,0x1dd0),'existing_semaphore1_use':(0x12750,0x127b0),'existing_semaphore2_use':(0x29a74,0x29ab8),'queue_sem_irq_pattern':(0x24bf4,0x24c48),'graphics_source':(0x15804,0x15b50),'lcd_descriptor_worker':(0x15d14,0x1613c),'graphics_stubs':(0x3f0d4,0x3f10c),'rectangle':(0x3f55c,0x3f61c),'progress_draw_send':(0x6038c,0x6040c),'lcd_shutdown_candidate':(0x38b88,0x38c28),'other_graphics_request':(0x83384,0x833f0),'task2_callback':(0x2a71c,0x2a730),'ui_tick':(0x836e4,0x83714),'fatal':(0x298bc,0x29a00),'task_exit':(0x1a24,0x1a64),'terminal_stop':(0x144,0x22c),'semaphore_config':(0xa3728,0xa3780)}
TARGETS=[0xc0015804,0xc0015824,0xc0015900,0xc0015988,0xc0015ab4,0xc0015dd0,0xc0015fa0,0xc003f55c,0xc0000d80,0xc0000ca8]
def output(cmd):return subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True).stdout
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);a=p.parse_args();build=ROOT/'build/recovery_r12';out=ROOT/'reports/recovery_r12';images=[]
 for path,h in zip((a.custom,a.backup),HASHES):
  b=path.read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
 ranges=[]
 for name,(lo,hi) in RANGES.items():assert images[0][lo:hi]==images[1][lo:hi],name;ranges.append({'name':name,'start':hex(0xc0000000+lo),'end_exclusive':hex(0xc0000000+hi),'sha256':hashlib.sha256(images[0][lo:hi]).hexdigest()})
 (build/'inspect.bin').write_bytes(images[0]);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r12/inspect.bin"\n');subprocess.run(['clang','--target=arm-none-eabi','-c',str(build/'inspect.S'),'-o',str(build/'inspect.o')],cwd=ROOT,check=True);elf=build/'STATIC_INSPECTION_ONLY.elf';subprocess.run(['ld.lld','-Ttext=0xc0000000','-e','image',str(build/'inspect.o'),'-o',str(elf)],check=True)
 text=[]
 for name,(lo,hi) in RANGES.items():text.append(name+'\n'+output(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',str(elf)]))
 (out/'native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(text).encode(),mtime=0))
 refs={hex(t):[] for t in TARGETS};literals={hex(t):[] for t in (0xc031b310,0xc031b710)}
 for pos in range(0,len(images[0]),4):
  w=struct.unpack_from('<I',images[0],pos)[0]
  if hex(w) in literals:literals[hex(w)].append(hex(0xc0000000+pos))
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   imm=w&0xffffff;imm=imm-(1<<24) if imm&(1<<23) else imm;t=(0xc0000000+pos+8+imm*4)&0xffffffff
   if t in TARGETS:refs[hex(t)].append(hex(0xc0000000+pos))
 count=struct.unpack_from('<I',images[0],0xa377c)[0];configs=[list(struct.unpack_from('<3I',images[0],0xa3728+i*12)) for i in range(count)];assert count==7 and configs==[[1,1,1]]*7
 (out/'static_audit.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':ranges,'semaphores':{'count':count,'config_records':configs,'runtime_base':'0xc06a2474','record_bytes':16},'aligned_branch_candidates':refs,'fixed_address_literals':literals,'limitations':'Not exhaustive: indirect calls, pointers and all execution contexts are not recovered. Data can decode as ARM branches. No unused semaphore ID or real exclusion inferred.'},indent=2)+'\n')
 tree=output(['git','ls-tree','-r','--name-only',BASE]).splitlines();wanted=['research/md53_frames.c','research/md54_scan.c','tests/run_md53.sh','tests/arm/md54_abi.S','MD53_RAPPORT_FR.md','MD54_RAPPORT_FR.md'];missing=[x for x in wanted if x not in tree]
 probe=subprocess.run(['git','cat-file','-e','4c1ec01^{commit}'],cwd=ROOT,capture_output=True);history=output(['git','log','--all','--oneline','--','*md53*','*MD53*','*md54*','*MD54*'])
 archives=[]
 # Repeat bounded archive search over the workspace; do not claim search of lost volume.
 for path in ROOT.parent.glob('**/*'):
  if len(path.relative_to(ROOT.parent).parts)>5 or any(x in path.parts for x in ('.git','build','work')):continue
  if path.is_file() and (path.suffix.lower() in ('.zip','.bundle','.tgz','.tar') or '.tar.' in path.name):archives.append(str(path.relative_to(ROOT.parent)))
 existing=['documents/RECOVERY_DOSSIER_MD46_MD87_TRANSCRIPTION.md','tools/recovery_r9/models.py','tests/recovery_r9/layout.c','src/lcd_source_mux.c','src/md18_lcd_abi.c','src/md30_lcd_gate.c','src/md31_lcd_comparator.c']
 (out/'inventory.json').write_text(json.dumps({'base_commit':BASE,'missing_exact_paths':missing,'historical_commit_4c1ec01_local_object_present':probe.returncode==0,'matching_path_history_all_local_refs':history.splitlines(),'archive_search_scope':'workspace to depth5, excluding .git/build/work; not old inaccessible environment','archives_found':archives,'available_sources_sha256':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in existing},'conclusion':'MD53/54 transcription available; original sources/tests/reports not recovered. R9 role model and older source adapters are actually present.'},indent=2)+'\n');print('PASS: 20 original ranges equal; seven semaphores; explicit MD53/54 inventory recorded')
if __name__=='__main__':main()
