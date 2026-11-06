#!/usr/bin/env python3
"""Read independent raw records; reject corruption, reordering and partial streams."""
import gzip,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r28';ref=(R/'reports/recovery_r26/arm-frames.bin').read_bytes();rows=json.loads((O/'results.json').read_text())['cases'];assert len(rows)==16
def verify_stream(stream,images,port):
 assert len(stream)==3168
 for f in range(3):
  for page in range(8):
   g=stream[(f*8+page)*132:(f*8+page+1)*132];assert len(g)==132
   assert all(a==port for pc,a,v in g)
   assert all(pc==0xc00184a4 for pc,a,v in g[:4]) and [v&255 for pc,a,v in g[:4]]==[0xb0+page,0x40,0x10,0]
   assert all(pc==0xc001862c for pc,a,v in g[4:])
   assert bytes(v&255 for pc,a,v in g[4:])==images[f][page*128:(page+1)*128]
for scene in range(8):
 for vi in range(2):
  raw=gzip.decompress((O/f'{vi}_{scene}.records.gz').read_bytes());data=gzip.decompress((O/f'{vi}_{scene}.writes.gz').read_bytes())
  assert len(raw)==7*2112 and len(data)==3168*12
  rec=[raw[i*2112:(i+1)*2112] for i in range(7)];hs=[struct.unpack_from('<16I',x) for x in rec]
  assert [h[2] for h in hs]==[10,20,11,21,30,40,50] and all(h[0]==0x52394c43 and h[1]==2800+scene and h[5]==i for i,h in enumerate(hs))
  images=[rec[i][64:1088] for i in (0,2,5)]
  assert images[:2]==[ref[scene*4096:scene*4096+1024],ref[scene*4096+1024:scene*4096+2048]]
  assert images[2]==bytes((i*37+13)&255 for i in range(1024))
  assert all(rec[after][1088:2112]==images[j] for j,after in enumerate((1,3,6)))
  stream=list(struct.iter_unpack('<III',data));port=hs[0][15]+0x3c;verify_stream(stream,images,port)
  mutated=stream.copy();pc,a,v=mutated[10];mutated[10]=(pc,a,v^1)
  for bad in (mutated,stream[:-132],stream[132:264]+stream[:132]+stream[264:]):
   try:verify_stream(bad,images,port);raise RuntimeError('negative witness not detected')
   except AssertionError:pass
print('PASS independent: 16 complete simulated-worker captures, page commands, V30 and Korg bytes; corruption/order/partial rejected')
