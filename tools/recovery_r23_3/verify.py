#!/usr/bin/env python3
import gzip,json
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'reports/recovery_r23_3'
j=json.loads((O/'results.json').read_text())['cases'];assert len(j)==10
for v in range(2):
 rows=[r for r in j if r['vsb']==v];assert [r['case'] for r in rows]==list(range(5))
 for r in rows:
  c=r['case'];t=gzip.decompress((O/f'{v}_{c}.trace.gz').read_bytes()).decode();assert '0xc00117c8:' in t
  if c in (2,3):assert '0xc0015cdc:' in t
  if c==4:assert '0xc001851c:' in t and '0xc001862c:' in t and r['records'][-2:]==[[0x52323333,4,2,1],[0x52323333,4,3,0x00fe007f]]
  assert r['exit']==('host_timeout' if c==2 else 0)
assert [r['records'] for r in j[:5]]==[r['records'] for r in j[5:]]
print('PASS independent trace/record checks; timeout is host termination, not LCD failure')
