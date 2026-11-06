#!/usr/bin/env python3
"""Interpret transition records and SPI streams independently of the runner."""
import gzip,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r29';j=json.loads((O/'results.json').read_text());assert len(j['cases'])==16
def check(stream,images,port):
 assert len(stream)==len(images)*1056
 for f,img in enumerate(images):
  for page in range(8):
   part=stream[(f*8+page)*132:(f*8+page+1)*132]
   assert len(part)==132 and all(addr==port for pc,addr,v in part)
   assert all(pc==0xc00184a4 for pc,addr,v in part[:4]) and [v&255 for pc,addr,v in part[:4]]==[0xb0+page,0x40,0x10,0]
   assert all(pc==0xc001862c for pc,addr,v in part[4:]) and bytes(v&255 for pc,addr,v in part[4:])==img[page*128:(page+1)*128]
for vi in range(2):
 for case in range(8):
  raw=gzip.decompress((O/f'{vi}_{case}.records.gz').read_bytes());data=gzip.decompress((O/f'{vi}_{case}.writes.gz').read_bytes());assert len(raw)==(4 if case==7 else 8)*2112 and len(data)%12==0
  rec=[raw[i*2112:(i+1)*2112] for i in range(len(raw)//2112)];heads=[struct.unpack_from('<16I',r) for r in rec]
  if case==7:
   assert [h[2] for h in heads]==[101,102,103,106] and all(h[0]==0x52394c43 and h[1]==2907 and h[5]==i for i,h in enumerate(heads))
   stream=list(struct.iter_unpack('<III',data));assert len(stream)==400
   mercury=rec[2][64:1088];port=heads[0][15]+0x3c
   for page in range(3):
    part=stream[page*132:(page+1)*132];assert all(a==port for pc,a,v in part)
    assert [v&255 for pc,a,v in part[:4]]==[0xb0+page,0x40,0x10,0]
    assert bytes(v&255 for pc,a,v in part[4:])==mercury[page*128:(page+1)*128]
   assert [v&255 for pc,a,v in stream[396:]]==[0xb3,0x40,0x10,0]
   continue
  assert [h[2] for h in heads]==[101,102,103,104,110,105,101,120]
  assert all(h[0]==0x52394c43 and h[1]==2900+case and h[5]==i for i,h in enumerate(heads))
  mercury=rec[2][64:1088];korg=bytes((i*37+13)&255 for i in range(1024));assert rec[-1][64:1088]==rec[-1][1088:2112]==korg
  stream=list(struct.iter_unpack('<III',data));images=[korg] if case==0 else [mercury,korg];port=heads[0][15]+0x3c;check(stream,images,port)
  if case==1:assert rec[3][1088:1216]!=rec[3][64:192] # before first page copy
  if case==2:assert rec[3][1088:1216]==rec[3][64:192] # after first page copy
  bad=stream.copy();pc,a,v=bad[-1];bad[-1]=(pc,a,v^1)
  try:check(bad,images,port);raise RuntimeError('corruption not detected')
  except AssertionError:pass
  try:check(stream[:-132],images,port);raise RuntimeError('partial restore not detected')
  except AssertionError:pass
print('PASS independent: 14 EXIT transitions, 2 fault stops, full page streams; corruption and partial restoration rejected')
