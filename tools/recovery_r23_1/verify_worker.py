#!/usr/bin/env python3
"""Independent checks over raw ARM records; does not execute the fixture."""
import gzip,struct
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'reports/recovery_r23_1'
for c in range(6):
 a=gzip.decompress((O/f'worker-0-{c}.gz').read_bytes());b=gzip.decompress((O/f'worker-1-{c}.gz').read_bytes());assert a==b
 records=[a[i:i+2112] for i in range(0,len(a),2112)];heads=[struct.unpack_from('<16I',r) for r in records]
 assert all(h[0]==0x52394c43 and h[1]==2300+c and h[5]==i and h[6:8]==(0x39,0xc5) for i,h in enumerate(heads))
 first,last=records[0],records[-1];src=lambda r:r[64:1088];shadow=lambda r:r[1088:2112]
 if c==0:assert src(last)==shadow(last) and heads[-1][2]==20
 if c in (1,5):assert src(last)[401]!=shadow(last)[401] and heads[-1][2]==20
 if c==2:
  assert src(first)==shadow(first) and src(last)==shadow(last) and src(last)[401]!=src(first)[401] and heads[-1][2]==20
 if c==3:assert src(last)[401]==shadow(last)[401] and src(last)[401]!=src(first)[401] and heads[-1][2:5]==(90,0xbc,11)
 if c==4:assert heads[-1][2:5]==(90,0xbc,11)
print('PASS independent raw records: source/shadow checks, expected faults and 6 cross-VSB pairs')
