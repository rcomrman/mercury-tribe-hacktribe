#!/usr/bin/env python3
"""Finite schedules: two storage slots, two owners, two one-shot callbacks.
Selected references exist BEFORE admission. Bad reclamation policies are model-only.
"""
import json
from collections import deque
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'reports/recovery_r18/model.json'
def explore(policy):
 # slots: (generation, owners). gen=0 unused, -1 model-only destroyed.
 # actors: (phase,index,selected_generation,owner), phase 0idle 1selected
 # 2resolved 3active 4returned 5done 6rejected. Clock may expire once.
 initial=(0,0,((0,0),(0,0)),((0,-1,0,0),(0,-1,0,0)))
 queue=deque([initial]);seen={initial:None};parent={};hazards={};max_used=0
 while queue:
  state=queue.popleft();made,expired,slots,actors=state;max_used=max(max_used,sum(g!=0 for g,o in slots));moves=[]
  if made<2:
   for i,(g,o) in enumerate(slots):
    if g==0:
     n=list(slots);n[i]=(made+1,3);moves.append(('allocate_fresh',(made+1,expired,tuple(n),actors)));break
  if not expired:moves.append(('clock_expires',(made,1,slots,actors)))
  for i,(g,o) in enumerate(slots):
   if g<=0:continue
   for bit in (1,2):
    if o&bit:
     n=list(slots);n[i]=(g,o&~bit);moves.append((f'retire_{i}_owner_{bit}',(made,expired,tuple(n),actors)))
   active=any(a[0]==3 and a[1]==i for a in actors)
   if policy=='reuse_on_zero_active' and o==0 and not active and made<3:
    n=list(slots);n[i]=(made+1,3);moves.append((f'reuse_{i}_despite_possible_selection',(made+1,expired,tuple(n),actors)))
   if policy=='timeout_destroy' and expired and o==0 and not active:
    n=list(slots);n[i]=(-1,0);moves.append((f'destroy_{i}_on_timeout',(made,expired,tuple(n),actors)))
  for who,a in enumerate(actors):
   phase,i,gen,owner=a
   choices=[]
   if phase==0:
    for j,(g,o) in enumerate(slots):
     if g>0:
      for bit in (1,2):choices.append((f'select_{j}_{bit}',(1,j,g,bit)))
   elif phase==1:choices.append(('resolve',(2,i,gen,owner)))
   elif phase==2:
    g,o=slots[i]
    if g<0:choices.append(('UAF_model_only',(6,i,gen,owner)))
    elif g!=gen:choices.append(('ABA_generation_reroute',(6,i,gen,owner)))
    elif not o&owner:choices.append(('reject_closed',(6,i,gen,owner)))
    else:choices.append(('invoke_with_borrow',(3,i,gen,owner)))
   elif phase==3:choices.append(('return',(4,i,gen,owner)))
   elif phase==4:choices.append(('release',(5,i,gen,owner)))
   for label,new in choices:
    n=list(actors);n[who]=new;moves.append((f'actor{who}:{label}',(made,expired,slots,tuple(n))))
  for label,new in moves:
   if 'UAF' in label or 'ABA' in label:
    kind='UAF' if 'UAF' in label else 'ABA'
    if kind not in hazards:
     path=[label];s=state
     while seen[s] is not None:
      prev=seen[s];path.append(parent[s]);s=prev
     hazards[kind]=list(reversed(path))
   if new not in seen:seen[new]=state;parent[new]=label;queue.append(new)
 return {'policy':policy,'states':len(seen),'max_storage_slots':max_used,'hazards':hazards}
def main():
 rows=[explore(p) for p in ('monotonic_keep','reuse_on_zero_active','timeout_destroy')]
 assert not rows[0]['hazards'] and rows[0]['max_storage_slots']==2
 assert 'ABA' in rows[1]['hazards'] and 'UAF' in rows[2]['hazards']
 OUT.write_text(json.dumps({'bounds':{'storage_slots':2,'owners_per_slot':2,'actors':2,'allocations':3,'clock_expirations':1},'assumptions':['Atomic externally serialized transitions','Immutable anchors/payloads only for monotonic_keep','No native slot mutation during resolver','No peripheral cessation claim'],'results':rows},indent=2)+'\n')
 print('PASS model:',[(r['policy'],r['states'],r['hazards'].keys()) for r in rows])
if __name__=='__main__':main()
