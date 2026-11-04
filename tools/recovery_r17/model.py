#!/usr/bin/env python3
"""Exhaustive finite schedules: two one-shot walkers, one close, optional queued borrow.
No scheduler, lock implementation, peripheral or hidden-alias assumption is proved.
"""
import json
from collections import deque
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'reports/recovery_r17/model.json'
def explore(policy,queued):
 # closed,entry,queue,walker0,walker1. 0 idle,1 selected,2 context loaded,
 # 3 resolved,4 invoking,5 returned,6 released/skipped,7 torn/faulted.
 initial=(0,1,queued,0,0);todo=deque([initial]);paths={initial:[]};hazards={};terminal=0
 while todo:
  s=todo.popleft();closed,entry,q,*p=s
  if closed and not q and all(x in (0,6,7) for x in p):terminal+=1
  moves=[]
  if not closed:
   keep=policy=='guarded' and any(1<=x<=5 for x in p) or policy=='active_only' and any(x==4 for x in p)
   moves.append(('request_close',(1,int(keep),q,*p)))
  if closed and entry and not any(1<=x<=5 for x in p):moves.append(('withdraw_after_return',(closed,0,q,*p)))
  if q:moves.append(('refuse_pending_then_ack',(closed,entry,0,*p)))
  for i,x in enumerate(p):
   n=list(p);label=None
   if x==0 and not closed:n[i]=1;label='select_admitted'
   elif x==1:n[i]=2 if entry else 6;label='load_key_context' if entry else 'skip_removed'
   elif x==2:n[i]=3 if entry else 7;label='resolve' if entry else 'TORN_tuple'
   elif x==3:n[i]=4;label='invoke' if entry else 'invoke_cached_after_withdraw'
   elif x==4:n[i]=5;label='return'
   elif x==5:n[i]=6;label='release_frame'
   if label:moves.append((f'w{i}:{label}',(closed,entry,q,*n)))
  for label,t in moves:
   path=paths[s]+[label]
   if 'TORN' in label:hazards.setdefault('torn_tuple',path)
   if 'invoke_cached' in label:hazards.setdefault('cached_callback_after_withdraw',path)
   if t not in paths:paths[t]=path;todo.append(t)
 return dict(policy=policy,queued=queued,states=len(paths),terminals=terminal,hazards=hazards)
def main():
 rows=[explore(p,q) for p in ('guarded','raw','active_only') for q in (0,1)]
 for r in rows:
  assert not r['hazards'] if r['policy']=='guarded' else set(r['hazards'])=={'torn_tuple','cached_callback_after_withdraw'}
 OUT.write_text(json.dumps({'bounds':{'walkers':2,'close_requests':1,'queued_borrows_max':1,'walks_per_walker':1},'assumptions':['All selections admitted before native loads','Atomic model transitions require an external gate','No hidden alias, native bypass, IRQ or peripheral'],'results':rows},indent=2)+'\n')
 print('PASS finite model:',sum(r['states'] for r in rows),'states; guarded invariants and raw/active-only counterexamples')
if __name__=='__main__':main()
