#!/usr/bin/env python3
"""Independent R19 record, native-path, bounded-witness and provenance verifier."""
import gzip,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r19';BASE='6808871b54c10e130e085ab4e658bc8bf3cbf1bb'
PC={1:0xc00707cc,2:0xc00707cc,3:0xc00707a4,4:0xc00707cc,5:0xc0070810,6:0xc00707cc,7:0xc00707cc,8:0xc00707cc,9:0xc00707cc,14:0xc007067c,15:0xc0070650,16:0xc007067c,30:0xc0070778}
SNAPS={1,10,11,12,15,20,30,31,80,89}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 rows=json.loads((OUT/'results.json').read_text())['cases'];assert len(rows)==62
 rawrows={};groups={};headers={};native={}
 for row in rows:
  v,c=row['vsb'],row['case'];assert v in (0,1) and c in range(31) and (v,c) not in rawrows
  raw=gzip.decompress((OUT/f'{v}_{c}.records.gz').read_bytes());assert raw and len(raw)%2112==0;hs=[];events=[]
  for p in range(0,len(raw),2112):
   h=list(struct.unpack_from('<16I',raw,p));assert h[0]==0x52394c43 and h[1]==800+c and h[5]==p//2112 and h[6]==0x39
   assert h[2]!=99,('ARM assertion',v,c,h)
   hs.append(h);events.append(dict(header=h,source_sha256=sha(raw[p+64:p+1088]),shadow_sha256=sha(raw[p+1088:p+2112])))
  assert events==row['events'];headers[v,c]=hs
  at=lambda stage:next(h for h in hs if h[2]==stage)
  assert at(0)[3:5]==[836,100] and at(50)[3:5]==[1616,48] and at(51)[3:5]==[256,1984]
  assert len([h for h in hs if h[2]==70 and h[3:5]==[0x200000,1]])==1
  gs=[]
  for i,h in enumerate(hs):
   if h[2] not in SNAPS:continue
   children=[];j=i+1
   while j<len(hs) and hs[j][2]>=100:children.append(hs[j]);j+=1
   assert [x[2] for x in children]==list(range(h[2]+100,h[2]+100+len(children)))
   gs.append((h,children))
  groups[v,c]=gs
  faults=[h for h in hs if h[2]==90]
  if c in (15,20,24,25):assert row['exit']==88 and len(faults)==1 and faults[0][3:5]==[{15:0,20:0xc06a293c,24:0xc06a293c,25:0x1e260bc}[c],11] and not any(h[2]==20 for h in hs)
  elif c==7:assert row['exit']==87 and at(81)[3:5]==[1,0] and not faults and not any(h[2]==20 for h in hs)
  elif c==26:assert row['exit']=='timeout' and not faults and not any(h[2]==20 for h in hs) and any(h[2]==15 for h in hs)
  else:assert row['exit']==0 and not faults and any(h[2]==20 for h in hs)
  if c in PC:
   d=row['debugger'];assert int(d['stop_pc'],16)==PC[c] and d['code_before']==d['code_breakpoint']
   assert not any(x.startswith(('M','X')) for x in d['commands'])
   if c==7:assert not d['register_restore_exact'] and not d['constructor_resumed']
   else:assert d['register_restore_exact'] and d['code_before']==d['code_after'] and d['saved_core'][15]==PC[c]
  else:assert row['debugger'] is None
  t=gzip.decompress((OUT/f'{v}_{c}.trace.gz').read_bytes()).decode();lines=re.findall(r'^0xc0[01][0-9a-f]{5}:.*$',t,re.M);assert lines;native[v,c]=lines;rawrows[v,c]=raw
  if c in (7,21,23):
   assert any(x.startswith('0xc0041b74:') for x in lines)
   assert not any(x.startswith(('0xc0028dd4:','0xc0008f50:')) for x in lines),'no native free in empty-inverse destructor experiment'
  if c==22:assert all(any(x.startswith(a) for x in lines) for a in ('0xc006eae0:','0xc0082550:','0xc0082728:','0xc007061c:'))
  if c in (20,24):assert any(x.startswith('0xc000a3c4:') for x in lines)
 for c in range(31):assert rawrows[0,c]==rawrows[1,c] and native[0,c]==native[1,c],('cross VSB',c)
 def at(c,stage):return next(h for h in headers[0,c] if h[2]==stage)
 def group(c,stage):return next((h,ch) for h,ch in groups[0,c] if h[2]==stage)
 for c in (1,2,3,4,5,6,7,8):
  h,ch=group(c,30);assert h[3]>>24==1 and ch[0][3]>>24==1 and not ch[0][3]&(1<<16),'constructor must remain live'
 for c,expected in ((3,[0,0]),(4,[1,0]),(5,[1,1]),(6,[1,0])):assert at(c,63)[3:5]==expected
 for c in (3,4,5,8):assert group(c,20)[1][0][3]==0x04010101
 assert group(6,20)[1][0][3]==0x03010100 and group(6,20)[1][0][4]>>16==0x0101
 assert at(7,65)[3:5]==[1,0] and group(7,80)[0][3]>>24==1
 assert at(8,66)[3:5]==[1,0]
 assert group(2,20)[0][4]>>24==0 and group(2,20)[0][4]>>16&255==1
 assert group(9,20)[0][4]>>24==3 and len(group(9,20)[1])==2
 assert at(14,67)[3:5]==[1,0] and at(15,67)[3:5]==[0,1] and at(16,67)[3:5]==[0,1]
 assert group(19,20)[1][0][3]>>24==5 and not group(19,20)[1][0][3]&1,'full native subject must not be marked live or detached'
 assert group(20,89)[0][3]>>24==1 and not group(20,89)[1][0][3]&(1<<16)
 assert at(24,92)[3:5]==[1,0],'whole UI constructor remains partial at heap boundary'
 for c,stage in ((25,89),(26,15)):
  h,ch=group(c,stage);assert h[3]==0x00010101 and ch[0][3]==0x03010100 and ch[0][4]&65535==0x0101
 assert at(30,71)[3:5]==[1,1] and group(30,20)[1][0][3]>>24==5 and not group(30,20)[1][0][3]&1
 # Native ownership contracts checked against archived disassembly words, independently of runner text.
 audit=json.loads((OUT/'ownership.json').read_text());words={}
 for line in gzip.decompress((OUT/'native-ownership.txt.gz').read_bytes()).decode().splitlines():
  m=re.match(r'^\s*([0-9a-f]{8}):\s*([0-9a-f]{8})',line)
  if m:words[int(m[1],16)]=int(m[2],16)
 for pc,w in audit['contracts'].items():assert words[int(pc,16)]==int(w,16),(pc,w)
 assert len(audit['references']['0xc00826a8']['branches'])==8 and len(audit['references']['0xc008241c']['branches'])==8
 assert audit['contracts']['0xc006e89c']=='0xc0691244' and audit['contracts']['0xc006e8a4']=='0xc0348844'
 assert any(x['status']=='INCONNU' for x in audit['ownership_graph'])
 # Independent interpreter of every negative witness, including actual return versus inverse publication.
 model=json.loads((OUT/'model.json').read_text());assert [r['states'] for r in model['results']]==[1397,3934,11793,4795]
 for result in model['results']:
  if result['policy'] in ('guard_before_constructor','permanent_quarantine'):assert not result['hazards'];continue
  for kind,path in result['hazards'].items():
   p=[0,0];closed=retired=pub=inv=0;a=[[0,-1],[0,-1]]
   for label in path:
    if label.startswith('w'):
     actor,event=label.split(':');who=int(actor[1:]);phase,target=a[who]
     if event.startswith('select_'):i=int(event.split('_')[1]);assert phase==0 and pub&(1<<i);a[who]=[1,i]
     elif event=='resolve':assert phase==1 and pub&(1<<target);a[who][0]=2
     elif event=='TORN_TUPLE':assert phase==1 and not pub&(1<<target);a[who][0]=7
     elif event=='invoke':assert phase==2 and p[target]==5 and not closed&(1<<target);a[who][0]=3
     elif event=='reject_uncommitted_or_closed':assert phase==2 and (p[target]!=5 or closed&(1<<target));a[who][0]=6
     elif event=='return':assert phase==3;a[who][0]=4
     elif event=='release':assert phase in (4,6);a[who][0]=5
     else:raise AssertionError(label)
    else:
     event,raw_i=label.rsplit('_',1);i=int(raw_i);bit=1<<i
     if event=='begin':assert p[i]==0 and not closed&bit and not any(1<=x<=4 for x in p);p[i]=1
     elif event=='close':assert not closed&bit;closed|=bit
     elif event=='tuple':assert p[i]==1;p[i]=2
     elif event in ('publish','LATE_PUBLISH'):assert p[i]==2;p[i]=3;pub|=bit;assert event!='LATE_PUBLISH' or retired&bit
     elif event in ('inverse','LATE_INVERSE'):assert p[i]==3;p[i]=4;inv|=bit;assert event!='LATE_INVERSE' or retired&bit
     elif event=='actual_return':assert p[i]==4;p[i]=5
     else:
      assert closed&bit and not retired&bit
      if event=='RETIRE_BEFORE_RETURN':assert 1<=p[i]<=4
      elif event=='RETIRE_WITH_FRAME':assert any(x[0] in (1,2,3,4,6) for x in a)
      else:assert event=='physical_detach'
      if result['policy']=='inverse_empty_only':assert not inv&bit
      if result['policy']=='commit_at_inverse':assert p[i]>=4
      retired|=bit;pub&=~bit;inv&=~bit
 # Historical preservation: all files in base, plus 154 actual R18 checksums.
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines();assert not subprocess.check_output(['git','diff',BASE,'--',*paths],cwd=ROOT)
 old=json.loads((ROOT/'reports/recovery_r18/provenance.json').read_text())['sha256'];assert len(old)==154
 for path,h in old.items():assert sha((ROOT/path).read_bytes())==h,path
 print('PASS 62 ARM scenarios: 50 normal, 8 expected faults, 2 controlled incomplete-constructor exits, 2 host timeouts.')
 print('PASS 31 exact cross-VSB records/native translated-block comparisons and 62 native-image byte checks.')
 print('PASS 26 debugger interleavings: 24 exact register restores; 2 explicit stops before native constructor return.')
 print('PASS constructor-live/inverse/tuple/return distinctions, native empty-inverse destructor paths without free.')
 print('PASS 21919 bounded model states and independently replayed negative transaction witnesses.')
 print('PASS shared UI root contracts; all base files and 154 R18 manifest entries preserved.')
 if '--manifest' in sys.argv:
  manifest=json.loads((OUT/'provenance.json').read_text())['sha256']
  for path,h in manifest.items():assert sha((ROOT/path).read_bytes())==h,path
  print('PASS R19 manifest:',len(manifest),'SHA-256 entries.')
if __name__=='__main__':main()
