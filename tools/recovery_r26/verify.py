#!/usr/bin/env python3
"""Read saved ARM frames and native records independently of runner."""
import gzip,hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r26'
frames=(O/'arm-frames.bin').read_bytes();j=json.loads((O/'results.json').read_text())
assert len(frames)==32768 and hashlib.sha256(frames).hexdigest()==j['sha256'] and len(j['native_integration'])==16
for scene in range(8):
 a=gzip.decompress((O/f'0_{scene}.records.gz').read_bytes());b=gzip.decompress((O/f'1_{scene}.records.gz').read_bytes());assert a==b and len(a)==13*2112
 for f in range(4):
  target=frames[(scene*4+f)*1024:(scene*4+f+1)*1024]
  for phase,stage in enumerate((10+f,30+f,50+f)):
   r=a[(3*f+phase)*2112:(3*f+phase+1)*2112];h=struct.unpack_from('<16I',r)
   assert h[0]==0x52394c43 and h[1]==2600+scene and h[2]==stage and h[5]==3*f+phase
   assert r[64:1088]==target
   if phase:assert r[1088:2112]==target
   if phase==2:assert h[3]==8
 for v in range(2):
  t=gzip.decompress((O/f'{v}_{scene}.trace.gz').read_bytes()).decode()
  for pc in ('0xc0015824:','0xc0015ab4:','0xc001851c:'):assert pc in t
print('PASS independent: 32 ARM frames, 16 integration records, source/shadow and transport entry traces')
