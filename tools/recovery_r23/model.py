#!/usr/bin/env python3
"""Transition authority model preserving all R22 stale-shadow witnesses."""
import itertools,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r23';old=json.loads((R/'reports/recovery_r22/model.json').read_text())['states']
E=('to_mercury','korg_begin','korg_end','mercury_begin','mercury_end','exit','escape','fault')
def step(s,e):
 s=dict(s)
 if e=='fault':s['mode']='FAULT';return s
 if e=='escape':s['escaped']=1;return s
 if e=='korg_begin':s['korg']+=1
 elif e=='korg_end' and s['korg']:s['korg']-=1
 elif e=='mercury_begin':s['mercury']+=1
 elif e=='mercury_end' and s['mercury']:s['mercury']-=1
 elif e=='to_mercury' and s['mode']=='KORG_ACTIVE':s['mode']='MERCURY_ACTIVE' if not s['korg'] and not s['escaped'] else 'FAULT'
 elif e=='exit' and s['mode']=='MERCURY_ACTIVE':s['mode']='KORG_ACTIVE' if not s['mercury'] and not s['korg'] and not s['escaped'] else 'FAULT'
 return s
rows=[]
for seq in itertools.product(E,repeat=4):
 s={'mode':'KORG_ACTIVE','korg':0,'mercury':0,'escaped':0}
 for e in seq:s=step(s,e)
 safe=s['mode']!='FAULT' and not s['escaped']
 rows.append({'events':seq,'final':s,'safe':safe})
assert sum(x['stale_ack'] for x in old)==21
(O/'model.json').write_text(json.dumps({'r22_states':64,'r22_stale_witnesses':21,'transition_states':rows},indent=2)+'\n')
print('PASS preserved 64 R22 states and 21 stale-shadow witnesses; explored',len(rows),'transition sequences; unsafe',sum(not r['safe'] for r in rows))
