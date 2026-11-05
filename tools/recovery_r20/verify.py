#!/usr/bin/env python3
"""Independent raw evidence, model and historical-preservation checks. No VSB needed."""
import gzip,hashlib,json,re,struct,subprocess,sys
from collections import Counter
from pathlib import Path
from check_model import check
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r20'
BASE='dce3fdc74b8dd0a0168f8ae920375fab52c6b31a';PHASE1='a220be8a5ac338f5bf8af79d838a8e8e05127fca'
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
PLAN={1:[(0xc00707a4,1)],2:[(0xc00707cc,1)],3:[(0xc0070810,1)],4:[(0xc007067c,2)],5:[(0xc007067c,3)],6:[(0xc0041bb4,6)],7:[(0xc0085204,7)],8:[(0xc00851d0,4),(0xc0041bb4,6)],9:[(0xc00851d0,5)],21:[(0xc00853a8,8),(0xc0041bb4,6)],23:[(0xc0070650,3)]}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 result=json.loads((OUT/'results.json').read_text());assert result['vsb_sha256']==HASHES
 rows=result['cases'];assert len(rows)==48;seen=set();raws={};native={};heads={};restores=stops=0
 for row in rows:
  v,c=row['vsb'],row['case'];assert v in (0,1) and c in range(24) and (v,c) not in seen;seen.add((v,c))
  raw=gzip.decompress((OUT/f'{v}_{c}.records.gz').read_bytes());assert raw and len(raw)%2112==0
  events=[];hs=[]
  for p in range(0,len(raw),2112):
   h=list(struct.unpack_from('<16I',raw,p));assert h[:2]==[0x52394c43,900+c] and h[5]==p//2112 and h[6:8]==[0x39,0xc5]
   assert h[2]!=99,('ARM assertion',v,c,h)
   events.append(dict(header=h,source_sha256=sha(raw[p+64:p+1088]),shadow_sha256=sha(raw[p+1088:p+2112])));hs.append(h)
  assert events==row['events'];heads[v,c]=hs;raws[v,c]=raw
  at=lambda stage:next(h for h in hs if h[2]==stage)
  assert at(0)[3:5]==[136,336] and at(50)[3:5]==[1808,64] and at(51)[3:5]==[788,24] and at(52)[3:5]==[76,256]
  assert [h[3:5] for h in hs if h[2]==70]==[[0x200000,1]]
  faults=[h for h in hs if h[2]==90]
  if c in (6,7,8,21):
   assert row['exit']==87 and not faults and not any(h[2]==20 for h in hs)
   pc=0xc0085204 if c==7 else 0xc0041bb4
   assert at(81)[3:5]==[pc,2 if c==7 else 1]
   assert at(82)[4]==(76 if c==7 else 16)
   assert row['debugger'][-1]['core'][0]==at(82)[3],'actual free argument must be retained fixture storage'
  elif c in (14,22,23):
   assert row['exit']==88 and len(faults)==1 and faults[0][3:5]==[{14:0x1e260bc,22:0xc06a293c,23:0}[c],11] and not any(h[2]==20 for h in hs)
  elif c==13:assert row['exit']=='timeout' and not faults and at(15)[3]==0x10100 and not any(h[2]==20 for h in hs)
  else:assert row['exit']==0 and not faults and at(20)[3]==0
  assert row['free_entry_guard']=='0xc0028dd4' and 'Z0' in row['commands'] and 'Z0,c0028dd4,4' in row['wire_commands']
  assert 'z0,c0028dd4,4' not in row['wire_commands']
  assert not any(cmd.startswith(('M','X')) for cmd in row['commands'])
  ds=row['debugger'];assert [(int(d['pc'],16),d['action']) for d in ds]==PLAN.get(c,[])
  for d in ds:
   if d['action'] in (6,7):
    assert not d['resumed'] and not d['register_restore_exact'] and d['core'][15]==int(d['pc'],16);stops+=1
   else:
    assert d['resumed'] and d['register_restore_exact'] and d['code_before']==d['code_after'] and d['saved_core'][15]==int(d['pc'],16);restores+=1
  trace=gzip.decompress((OUT/f'{v}_{c}.trace.gz').read_bytes()).decode();lines=re.findall(r'^0xc0[01][0-9a-f]{5}:.*$',trace,re.M);assert lines
  native[v,c]=lines
  # Translation blocks are not execution traces; a separate free-entry breakpoint is mandatory above.
  assert not any(line.startswith(('0xc0028dd4:','0xc0008f50:')) for line in lines),'no native free block'
  if c in (0,1,2,3,4,5,6,7,8,9,10,11,12,16,18,19,21,23):assert any(line.startswith('0xc00851b4:') for line in lines)
  if c in (5,8,16):assert any(line.startswith('0xc0085078:') for line in lines)
  if c==21:assert all(any(line.startswith(pc) for line in lines) for pc in ('0xc00852b0:','0xc0085278:','0xc0030d28:','0xc0041b74:','0xc00705dc:'))
  gzip.decompress((OUT/f'{v}_{c}.stderr.gz').read_bytes()).decode()
 for c in range(24):assert raws[0,c]==raws[1,c] and native[0,c]==native[1,c],('cross VSB',c)
 def at(c,stage):return next(h for h in heads[0,c] if h[2]==stage)
 for c,exp in ((1,[0,0]),(2,[1,0]),(3,[1,1])):assert at(c,62)[3:5]==exp and at(c,30)[3]>>24==1
 assert at(4,63)[3:5]==[1,3] and at(4,120)[4]&0xffff==0x101
 assert at(5,64)[3]==0xc00e3f70 and at(5,120)[4]==0x101,'native callback still writes after destructor return'
 assert at(8,65)[3:5]==[0x101,1] and at(8,180)[4]&0xffff==0x101
 assert at(9,66)[3:5]==[1,0]
 assert at(10,120)[4]==0 and at(10,121)[4]==0x101
 assert at(11,15)[3]==0x20200 and at(11,20)[4]==0x1020200
 assert at(12,61)[3:5]==[1,1] and at(12,60)[3]==2
 for c,stage in ((13,15),(14,89)):
  assert at(c,stage)[3]==0x10100 and at(c,stage+100)[3:5]==[0x3010100,0x11020000]
 assert at(15,68)[3:5]==[4,4] and at(15,20)[4]==0x4040004
 for stage in (120,121,122,123):assert at(15,stage)[3:5]==[0x3010100,0x11020000]
 assert at(16,69)[3:5]==[0,0] and at(16,120)[4]==0x101
 assert at(17,120)[3:5]==[0x3010100,0x11020000]
 assert at(18,72)[3:5]==[1,1]
 assert at(20,120)[3:5]==[0x3010100,0x11020000] and at(20,20)[4]==0x1010001
 assert at(21,67)[3:5]==[4,1] and at(21,73)[3:5]==[1,2] and at(21,74)[3:5]==[0,2] and at(21,75)[3:5]==[0,0]
 assert at(22,89)[3]>>24==1 and at(22,189)[3]==0x01000000
 assert at(23,189)[3:5]==[0x3010101,0]
 for jsonname,txtname in (('native-map.json','native-map.txt.gz'),('supplement.json','supplement.txt.gz')):
  audit=json.loads((OUT/jsonname).read_text());words={}
  for line in gzip.decompress((OUT/txtname).read_bytes()).decode().splitlines():
   m=re.match(r'^\s*([0-9a-f]{8}):\s*([0-9a-f]{8})',line)
   if m:words[int(m[1],16)]=int(m[2],16)
  for pc,w in audit['contracts'].items():assert words[int(pc,16)]==int(w,16)
  for span in audit['ranges']:
   lo,hi=int(span['start'],16),int(span['end_exclusive'],16)
   # llvm-objdump abbreviates zero runs. Reconstruct them, then check actual bytes.
   assert lo<hi and not (lo|hi)&3
   data=b''.join(struct.pack('<I',words.get(pc,0)) for pc in range(lo,hi,4))
   assert sha(data)==span['sha256'],span['name']
 assert json.loads((OUT/'supplement.json').read_text())['native_owner_allocation_bytes']==76
 model=json.loads((OUT/'model.json').read_text());assert [r['policy'] for r in model['results']]==['mediated','quarantine','active_only','partial_domain','return_certificate']
 total=sum(check(r) for r in model['results'])
 assert not model['results'][0]['hazards'] and not model['results'][1]['hazards']
 # Preserve complete R19 tree and the phase1 commit, not just a selected manifest.
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',PHASE1],cwd=ROOT,text=True).splitlines()
 for path in names:
  old=subprocess.check_output(['git','show',f'{PHASE1}:{path}'],cwd=ROOT);assert (ROOT/path).read_bytes()==old,('historical modification',path)
 manifest=json.loads((ROOT/'reports/recovery_r19/provenance.json').read_text())['sha256'];assert len(manifest)==150
 for path,h in manifest.items():assert sha((ROOT/path).read_bytes())==h
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='recovery/mercury-dust'
 assert Counter(r['exit'] for r in rows)=={0:32,87:8,88:6,'timeout':2}
 print('PASS 48 ARM runs: 32 normal, 8 stops before native free, 6 expected faults, 2 host timeouts.')
 print(f'PASS 24 exact cross-VSB raw/native-block pairs; 48 native-byte checks; {restores} exact register restores, {stops} deliberately unresumed free boundaries.')
 print('PASS constructor/destructor overlap, selected references, reentry, owners, page deferral, saturation, unknown aliases, model+4 second subscription.')
 print(f'PASS {total} model states independently re-explored, every negative witness independently interpreted.')
 print(f'PASS all {len(names)} files at phase1 and all 150 R19 manifest checksums unchanged; no allocation free authority.')
 if '--manifest' in sys.argv:
  provenance=json.loads((OUT/'provenance.json').read_text())
  for path,h in provenance['sha256'].items():assert sha((ROOT/path).read_bytes())==h,('R20 manifest',path)
  print('PASS R20 manifest:',len(provenance['sha256']),'SHA-256 entries.')
if __name__=='__main__':main()
