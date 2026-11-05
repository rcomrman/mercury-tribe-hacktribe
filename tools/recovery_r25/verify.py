#!/usr/bin/env python3
"""Re-read R25 snapshots independently; no VSB or rebuild required."""
import gzip,hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r25';B=R/'build/recovery_r25'
frames=(B/'frames.bin').read_bytes();j=json.loads((O/'results.json').read_text());assert hashlib.sha256(frames).hexdigest()==j['frame_sha256'] and len(j['cases'])==32
for scene in range(8):
 for worker in range(2):
  raw=gzip.decompress((O/f'0_{scene}_{worker}.records.gz').read_bytes());assert raw==gzip.decompress((O/f'1_{scene}_{worker}.records.gz').read_bytes())
  assert len(raw)%2112==0;records=[raw[i:i+2112] for i in range(0,len(raw),2112)]
  for i,r in enumerate(records):
   h=struct.unpack_from('<16I',r);assert h[0]==0x52394c43 and h[1]==2500+2*scene+worker and h[5]==i and h[2]!=99
   assert r[64:1088]==frames[scene*4096:scene*4096+1024]
  last=records[-1];h=struct.unpack_from('<16I',last)
  if worker:assert h[2:5]==(90,0xbc,11)
  else:
   assert len(records)==10 and h[2]==20 and last[64:1088]==last[1088:2112]
   for page in range(8):assert struct.unpack_from('<16I',records[1+page])[2:5]==(30+page,1,page)
  for vi in range(2):
   t=gzip.decompress((O/f'{vi}_{scene}_{worker}.trace.gz').read_bytes()).decode()
   for pc in ('0xc0015824:','0xc0015ab4:'):assert pc in t
   if worker:assert '0xc0015fa0:' in t and '0xc001613c:' in t
print('PASS 8 V30 presets: native pixel/comparator 8 pages, expected worker/sender fault, 16 cross-VSB pairs')
