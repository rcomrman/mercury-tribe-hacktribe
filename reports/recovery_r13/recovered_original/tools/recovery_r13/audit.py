#!/usr/bin/env python3
"""Bounded graphic access graph; exact ARM branches/tables, explicit unknown contexts."""
import argparse,gzip,json,struct,subprocess
from pathlib import Path
from run import ROOT,HASHES,sha
RANGES={
 'fixed_source_primitives':(0x15804,0x15b50),'lcd_entry_worker':(0x15d14,0x160c4),'lcd_controls':(0x16230,0x163c8),'poll':(0x15cdc,0x15d14),
 'progress_leaf':(0x60300,0x60424),'progress_owner_getter':(0x4d598,0x4d5cc),'progress_io_read':(0x4d5cc,0x4d860),'progress_io_outer':(0x4d860,0x4de60),
 'progress_upstream_service':(0x31234,0x31344),'progress_upstream_other':(0x38d80,0x38e88),
 'startup':(0x2ab7c,0x2b110),'task_ui':(0x2b144,0x2b220),'wrapper_mode_select':(0x2d030,0x2d238),
 'ui_alternate':(0x83374,0x834fc),'ui_main_dispatch_tick':(0x834fc,0x83714),'ui_drain':(0x83848,0x83898),
 'timer_callback_loop':(0x2a71c,0x2a978),'secondary_requests':(0x6eae0,0x6eb78),'secondary_create':(0x6e9a0,0x6ea10),'secondary_delete':(0x6efd0,0x6f178),'graphic_cycle':(0x6f178,0x6f370),
 'fatal':(0x298bc,0x29a00),'graphics_stubs':(0x3f0d4,0x3f10c),'rectangle':(0x3f55c,0x3f650),'widget_pixel_reader':(0x71e84,0x71ef4),
 'ui_tables':(0xe4bb8,0xe4c70),'task_table':(0xa37a8,0xa38e8),'kernel_priority':(0x6a0,0x7ac),'kernel_wait_dispatch':(0x7ac,0x928),'irq_switch':(0x1648,0x18f0),'terminal_stop':(0x144,0x22c)}
TARGETS=[0xc0015804,0xc0015824,0xc0015900,0xc0015988,0xc0015ab4,0xc0015dd0,0xc0015fa0,0xc006038c,0xc006040c,0xc004d598,0xc004d5cc,0xc004d860,0xc006f178,0xc006e9a0,0xc006efd0,0xc0083374,0xc0083428,0xc0083848,0xc002d030,0xc003f55c]
ROWS=[
 ('ui_main','task4 / verified reference UI mode','C002B144→C002D030→C0083848→C00834FC→C00836E4→C006F178','C002D030 outer invocation','conditional','R7/R11 archives; R13 does not repeat full main cycle'),
 ('ui_alternate','task4 when selected UI mode2 (service mode7)','C002D030→C0083428→C00833F0→C0083374','same wrapper plus alternate draw coverage','protected_in_fixture','cases5/6: native queue/dispatch/loop, fixture widget'),
 ('secondary_pages','task4 along tick, other callers not exhausted','C00836E4→C006EAE0→C006E9A0 and C006F178 two slots','whole UI transaction before update, not Mercury callback only','conditional','static calls and R7/R8 evidence; no global lock installed'),
 ('periodic_worker','task2 timer callback','C002A7EC→callback+C→C002A71C→C0015DD0(3)→C0015FA0','timer callback+C outer adapter','protected_in_fixture','case17: callback fixture defers; later worker hits GPIO fault'),
 ('progress','task1 startup proven route; service callers also exist','C002AE90→C004D860→C006040C/C006038C→draw+op2+op3','top-level progress operation domain, not timer','unprotected','cases3/4/16; callers C0031250,C0038E40 also traced, contexts incomplete'),
 ('startup','task1','C002AB7C→C0015DA8→C0015EB8→clear source/shadow→forced worker','exclusive startup lifecycle before any Mercury ownership','unprotected','direct initializer bypasses dispatcher for forced worker'),
 ('fatal','many callers, arbitrary failure phase','C00298BC→clear/draw→op2/op3→GPIO→C00299F4','fault domain; no safe suppression/recovery proven','unprotected','R10 fault archive; nested error/transport dependence remains'),
 ('direct_compare','worker known caller; arbitrary probe/adapter aliases unknown','C0015AB4 reads fixed source without descriptor or private gate','full reader interval mediation','unprotected','cases2/9/14'),
 ('lcd_controls','service shutdown and parameter calls, full task contexts unknown','C0015DD0(7)→C00162C4→GPIO/SPI; op4 sets pending','transport/control domain separate from worker request','unprotected','case10; op5 is no-op, op1 clears source'),
 ('pixel_writer','UI and service widget chains, all contexts not assigned','C003F154/C0071EE0/C0073034/C00730EC→C0015824','all composition domains','unknown','four direct call sites; indirect widget entry/context not exhaustive'),
 ('range_writer','many widgets and service paths','C003F55C→C0015988, plus pixel line paths','all composition domains','unknown','all aligned rectangle call candidates retained'),
 ('pixel_reader','widget function context not fully assigned','C0071EC8→C0015900','reader coverage when source consistency required','unknown','R12 pixel observations preserved'),
 ('calculated_aliases','unknown / IRQ / FIQ / DMA not proven absent','computed addresses, indirect/native observer aliases','must identify or explicitly exclude','unknown','literal/branch scan cannot establish absence'),
 ('queue_drain_liveness','task4 consumer and producers','C002D030→drain until empty','bound complete domain duration','unprotected','case18:32 messages consumed in one call; unbounded producer model')]
def cmd(args):return subprocess.run(list(map(str,args)),cwd=ROOT,capture_output=True,text=True,check=True).stdout
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('custom',type=Path);p.add_argument('backup',type=Path);a=p.parse_args();build=ROOT/'build/recovery_r13';out=ROOT/'reports/recovery_r13';images=[]
 for path,h in zip((a.custom,a.backup),HASHES):b=path.read_bytes();assert len(b)==0x200100 and sha(b)==h;images.append(b[256:])
 ranges=[]
 for name,(lo,hi) in RANGES.items():assert images[0][lo:hi]==images[1][lo:hi],name;ranges.append({'name':name,'start':hex(0xc0000000+lo),'end_exclusive':hex(0xc0000000+hi),'sha256':sha(images[0][lo:hi])})
 (build/'inspect.bin').write_bytes(images[0]);(build/'inspect.S').write_text('.section .text\n.global image\nimage:\n.incbin "build/recovery_r13/inspect.bin"\n');cmd(['clang','--target=arm-none-eabi','-c',build/'inspect.S','-o',build/'inspect.o']);elf=build/'STATIC_INSPECTION_ONLY.elf';cmd(['ld.lld','-Ttext=0xc0000000','-e','image',build/'inspect.o','-o',elf]);text=[]
 for name,(lo,hi) in RANGES.items():text.append(name+'\n'+cmd(['llvm-objdump','-D',f'--start-address={0xc0000000+lo}',f'--stop-address={0xc0000000+hi}',elf]))
 (out/'native_disassembly.txt.gz').write_bytes(gzip.compress('\n'.join(text).encode(),mtime=0))
 refs={hex(t):[] for t in TARGETS};tables={hex(t):[] for t in TARGETS};literals={hex(t):[] for t in (0xc031b310,0xc031b710)};edges=[]
 for pos in range(0,len(images[0]),4):
  w=struct.unpack_from('<I',images[0],pos)[0];address=hex(0xc0000000+pos)
  if hex(w) in tables:tables[hex(w)].append(address)
  if hex(w) in literals:literals[hex(w)].append(address)
  if w&0x0e000000==0x0a000000 and w>>28!=15:
   imm=w&0xffffff;imm=imm-(1<<24) if imm&(1<<23) else imm;t=(0xc0000000+pos+8+imm*4)&0xffffffff
   if t in TARGETS:refs[hex(t)].append(address);edges.append({'callsite':address,'target':hex(t),'word':hex(w),'kind':'BL' if w&0x1000000 else 'B'})
 assert refs['0xc006038c']==['0xc004d81c','0xc004d928','0xc0060420']
 assert refs['0xc004d860']==['0xc002ae90','0xc0031250','0xc0038e40']
 assert struct.unpack_from('<I',images[0],0xe4bd0)[0]==0xc0083374 and struct.unpack_from('<I',images[0],0xe4bc4)[0]==0xc0083428
 coverage=[dict(zip(('id','context','chain','candidate_outer_point','lab_coverage','evidence'),row),installed_in_native_firmware=False) for row in ROWS]
 (out/'access_graph.json').write_text(json.dumps({'vsb_sha256':HASHES,'ranges':ranges,'direct_branch_candidates':refs,'branch_edges':edges,'aligned_pointer_candidates':tables,'fixed_address_literals':literals,'coverage':coverage,'scope':'No original instruction patched; laboratory coverage only. No global safe outer dominator found in inspected graph. Unknown contexts are explicit; no exhaustive indirect, Thumb, IRQ/FIQ/DMA exclusion claimed.'},indent=2)+'\n');print('PASS:',len(ranges),'identical original ranges;',len(edges),'candidate edges;14 coverage domains, no installed native protection')
if __name__=='__main__':main()
