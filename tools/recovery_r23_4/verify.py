#!/usr/bin/env python3
"""Independently interpret saved forced-comparator records."""
import gzip,struct
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'reports/recovery_r23_4'
for c in range(2):
 a=gzip.decompress((O/f'0_{c}.records.gz').read_bytes());b=gzip.decompress((O/f'1_{c}.records.gz').read_bytes());assert a==b and len(a)==21120
 for i in range(10):
  record=a[i*2112:(i+1)*2112];h=struct.unpack_from('<16I',record)
  assert h[:2]==(0x52394c43,2500+c) and h[5]==i and h[6:8]==(0x39,0xc5)
  assert record[64:1088]==record[1088:2112]
  if 1<=i<=8:assert h[2:5]==(9+i,c,i-1)
 for v in range(2):
  trace=gzip.decompress((O/f'{v}_{c}.trace.gz').read_bytes()).decode()
  assert '0xc0015ab4:' in trace and '0xc001613c:' not in trace
print('PASS independent eight-page force/no-force records, two VSB; no sender executed')
