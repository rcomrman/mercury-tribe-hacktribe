#!/usr/bin/env python3
"""Independent record and corruption/page-order checks, no replay runner imports."""
import gzip,hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r27';refs=(R/'reports/recovery_r26/arm-frames.bin').read_bytes();rows=json.loads((O/'results.json').read_text())['cases']
assert len(rows)==16
def check(writes,frame,address):
 assert len(writes)==1024 and all(a==address for a,v in writes)
 assert bytes(v&255 for a,v in writes)==frame
for scene in range(8):
 for vi in range(2):
  raw=gzip.decompress((O/f'{vi}_{scene}.records.gz').read_bytes());w=gzip.decompress((O/f'{vi}_{scene}.writes.gz').read_bytes());assert len(raw)==4224 and len(w)==8192
  h=struct.unpack_from('<16I',raw);assert h[0:4]==(0x52394c43,2700+scene,10,h[3])
  frame=refs[scene*4096:scene*4096+1024];assert raw[64:1088]==raw[1088:2112]==frame
  writes=list(struct.iter_unpack('<II',w));check(writes,frame,h[3]+0x3c)
  row=next(x for x in rows if x['vsb']==vi and x['scene']==scene);assert row['writes']==1024 and row['sha256']==hashlib.sha256(frame).hexdigest()
  bad=writes.copy();bad[0]=(bad[0][0],bad[0][1]^1)
  try:check(bad,frame,h[3]+0x3c);raise RuntimeError('corruption survived')
  except AssertionError:pass
  # Swap two unequal pages: choose a pair with distinct data rather than assume all differ.
  pages=[frame[i:i+128] for i in range(0,1024,128)]
  pair=next(((i,k) for i in range(8) for k in range(i+1,8) if pages[i]!=pages[k]),None)
  assert pair is not None;i,k=pair;bad=writes.copy();bad[i*128:(i+1)*128],bad[k*128:(k+1)*128]=bad[k*128:(k+1)*128],bad[i*128:(i+1)*128]
  try:check(bad,frame,h[3]+0x3c);raise RuntimeError('page swap survived')
  except AssertionError:pass
print('PASS independent: 16 ordered 1024-byte streams; corrupted byte and page swap rejected')
