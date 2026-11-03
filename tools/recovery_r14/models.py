#!/usr/bin/env python3
"""Independent abstract admission model, bounded to two source generations.
Transitions are serialized assumptions, never native IRQ/watchdog evidence.
"""
from dataclasses import dataclass,replace
from collections import deque
import json
from pathlib import Path
@dataclass(frozen=True)
class S:
 phase:int=0
 source:tuple=(0,)*8
 scan:tuple=()
 page:int=0
 written:int=0
 pending:int=0
 critical:int=0
 complete:int=1
 closing:int=0
 suspect:int=0
 generation:int=0
 retained:int=0
 scan_generation:int=0

def successors(s):
 def add(name,**kw):return name,replace(s,**kw)
 if not s.closing:yield add('close',closing=1)
 if s.phase and not s.suspect:yield add('injected_independent_observer',suspect=1)
 if s.suspect:return
 if not s.pending:yield add('request_read',pending=1)
 if not s.closing and not s.critical:yield add('request_critical',critical=1)
 free=not s.closing and s.phase==0
 if free and not s.pending and not s.critical and s.generation<2:
  yield add('begin_draw',phase=1,complete=0,written=0,retained=1)
 if s.phase==1:
  if s.written<8:
   n=min(s.written+4,8);src=s.source[:s.written]+(s.generation+1,)*(n-s.written)+s.source[n:];yield add('draw_chunk',source=src,written=n)
  else:yield add('draw_done',phase=0,complete=1,generation=s.generation+1,retained=0)
 if free and s.pending and not s.critical and s.complete:yield add('begin_read',phase=2,pending=0,page=0,scan=(),scan_generation=s.generation)
 if s.phase==2:
  if s.page<8:yield add('native_comparison_completed',page=s.page+1,scan=s.scan+(s.source[s.page],))
  else:yield add('read_done',phase=0)
 if free and s.complete and not s.retained and s.generation<2:yield add('begin_critical',phase=4,critical=0,complete=0)
 if s.phase==4:
  yield add('native_operation_returned_complete',phase=0,source=(s.generation+1,)*8,generation=s.generation+1,complete=1,pending=1)

def explore():
 start=S();q=deque([start]);seen={start};edges=0;scans=0;closed_active=0
 while q:
  s=q.popleft()
  assert s.retained==(s.phase==1)
  if s.complete:assert len(set(s.source))==1
  if s.phase==2:assert s.complete and all(x==s.scan_generation for x in s.scan)
  if s.closing and s.phase:closed_active+=1
  for name,t in successors(s):
   edges+=1
   if name=='read_done':scans+=1;assert len(t.scan)==8 and len(set(t.scan))==1
   if s.suspect:assert t.phase==s.phase and t.retained==s.retained
   if s.closing:assert name not in ('begin_draw','begin_read','begin_critical')
   if t not in seen:seen.add(t);q.append(t)
 return dict(states=len(seen),transitions=edges,completed_scan_edges=scans,closing_with_active_authority_states=closed_active,max_generations=2,atomic_transitions_assumed=True)
def scheduling():
 # Runnable busy worker rank1; lower-priority monitor never gets selected.
 def chosen(rank):return min(((1,'worker'),(rank,'observer')))[1]
 assert all(chosen(6)=='worker' for _ in range(100))
 assert chosen(0)=='observer'
 return {'100_dispatches_rank6_observer':0,'rank0_observer_selected_under_model':True,'limits':'Initial strict priorities only; IRQ masking, dispatch inhibit, shared waits, real CPU time and scheduling setup not simulated'}
def main():
 r={'admission':explore(),'scheduling_counterexample':scheduling(),'counterexamples':{'copy_only':'publish A; read pages0..2; publish B; read3..7 -> mixed','unmediated_writer':'begin READ; three pages; direct native write; remaining pages -> mixed despite valid page counter','cooperative_timeout':'enter worker; never return; code after call never executes','false_stall':'No heartbeat change can be legitimate peripheral wait or starvation; suspicion is not proven fault','unsafe_unlock':'observer clears READ; writer reuses source; old worker resumes -> mixed/use-after-lifetime','admission_race':'two actors read IDLE before either stores owner -> both admitted unless metadata serialized'},'recovery_capabilities':{'detection':'Injected abstract observer only; no native independent authority proved','containment':'Cooperative refusal retains active owner and borrow','cancellation':False,'restoration':False}}
 p=Path(__file__).resolve().parents[2]/'reports/recovery_r14/models.json';p.write_text(json.dumps(r,indent=2)+'\n');print('PASS',json.dumps(r['admission'],sort_keys=True))
if __name__=='__main__':main()
