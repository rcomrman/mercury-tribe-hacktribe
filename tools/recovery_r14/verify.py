#!/usr/bin/env python3
"""Independent raw record, image, phase, lifetime and preservation oracles.
Does not import runner or admission implementation. No peripheral oracle.
"""
import gzip,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='cb0d8caf9cb70d182f6e64ea7e72d8c796cd4e96'
def sha(b):return hashlib.sha256(b).hexdigest()
# Final phase, flags packed in record aux, ticket, pool+epoch packed aux.
# Constants encode required owner/complete/close/pending/pages/written values.
END={0:(0,0x108400,64,0x3302020),1:(0,0x108400,3,0x3300202),2:(0,0x100400,1,0x3300100),3:(0,0x100400,1,0x3300100),4:(0,0x108000,1,0x3300000),5:(0,0x108000,3,0x3300101),6:(0,0x108400,3,0x3300101),7:(0,0x108000,2,0x3300101),8:(4,0x5000000,1,0x3300000),9:(0,0x140400,1,0x3380100),10:(0,0x148000,1,0x3380000),11:(0,0x160000,1,0x3380100),12:(1,0x40c0080,1,0x1380000),15:(1,0x4000180,1,0x1300000),16:(0,0x108000,1,0x3300000),17:(4,0x5010000,1,0x3300000),18:(0,0x20000,0,0x3300000),19:(0,0x120000,0xffffffff,0x3300000),20:(0,0x120000,1,0x3300100),21:(0,0x108400,2,0x3300101),23:(0,0x108000,3,0x3300101),24:(2,0x21c1000,1,0x3380000),25:(4,0x50c0000,1,0x3380000),26:(0,0x120000,0,0xffffff00|0x3300000),27:(0,0x100400,2,0x3300200)}
FAULT={13:(2,0x2100400,2,0x3300100),14:(4,0x5000000,1,0x3300000),22:(1,0x4010180,1,0x1300000)}
def main():
 out=ROOT/'reports/recovery_r14';r=json.loads((out/'results.json').read_text());assert len(r['cases'])==56
 frames=(ROOT/'build/recovery_r14/frames.bin').read_bytes();assert len(frames)==32768 and sha(frames)==r['frames_sha256']==json.loads((ROOT/'reports/recovery_r1/results.json').read_text())['frames_sha256']
 old=bytes([0x11])*1024;new=bytes([0xee])*1024;zero=bytes(1024);partial=new[:384]+old[384:];bar=bytearray(old)
 for x in range(9,65):bar[896+x]=0x71
 partialbar=partial[:896]+bar[896:]
 final_images={0:(frames[-1024:],frames[-1024:]),1:(zero,zero),2:(new,old),3:(new,old),4:(old,old),5:(zero,zero),6:(new,new),7:(zero,zero),8:(old,old),9:(new,old),10:(old,old),11:(zero,old),12:(new[:128]+old[128:],old),13:(new,new[:128]+old[128:]),14:(bar,bar),15:(partial,partial),16:(new,old[:384]+new[384:]),17:(zero,old),18:(old,old),19:(old,old),20:(bar,old),21:(new,new),22:(partialbar,new[:128]+old[128:]),23:(zero,zero),24:(old,old),25:(old,old),26:(old,old),27:(old,old)}
 for vi in range(2):
  for case in range(28):
   row=r['cases'][vi*28+case];assert (row['vsb'],row['case'])==(vi,case);raw=gzip.decompress((out/f'{vi}_{case}.records.gz').read_bytes());assert raw and len(raw)%2112==0;events=[];snapshots={}
   for i in range(0,len(raw),2112):
    h=list(struct.unpack_from('<16I',raw,i));assert h[:2]==[0x52394c43,300+case] and h[5]==len(events) and h[6]==0x39 and h[2]!=99
    src=raw[i+64:i+1088];shd=raw[i+1088:i+2112];events.append(dict(header=h,source_sha256=sha(src),shadow_sha256=sha(shd)));snapshots[h[2]]=(h,src,shd)
   assert events==row['events']
   assert events[0]['header'][2:5]==[0,64,3112]
   h,src,shd=snapshots[90 if case in FAULT else 20];want=final_images[case];assert src==want[0] and shd==want[1],(vi,case,'image')
   stage=89 if case in FAULT else 20;meta=189 if case in FAULT else 120;exp=(FAULT if case in FAULT else END)[case]
   assert snapshots[stage][0][3:5]==list(exp[:2]),(vi,case,'phase',snapshots[stage][0][3:5],exp)
   assert snapshots[meta][0][3:5]==list(exp[2:]),(vi,case,'metadata',snapshots[meta][0][3:5],exp)
   trace=gzip.decompress((out/f'{vi}_{case}.trace.gz').read_bytes())
   if case in FAULT:
    assert row['exit']==88 and events[-1]['header'][2:5]==[90,0x01e260bc,11] and b'0xc0016c18:' in trace
   else:assert row['exit']==0 and 90 not in snapshots and events[-1]['header'][2]==120
   if case==0:
    shots=[e for e in events if e['header'][2]==10];assert len(shots)==32
    for n,e in enumerate(shots):assert e['header'][3:5]==[n,n+1] and e['source_sha256']==e['shadow_sha256']==sha(frames[n*1024:(n+1)*1024])
   # Early refusals retain exact partial source and held reader, before completion.
   if case in (1,2,9):
    count=64 if case==2 else 128;assert snapshots[1][1]==new[:count]+old[count:] and snapshots[1][2]==old and snapshots[101][0][4]>>24==1
   if case==4:assert snapshots[1][0][3:5]==[2,0x2101000]
   if case==5:assert snapshots[1][0][3:5]==[2,0x2113000]
   if case in (14,20,22):assert b'0xc006038c:' in trace
   if case in (1,5,7,11,17,23):assert b'0xc0015f84:' in trace
   if case==21:
    assert all(b'0x'+v+b':' in trace for v in (b'c002d030',b'c0083428',b'c00833f0',b'c0083374')) and b'0xc006f178:' not in trace
   if case==20:assert snapshots[20][0][9]&255==0 and src!=shd and b'0xc001613c:' not in trace
   if case in (15,16):assert src!=old and b'0xc0015ab4:' in trace
 for x,y in zip(r['cases'][:28],r['cases'][28:]):assert x['events']==y['events'] and x['exit']==y['exit']
 # Independent new recovery-boundary experiments; never equate ready with resumed.
 recovery=json.loads((out/'results_recovery.json').read_text());assert len(recovery['cases'])==8
 for vi in range(2):
  for case in range(28,32):
   row=recovery['cases'][vi*4+case-28];assert (row['vsb'],row['case'],row['exit'])==(vi,case,0)
   raw=gzip.decompress((out/f'{vi}_{case}.records.gz').read_bytes());assert raw and len(raw)%2112==0;ev=[];st={}
   for pos in range(0,len(raw),2112):
    h=list(struct.unpack_from('<16I',raw,pos));assert h[:2]==[0x52394c43,300+case] and h[5]==len(ev) and h[6]==0x39 and h[2] not in (99,90)
    src=raw[pos+64:pos+1088];shd=raw[pos+1088:pos+2112];assert src==shd==old
    ev.append(dict(header=h,source_sha256=sha(src),shadow_sha256=sha(shd)));st[h[2]]=h
   assert ev==row['events'] and st[0][3:5]==[64,3112]
   assert st[20][3:5]==([4,0x5000000] if case==29 else [2,0x2100000]) and st[120][3:5]==[1,0x3300000]
   trace=gzip.decompress((out/f'{vi}_{case}.trace.gz').read_bytes())
   if case in (28,29):assert st[60][3:5]==[0xffffffce,1] and st[61][3:5]==[1,0xc06a24e4] and b'0xc0001c7c:' in trace
   if case==30:assert st[60][3:5]==[0xffffffe7,0] and b'0xc0000d80:' in trace
   if case==31:assert st[60][3:5]==[0xc06a2544,6] and st[61][3:5]==[0xc06a24e4,0] and b'0xc00018f0:' in trace
   assert b'0xc0015fa0:' not in trace
 for x,y in zip(recovery['cases'][:4],recovery['cases'][4:]):assert x['events']==y['events'] and x['exit']==y['exit']
 # Preserve all previous research, not just selected source files.
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
 assert not subprocess.check_output(['git','diff',BASE,'--',*names],cwd=ROOT)
 p=json.loads((ROOT/'reports/recovery_r13/provenance.json').read_text())
 for n,h in p['sha256'].items():assert sha((ROOT/n).read_bytes())==h,n
 a=json.loads((out/'audit.json').read_text());assert len(a['ranges'])==20 and [c['service'] for c in a['contexts']]==[17,35] and all(c['progress_argument']==0 for c in a['contexts'])
 m=json.loads((out/'models.json').read_text());assert m['admission']['states']==1180 and m['admission']['transitions']==2181 and m['admission']['completed_scan_edges']==40 and not m['recovery_capabilities']['cancellation'] and not m['recovery_capabilities']['restoration']
 msg='PASS:64 R14 ARM cases;58 normal exits;6 expected GPIO faults;32 V30 frames/VSB;exact cross-VSB records;owner/ticket/pages/close/stall oracles;201 R13 manifest entries and all R1-R13 tracked paths unchanged'
 (out/'independent_verification.log').write_text(msg+'\n');print(msg)
 paths=[p for d in ('tests/recovery_r14','tools/recovery_r14','reports/recovery_r14') for p in sorted((ROOT/d).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p!=out/'provenance.json']
 paths += [p for p in (ROOT/'RECOVERY_R14_RAPPORT_FR.md',ROOT/'documents/RECOVERY_R14_GRAPHICS_CONTEXT_MAP_FR.md',ROOT/'documents/RECOVERY_R14_ADMISSION_ARCHITECTURE_FR.md',ROOT/'tests/run_recovery_r14.sh') if p.exists()]
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; native code RX; no hardware replies; serialized laboratory transitions; no native cancellation proof','native_cases':64,'normal_exits':58,'expected_gpio_faults':6,'original_vsb_sha256':r['vsb_sha256'],'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}},indent=2)+'\n')
if __name__=='__main__':main()
