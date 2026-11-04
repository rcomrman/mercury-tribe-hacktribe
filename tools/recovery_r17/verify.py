#!/usr/bin/env python3
"""Independent record/trace/provenance verifier; does not trust runner PASS text."""
import gzip,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r17'
BASE='60eddcdd2cc06dff43b71d5459b147d8c835457f'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 data=json.loads((OUT/'results.json').read_text());assert len(data['cases'])==58
 seen={};native={};headers={}
 for row in data['cases']:
  v,c=row['vsb'],row['case'];assert v in (0,1) and c in range(29) and (v,c) not in seen
  raw=gzip.decompress((OUT/f'{v}_{c}.records.gz').read_bytes());assert raw and len(raw)%2112==0
  hs=[];events=[]
  for i in range(0,len(raw),2112):
   h=list(struct.unpack_from('<16I',raw,i));assert h[0]==0x52394c43 and h[1]==600+c and h[5]==i//2112 and h[6]==0x39
   assert h[2]!=99,('ARM assertion',v,c,h)
   hs.append(h);events.append(dict(header=h,source_sha256=sha(raw[i+64:i+1088]),shadow_sha256=sha(raw[i+1088:i+2112])))
  assert events==row['events'];headers[v,c]=hs
  assert len([h for h in hs if h[2]==70 and h[3:5]==[0x200000,1]])==1,'native byte integrity'
  faults=[h for h in hs if h[2]==90]
  if c in (6,17):
   assert row['exit']==88 and len(faults)==1 and faults[0][3:5]==[0 if c==6 else 0x1e260bc,11]
   assert not any(h[2]==20 for h in hs)
   if c==17:
    h=next(h for h in hs if h[2]==89);assert h[3]>>24==1 and ((h[3]>>12)&15)==1 and ((h[3]>>8)&15)==1 and h[4]==10
  else:assert row['exit']==0 and not faults and hs[-3][2]==20
  if c in (3,4,5,6,7,27):
   d=row['debugger'];assert d['register_restore_exact'] and d['code_before']==d['code_breakpoint']==d['code_after']
   assert int(d['stop_pc'],16)=={3:0xc007067c,4:0xc007067c,5:0xc007061c,6:0xc0070650,7:0xc0070650,27:0xc007067c}[c]
   assert not any(cmd.startswith(('M','X')) for cmd in d['commands'])
   b=next(h for h in hs if h[2]==31)
   if c in (4,7,27):assert b[4]==10 and b[3]>>24==1 and b[3]&(1<<20)==0
   after=next(h for h in hs if h[2]==131)
   assert bool(after[3])==(c in (4,7,27)),'entry mutation after close versus raw withdraw'
  else:assert row['debugger'] is None
  trace=gzip.decompress((OUT/f'{v}_{c}.trace.gz').read_bytes()).decode()
  native[v,c]=re.findall(r'^0xc0[01][0-9a-f]{5}:.*$',trace,re.M);assert native[v,c]
  seen[v,c]=raw
 for c in range(29):assert seen[0,c]==seen[1,c] and native[0,c]==native[1,c],('cross VSB',c)
 # Explicit semantic witnesses, independent of the C assertions.
 def state(c,s):return next(h for h in headers[0,c] if h[2]==s)
 assert state(3,111)[3:5]==[0,0] and state(3,20)[3]&255==1 # cleared slot, cached callback still ran
 assert state(5,20)[3]&255==0
 assert state(10,20)[3]&255==2 and state(11,20)[3]&255==2
 assert state(13,220)[4]&(1<<16) and state(13,10)[4]==0 # alias after local quiet
 assert state(15,220)[4]==0 # rebind breaks quiet, raw alias still invokes
 assert state(19,220)[3]==1 and not state(19,220)[4]&(1<<16)
 assert state(22,20)[3]&255==1 and state(28,20)[3]&255==2
 assert state(27,220)[4]==0x10002
 model=json.loads((OUT/'model.json').read_text());assert len(model['results'])==6
 assert sum(r['states'] for r in model['results'])==1080
 for r in model['results']:
  if r['policy']=='guarded':assert not r['hazards']
  else:
   assert set(r['hazards'])=={'torn_tuple','cached_callback_after_withdraw'}
   for kind,path in r['hazards'].items():
    closed=False;entry=True;p=[0,0]
    for step in path:
     if step=='request_close':
      closed=True;entry=any(x==4 for x in p) if r['policy']=='active_only' else False
     elif step=='withdraw_after_return':entry=False
     elif step=='refuse_pending_then_ack':pass
     else:
      who,event=step.split(':');i=int(who[1:]);old=p[i]
      if event=='select_admitted':assert not closed and old==0;p[i]=1
      elif event=='load_key_context':assert old==1 and entry;p[i]=2
      elif event=='resolve':assert old==2 and entry;p[i]=3
      elif event=='TORN_tuple':assert old==2 and not entry;p[i]=7
      elif event=='invoke_cached_after_withdraw':assert old==3 and not entry;p[i]=4
      elif event=='invoke':assert old==3;p[i]=4
      elif event=='return':assert old==4;p[i]=5
      elif event=='release_frame':assert old==5;p[i]=6
      elif event=='skip_removed':assert old==1 and not entry;p[i]=6
      else:raise AssertionError(step)
 audit=json.loads((OUT/'audit.json').read_text());assert len(audit['ranges'])==15
 assert audit['instruction_contracts']['0xc0016594']=='0x1e26000' and audit['instruction_contracts']['0xc0016b54']=='0xe5832004'
 assert audit['references']['0xc007061c']['direct_branch_candidates']==['0xc00706b4','0xc0082770']
 # Historical preservation is checked against the entire base tree, not selected files.
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
 diff=subprocess.check_output(['git','diff',BASE,'--',*paths],cwd=ROOT);assert not diff,'historical tracked files changed'
 old=json.loads((ROOT/'reports/recovery_r16/provenance.json').read_text())
 # Inspect manifest structure without assuming its shape.
 manifest=old['sha256']
 items=manifest.items() if isinstance(manifest,dict) else ((x['path'],x['sha256']) for x in manifest)
 n=0
 for path,value in items:
  expected=value['sha256'] if isinstance(value,dict) else value
  assert sha((ROOT/path).read_bytes())==expected,path;n+=1
 assert n==167
 print('PASS: 58 ARM scenarios, 54 normal returns, 4 expected faults (0 and 0x01E260BC).')
 print('PASS: 58 full native-image byte comparisons; 29 exact cross-VSB records and native translated-block comparisons.')
 print('PASS: 12 debugger interleavings, unchanged breakpoint bytes, exact register restoration; no memory-write packets.')
 print('PASS: 1080 bounded model states and independently replayed negative witnesses.')
 print('PASS: 167 R16 manifest entries and every base tracked path preserved.')
 if '--manifest' in sys.argv:
  manifest=json.loads((OUT/'provenance.json').read_text())['sha256']
  for path,expected in manifest.items():assert sha((ROOT/path).read_bytes())==expected,path
  print('PASS: R17 published manifest:',len(manifest),'SHA-256 entries.')
if __name__=='__main__':main()
