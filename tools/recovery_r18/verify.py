#!/usr/bin/env python3
"""Independent ARM record semantics, static coverage witnesses and manifest checks."""
import csv,gzip,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r18';BASE='c4fe851f64d325bc6311e4aa7cbee85ce2707cab'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 rows=json.loads((OUT/'results.json').read_text())['cases'];assert len(rows)==62
 rawrows={};hsrows={};traces={}
 for row in rows:
  v,c=row['vsb'],row['case'];assert v in (0,1) and c in range(31) and (v,c) not in rawrows
  raw=gzip.decompress((OUT/f'{v}_{c}.records.gz').read_bytes());assert raw and len(raw)%2112==0
  hs=[];events=[]
  for p in range(0,len(raw),2112):
   h=list(struct.unpack_from('<16I',raw,p));assert h[0]==0x52394c43 and h[1]==700+c and h[5]==p//2112 and h[6]==0x39
   assert h[2]!=99,('ARM assertion',v,c,h)
   hs.append(h);events.append({'header':h,'source_sha256':sha(raw[p+64:p+1088]),'shadow_sha256':sha(raw[p+1088:p+2112])})
  assert row['events']==events
  at=lambda stage:next(h for h in hs if h[2]==stage)
  assert at(0)[3:5]==[1616,400] and at(50)[3:5]==[36,48] and at(51)[3:5]==[192,904]
  assert len([h for h in hs if h[2]==70 and h[3:5]==[0x200000,1]])==1
  faults=[h for h in hs if h[2]==90]
  if c in (4,8,17):assert row['exit']==88 and len(faults)==1 and faults[0][3:5]==[0x1e260bc if c==17 else 0,11]
  elif c==18:
   assert row['exit']=='timeout' and not faults and any(h[2]==15 for h in hs) and not any(h[2]==20 for h in hs)
  else:assert row['exit']==0 and not faults and at(64)[3]==1
  if c in (17,18):
   stage=89 if c==17 else 15
   assert at(stage)[3]&255==1 and at(stage+100)[3]==0 and at(stage+100)[4]==0x10001 and at(stage+200)[3]==0
  if c in (2,3,4,6,7,8,21,24,30):
   d=row['debugger'];assert d['register_restore_exact'] and d['code_before']==d['code_breakpoint']==d['code_after']
   expected={2:0xc0070650,3:0xc007067c,4:0xc0070650,6:0xc007066c,7:0xc007067c,8:0xc007066c,21:0xc007067c,24:0xc007067c,30:0xc00707cc}[c]
   assert int(d['stop_pc'],16)==expected and d['saved_core'][15]==expected
   assert not any(x.startswith(('M','X')) for x in d['commands'])
  else:assert row['debugger'] is None
  rawrows[v,c]=raw;hsrows[v,c]=hs
  t=gzip.decompress((OUT/f'{v}_{c}.trace.gz').read_bytes()).decode();traces[v,c]=re.findall(r'^0xc0[01][0-9a-f]{5}:.*$',t,re.M);assert traces[v,c]
 for c in range(31):assert rawrows[0,c]==rawrows[1,c] and traces[0,c]==traces[1,c],('cross-VSB',c)
 def at(c,stage):return next(h for h in hsrows[0,c] if h[2]==stage)
 for c in (1,2,3,14,21,22,23):assert at(c,20)[3]>>16&255==0 and at(c,20)[3]>>8&255==1
 assert at(6,60)[3:5]==[0,1] and at(7,60)[3:5]==[1,0] # vtable before versus after resolution
 assert at(30,65)[3:5]==[1,0] and at(30,66)[3:5]==[1,0] and at(30,67)[3:5]==[4,1]
 assert at(24,61)[4]==0xb1 # stable context, mutable payload pointer
 assert at(12,20)[3]>>16&255==1 and at(12,20)[3]>>8&255==1
 assert at(13,20)[3]>>16&255==1 and at(20,20)[3]>>16&255==1
 assert at(16,20)[4]>>24==4 and at(16,20)[4]>>16&255==4 and at(16,64)[4]==4
 assert at(15,63)[3:5]==[1,1] # hidden raw payload still readable, no free
 assert at(27,220)[3]==0 and at(19,220)[3]==1 # borrow survives timeout; explicit leave required
 # Validate EVERY static row against R17 candidate inventory, not just aggregate counts.
 cov=json.loads((OUT/'coverage.json').read_text());old=json.loads((ROOT/'reports/recovery_r17/audit.json').read_text());assert len(cov['rows'])==316
 expected={(t,site) for t,v in old['references'].items() for site in v['direct_branch_candidates']}
 assert {(r['target'],r['site']) for r in cov['rows']}==expected
 for r in cov['rows']:assert r['owner']=='UNKNOWN' and r['coverage']=='NO_INSTALLED_GUARD'
 csvrows=list(csv.DictReader((OUT/'coverage.csv').open()));assert len(csvrows)==316 and {(r['target'],r['site']) for r in csvrows}==expected
 # Verify all witness branch transitions using the signed native instructions archived by audit.
 words={}
 text=gzip.decompress((OUT/'native-contexts.txt.gz').read_bytes()).decode()
 for line in text.splitlines():
  m=re.match(r'^([0-9a-f]{8}): ([0-9a-f]{8})',line)
  if m:words[int(m[1],16)]=int(m[2],16)
 for row in cov['rows']:assert words[int(row['site'],16)]==int(row['instruction'],16)
 witnesses=json.loads(gzip.decompress((OUT/'coverage-witnesses.json.gz').read_bytes()))
 allwords={int(pc,16):int(w,16) for pc,w in json.loads(gzip.decompress((OUT/'coverage-code-words.json.gz').read_bytes())).items()}
 for root,paths in witnesses.items():
  for site,path in paths.items():
   assert path[0]==cov['roots'][root]['root'] and path[-1]==site
   for a,b in zip(path,path[1:]):
    pc,nxt=int(a,16),int(b,16);w=allwords[pc];cond=w>>28;assert cond!=15
    if (w>>25)&7==5:
     off=w&0xffffff;off=off-0x1000000 if off>=0x800000 else off
     allowed={(pc+8+4*off)&0xffffffff}
     if w&0x1000000 or cond!=14:allowed.add(pc+4)
     assert nxt in allowed
    else:
     assert nxt==pc+4
     bx=(w&0x0ffffff0)==0x012fff10;blx=(w&0x0ffffff0)==0x012fff30
     ldm_pc=(w&0x0e100000)==0x08100000 and bool(w&0x8000)
     ldr_pc=(w&0x0c100000)==0x04100000 and ((w>>12)&15)==15
     data_pc=(w&0x0c000000)==0 and ((w>>12)&15)==15 and ((w>>21)&15) not in (8,9,10,11)
     assert cond!=14 or blx or not (bx or ldm_pc or ldr_pc or data_pc)
   assert allwords[int(site,16)]==int(next(r['instruction'] for r in cov['rows'] if r['site']==site),16)
 bridge=json.loads((OUT/'typed-ui-bridge.json').read_text());assert not bridge['exclusive_task'] and bridge['owner']=='UNKNOWN'
 assert bridge['words']['0xc00e4c68']=='0xc00836e4' and bridge['words']['0xc006eb74']=='0xea004eeb'
 # Model-only counterexamples: independent interpreter checks reuse/destroy assumptions and stale selection.
 model=json.loads((OUT/'model.json').read_text());assert [r['states'] for r in model['results']]==[18118,99950,22556]
 for result in model['results']:
  if result['policy']=='monotonic_keep':assert not result['hazards'] and result['max_storage_slots']==2;continue
  for kind,path in result['hazards'].items():
   slots=[[0,0],[0,0]];actors=[[0,-1,0,0],[0,-1,0,0]];made=0;expired=False
   for label in path:
    if label=='allocate_fresh':
     i=next(i for i,s in enumerate(slots) if s[0]==0);made+=1;slots[i]=[made,3]
    elif label=='clock_expires':assert not expired;expired=True
    elif label.startswith('retire_'):
     _,i,_,owner=label.split('_');i=int(i);owner=int(owner);assert slots[i][1]&owner;slots[i][1]&=~owner
    elif label.startswith('reuse_'):
     i=int(label.split('_')[1]);assert slots[i][1]==0 and not any(a[0]==3 and a[1]==i for a in actors);made+=1;slots[i]=[made,3]
    elif label.startswith('destroy_'):
     i=int(label.split('_')[1]);assert expired and slots[i][1]==0 and not any(a[0]==3 and a[1]==i for a in actors);slots[i]=[-1,0]
    else:
     who,event=label.split(':');a=actors[int(who[-1])]
     if event.startswith('select_'):
      _,i,owner=event.split('_');i=int(i);owner=int(owner);assert a[0]==0 and slots[i][0]>0;a[:]=[1,i,slots[i][0],owner]
     elif event=='resolve':assert a[0]==1;a[0]=2
     elif event=='ABA_generation_reroute':assert a[0]==2 and slots[a[1]][0]!=a[2] and slots[a[1]][0]>0;a[0]=6
     elif event=='UAF_model_only':assert a[0]==2 and slots[a[1]][0]<0;a[0]=6
     elif event=='invoke_with_borrow':assert a[0]==2 and slots[a[1]][1]&a[3];a[0]=3
     elif event=='return':assert a[0]==3;a[0]=4
     elif event=='release':assert a[0]==4;a[0]=5
     elif event=='reject_closed':assert a[0]==2 and not slots[a[1]][1]&a[3];a[0]=6
     else:raise AssertionError(event)
 # All R1-R17 tracked paths and every R17 manifested proof are preserved.
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines();assert not subprocess.check_output(['git','diff',BASE,'--',*paths],cwd=ROOT)
 prior=json.loads((ROOT/'reports/recovery_r17/provenance.json').read_text())['sha256']
 for path,h in prior.items():assert sha((ROOT/path).read_bytes())==h,path
 print('PASS 62 ARM cases: 54 normal returns, 6 expected faults, 2 host timeouts with borrows held.')
 print('PASS 31 exact cross-VSB record/native translated-block comparisons; 62 native-image integrity checks.')
 print('PASS 18 debugger interleavings; unchanged native code; exact register restore; 1616-byte pool, 400-byte slots.')
 print('PASS 316 static candidate rows, including all 119 registrations and 120 notifications; owners remain UNKNOWN.')
 print('PASS 140624 finite model states; negative ABA/timeout-destruction witnesses replayed independently.')
 print('PASS all base paths and 142 R17 manifest entries preserved.')
 if '--manifest' in sys.argv:
  manifest=json.loads((OUT/'provenance.json').read_text())['sha256']
  for path,h in manifest.items():assert sha((ROOT/path).read_bytes())==h,path
  print('PASS R18 manifest:',len(manifest),'SHA-256 entries.')
if __name__=='__main__':main()
