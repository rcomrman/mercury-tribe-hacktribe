#!/usr/bin/env python3
"""Standalone archive/phase/image oracles. Does not call run.decode or run.validate."""
import gzip,hashlib,json,re,struct,subprocess
from pathlib import Path
from models import explore
ROOT=Path(__file__).resolve().parents[2]
BASE='9c4ba62541648ff057800c3b98619cdaa30092d8'
CHECKPOINT='58bbfba748f499135a44170d170ec36d63023fa4'
FAULTS={4,8,10,12,16,17,19}
OBS={1:[(1,1,1,1,64)],2:[(1,1,1,1,384)],3:[(1,1,1,1,384)],4:[(89,1,1,1,384)],5:[(1,0,0,3,1024)],6:[(1,2,0,1,1024)],7:[(1,1,0,1,384)],8:[(1,1,0,1,384),(89,1,0,1,384)],9:[(1,1,0,1,384)],10:[(89,1,1,1,384)],11:[(1,0,0,3,0)],12:[(89,2,0,3,1024)],13:[(1,0,0,3,1024)],14:[(1,0,0,3,1024)],15:[(1,3,0,1,128)],16:[(89,1,1,1,384)],17:[(1,1,1,1,384),(2,2,0,3,1024),(89,2,0,3,1024)],18:[(1,0,1,3,1024)],19:[(1,4,1,3,0),(89,4,1,3,0)]}
ENDS={0:(0,32),1:(0,1),2:(0,1),3:(1,0),5:(0,1),6:(2,0),7:(1,0),9:(1,0),11:(0,0),13:(0,1),14:(0,0),15:(3,0),18:(0,0)}
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(raw,case,offset=200):
 assert raw and len(raw)%2112==0
 rows=[]
 for pos in range(0,len(raw),2112):
  h=struct.unpack_from('<16I',raw,pos);a=raw[pos+64:pos+1088];b=raw[pos+1088:pos+2112]
  assert h[:2]==(0x52394c43,offset+case) and h[5]==len(rows) and h[6]==0x39
  rows.append({'header':list(h),'source_sha256':sha(a),'shadow_sha256':sha(b),'different_bytes':sum(x!=y for x,y in zip(a,b))})
 return rows

def main():
 out=ROOT/'reports/recovery_r13';r=json.loads((out/'results.json').read_text());assert not r['exploratory'] and len(r['cases'])==40
 frames=(ROOT/'build/recovery_r13/frames.bin').read_bytes();oracle=json.loads((ROOT/'reports/recovery_r1/results.json').read_text())['frames_sha256'];assert len(frames)==32768 and sha(frames)==oracle==r['frames_sha256']
 initial=bytes([0x11])*1024;fresh=bytes([0xee])*1024;partial=fresh[:384]+initial[384:];mixed=initial[:384]+fresh[384:];firstpage=fresh[:128]+initial[128:]
 bar=bytearray(initial)
 for x in range(9,65):bar[896+x]=0x71
 partialbar=partial[:896]+bar[896:]
 comparisons=[]
 for vi in range(2):
  for case in range(20):
   row=r['cases'][vi*20+case];assert (row['vsb'],row['case'])==(vi,case)
   stem=f'{vi}_{case}';raw=gzip.decompress((out/(stem+'.records.gz')).read_bytes());events=parse(raw,case);assert events==row['events'];trace=gzip.decompress((out/(stem+'.trace.gz')).read_bytes())
   assert row['exit']==(88 if case in FAULTS else 0)
   assert events[0]['header'][2:5]==[0,32,3112] and not any(e['header'][2]==99 for e in events)
   stages={e['header'][2]:e for e in events}
   for stage,phase,pending,reader,written in OBS.get(case,[]):
    h=stages[stage]['header'];assert h[3:5]==[phase,(pending<<24)|(reader<<16)|written],(vi,case,stage,h)
   def frame(stage,a,b):
    e=stages[stage];assert e['source_sha256']==sha(a) and e['shadow_sha256']==sha(b),(vi,case,stage)
   if case in FAULTS:
    assert events[-1]['header'][2:5]==[90,0x01e260bc,11] and sum(e['header'][2]==90 for e in events)==1
    assert b'0xc0016c18:' in trace
   else:
    assert events[-1]['header'][2]==20 and tuple(events[-1]['header'][3:5])==ENDS[case]
    assert 90 not in stages
   if case==0:
    shots=[e for e in events if e['header'][2]==1];assert len(shots)==32
    for n,e in enumerate(shots):assert e['header'][3:5]==[n,n+1] and e['source_sha256']==e['shadow_sha256']==sha(frames[n*1024:(n+1)*1024])
   if case==1:frame(1,fresh[:64]+initial[64:],initial);frame(20,fresh,fresh)
   if case==2:frame(1,partial,partial);frame(20,fresh,fresh)
   if case==3:frame(1,partialbar,initial)
   if case==4:frame(90,partialbar,firstpage)
   if case==5:frame(1,frames[:1024],frames[:1024]);assert stages[1]['header'][9]>>8&255==1
   if case in (6,14):frame(1,fresh,mixed)
   if case==7:frame(1,bytes(1024),initial);assert b'0xc0015f84:' in trace
   if case in (8,16):frame(90,partial,firstpage)
   if case==9:frame(1,partial,partial);assert stages[1]['header'][9]&255==0
   if case==10:frame(90,partial,initial);assert b'0xc00162c4:' in trace
   if case==11:frame(1,initial,initial);assert stages[1]['header'][9]>>8&255==1 and b'0xc001613c:' not in trace
   if case==12:frame(90,fresh,firstpage)
   if case==13:frame(1,fresh,fresh)
   if case==15:frame(1,fresh[:128]+initial[128:],initial)
   if case==16:assert stages[88]['header'][3:5]==[1,0] and b'0xc006040c:' in trace
   if case==17:frame(1,partial,initial);frame(90,fresh,firstpage);assert b'0xc002a7ec:' in trace
   if case==18:frame(1,frames[:1024],initial);assert stages[18]['header'][3:5]==[32,0x00200020] and b'0xc0015fa0:' not in trace
   if case==19:frame(90,bar,bar)
   if case in (5,6,18):
    assert all(b'0x'+addr+b':' in trace for addr in (b'c002d030',b'c0083428',b'c00833f0',b'c0083374')) and b'0xc006f178:' not in trace
   if case in (3,4,16,19):assert b'0xc006038c:' in trace
   if case not in FAULTS:assert b'0xc001613c:' not in trace
   recovered=out/'recovered_original/reports/recovery_r13';old_raw=gzip.decompress((recovered/(stem+'.records.gz')).read_bytes());old=parse(old_raw,case)
   # Only new diagnostic stages88(case16) and18(case18) differ. Never relabel old archives.
   stripped=[dict(e,header=list(e['header'])) for e in events if not (case==16 and e['header'][2]==88) and not (case==18 and e['header'][2]==18)]
   for i,e in enumerate(stripped):e['header'][5]=i
   assert stripped==old,(vi,case,'unexpected original/final difference')
   old_trace=gzip.decompress((recovered/(stem+'.trace.gz')).read_bytes());native=lambda t:re.findall(rb'^0xc0[0-1][0-9a-f]{5}:.*$',t,re.M)
   comparisons.append({'vsb':vi,'case':case,'raw_records_identical':raw==old_raw,'identical_after_explicit_new_diagnostic_records_removed':True,'native_instruction_lines_identical':native(trace)==native(old_trace)})
 for a,b in zip(r['cases'][:20],r['cases'][20:]):assert a['events']==b['events'] and a['exit']==b['exit']
 m=json.loads((out/'models.json').read_text());assert m['participating_protocol']==explore()=={'states':168,'transitions':252,'complete_scan_edges_checked':6,'draw_states_with_deferred_request':27,'max_commits':2,'pages':8}
 graph=json.loads((out/'access_graph.json').read_text());assert len(graph['ranges'])==31 and len(graph['branch_edges'])==118 and len(graph['coverage'])==14 and not any(x['installed_in_native_firmware'] for x in graph['coverage'])
 old=json.loads((ROOT/'reports/recovery_r12/results.json').read_text())
 for row in old['cases']:
  raw=gzip.decompress((ROOT/f'reports/recovery_r12/{row["vsb"]}_{row["case"]}.records.gz').read_bytes());events=parse(raw,row['case'],100);assert events==row['events']
  if row['case'] in (4,17,24):
   e=next(x for x in events if x['header'][2]==1);n=64 if row['case']==24 else 384;assert e['shadow_sha256']==sha(fresh[:n]+initial[n:])
 manifest=json.loads((out/'recovered_original/manifest.json').read_text())
 for name,expected in manifest.items():assert sha((out/'recovered_original'/name).read_bytes())==expected
 oldfiles=subprocess.run(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines();assert not subprocess.run(['git','diff',BASE,'--',*oldfiles],cwd=ROOT,capture_output=True,check=True).stdout
 (out/'original_final_comparison.json').write_text(json.dumps({'scope':'Genuine original versus new replay; differences limited to diagnostic records16/18; raw archives both retained','cases':comparisons},indent=2)+'\n')
 subprocess.run(['git','merge-base','--is-ancestor',CHECKPOINT,'HEAD'],cwd=ROOT,check=True)
 message='PASS:40 R13 cases;32 V30 images/VSB;26 normal and14 expected faults;DRAW/READ/CRITICAL/FAULT oracles;52 R12 archives;92 recovered originals intact;R1-R12 unchanged'
 (out/'independent_verification.log').write_text(message+'\n')
 paths=[p for d in ('tests/recovery_r13','tools/recovery_r13','reports/recovery_r13') for p in sorted((ROOT/d).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p!=out/'provenance.json']
 paths.extend(ROOT/p for p in ('RECOVERY_R13_RAPPORT_FR.md','documents/RECOVERY_R13_GRAPHICS_ACCESS_MAP_FR.md','documents/RECOVERY_R13_PUBLICATION_ARCHITECTURES_FR.md','tests/run_recovery_r13.sh'))
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'checkpoint_commit':CHECKPOINT,'scope':'RESEARCH_ONLY; genuine recovered originals separated from new replay; no hardware/RTOS concurrency claim','native_cases':40,'normal_process_exits':26,'expected_fault_exits':14,'v30_images_per_vsb':32,'exact_cross_vsb_records':True,'independent_oracles':'Standalone phase, byte-image, status and trace checks; no import from runner','recovered_original_files_checked':len(manifest),'r12_records_reparsed':len(old['cases']),'all_r1_r12_tracked_paths_unchanged':True,'checkpoint_ancestor_verified':True,'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}},indent=2)+'\n')
 print(message)
if __name__=='__main__':main()
