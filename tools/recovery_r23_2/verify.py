#!/usr/bin/env python3
"""Reparse saved raw records without depending on the fixture assertions."""
import gzip,struct
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'reports/recovery_r23_2'
for c in range(4):
 raw=gzip.decompress((O/f'0_{c}.records.gz').read_bytes());assert raw==gzip.decompress((O/f'1_{c}.records.gz').read_bytes())
 rs=[raw[i:i+2112] for i in range(0,len(raw),2112)];hs=[struct.unpack_from('<16I',r) for r in rs]
 assert all(h[0]==0x52394c43 and h[1]==2400+c and h[5]==i and h[6:8]==(0x39,0xc5) for i,h in enumerate(hs))
 src=lambda r:r[64:1088];shadow=lambda r:r[1088:2112]
 if c==0:assert hs[-1][2:5]==(20,1,0) and src(rs[-1])[401]!=shadow(rs[-1])[401]
 if c==1:assert hs[-1][2:5]==(20,1,4)
 if c==2:
  r=rs[-1];assert hs[-1][2:5]==(90,0xbc,11)
  assert src(r)[129]==shadow(r)[129] and src(r)[386]!=shadow(r)[386]
 if c==3:assert hs[-1][2]==20 and src(rs[-1])[401]==shadow(rs[-1])[401]
print('PASS independent raw records: persistent request, coalescing, partial shadow on fault, changed flag lost')
