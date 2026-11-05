#!/usr/bin/env python3
"""Replays R22 abstract operations and runs explicitly synthetic LCD schedules."""
import json,itertools,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from model import State
ROOT=Path(__file__).resolve().parents[2]

def replay(bits):
 before,inflight,changes,mercury,restore,fault=bits
 s=State(framebuffer=1,shadow=int(bool(before)),lcd=int(bool(before)))
 trace=[]
 if inflight:s.lcd=0;trace.append('inflight_may_complete_old')
 if changes:s.event('compare');trace.append('compare_copy')
 if mercury:s.lcd=0;trace.append('mercury_changes_lcd')
 if restore and not fault:s.shadow=s.lcd=1;trace.append('assumed_forced_restore')
 return s,trace

def brutal(kind,kperiod,duration,order,delay):
 # Discrete 10 ms ticks. Delays and completion ordering are synthetic.
 s=State(owner='M',mode='MERCURY_ACTIVE');queue=[];collisions=ignored=0;seq=0
 for t in range(duration):
  due=[x for x in queue if x[0]==t];queue=[x for x in queue if x[0]!=t]
  if order=='late':due.reverse()
  for _,token in due:s.event('complete',token)
  if t%kperiod==0:
   s.event('korg_frame',value=1000+t).event('compare')
   if kind=='ignore':ignored+=1
   else:
    collisions+=bool(s.pending);seq+=1;s.event('begin_korg',seq,s.framebuffer);queue.append((t+delay,seq))
  if t%10==0:
   collisions+=bool(s.pending);seq+=1;s.event('begin_mercury',seq,2000+t);queue.append((t+delay,seq))
 # Brutal EXIT: ownership changes without drain or restoration.
 s.event('exit');s.owner='K';s.mode='KORG_ACTIVE'
 for _,token in sorted(queue,reverse=(order=='late')):s.event('complete',token)
 frozen=s.shadow==s.framebuffer and s.lcd!=s.framebuffer
 return dict(kind=kind,korg_period_ticks=kperiod,duration_ticks=duration,order=order,transfer_delay_ticks=delay,collisions=collisions,ignored=ignored,violations=len(s.violations),shadow_equals_framebuffer=s.shadow==s.framebuffer,lcd_equals_framebuffer=s.lcd==s.framebuffer,exit_frozen=frozen)

def main():
 rows=json.loads((ROOT/'reports/recovery_r22/model.json').read_text())['states'];replayed=[]
 for row in rows:
  s,trace=replay(row['inputs']);stale=s.shadow==s.framebuffer and s.lcd!=s.framebuffer and bool(row['inputs'][2])
  assert stale==row['stale_ack'],row
  if stale:replayed.append(dict(inputs=row['inputs'],trace=trace,shadow=s.shadow,lcd=s.lcd))
 assert len(replayed)==21
 results=[brutal(kind,p,d,o,delay) for kind,p,d,o,delay in itertools.product(('priority','ignore'),(5,10,17),(100,1000),('early','late'),(1,2,11))]
 out=ROOT/'reports/recovery_r23_1';out.mkdir(parents=True,exist_ok=True)
 (out/'experiments.json').write_text(json.dumps({'r22_replayed':replayed,'brutal':results},indent=2)+'\n')
 print('PASS replayed 64 R22 abstractions, including 21 stale-shadow witnesses; 72 synthetic brutal schedules')
if __name__=='__main__':main()
