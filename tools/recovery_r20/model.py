#!/usr/bin/env python3
"""Finite lifetime model. Reclamation is a claim only; no native free exists here."""
from collections import deque
from pathlib import Path
import json
OUT=Path(__file__).resolve().parents[2]/'reports/recovery_r20/model.json'
POLICIES=('mediated','quarantine','active_only','partial_domain','return_certificate')
# State: construction phases, closed mask, slot mask, inverse mask,
# destructor phases, two walkers (phase,target). 1=selected,2=resolved,
# 3=callback,4=returned-but-frame-retained,5=released,6=rejected,7=torn.
INITIAL=((0,0),0,0,0,(0,0),((0,-1),(0,-1)))
def edges(s,policy):
 b,closed,slots,inverse,dt,walkers=s
 def state(B=b,C=closed,S=slots,I=inverse,D=dt,W=walkers):return (B,C,S,I,D,W)
 def put(seq,i,x):return seq[:i]+(x,)+seq[i+1:]
 live=lambda w:w[0] in (1,2,3,4,6)
 for i in range(2):
  bit=1<<i
  if not closed&bit:yield f'close:{i}',state(C=closed|bit)
  if b[i]==0 and not closed&bit and not any(1<=x<=4 for x in b) and not any(live(w) for w in walkers) and not any(1<=x<=2 for x in dt):
   yield f'begin:{i}',state(B=put(b,i,1))
  if 1<=b[i]<=4:
   label={1:'tuple',2:'publish',3:'inverse',4:'actual_return'}[b[i]]
   yield f'{label}:{i}',state(B=put(b,i,b[i]+1),S=slots|bit if b[i]==2 else slots,I=inverse|bit if b[i]==3 else inverse)
  if policy!='quarantine' and closed&bit and b[i]==5 and dt[i]==0:
   if policy=='mediated':ok=not any(live(w) for w in walkers) and not any(1<=x<=4 for x in b) and not any(1<=x<=2 for x in dt)
   elif policy=='partial_domain':ok=not live(walkers[0]) and not any(1<=x<=4 for x in b) and not any(1<=x<=2 for x in dt)
   else:ok=not any(w[0]==3 for w in walkers) and not any(1<=x<=2 for x in dt)
   if ok:yield f'admit_destructor:{i}',state(D=put(dt,i,1))
  if dt[i]==1:yield f'detach:{i}',state(D=put(dt,i,2),S=slots&~bit,I=inverse&~bit)
  if dt[i]==2:yield f'body_return:{i}',state(D=put(dt,i,3))
  if dt[i]==3 and policy=='return_certificate':yield f'CLAIM_FREE:{i}',state(D=put(dt,i,4))
 for w,(phase,target) in enumerate(walkers):
  if phase==0:
   for i in range(2):
    # partial_domain has one unmediated caller; all other policies close admissions.
    raw=policy=='partial_domain' and w==1
    if slots&(1<<i) and (raw or (b[i]==5 and not closed&(1<<i) and not any(1<=x<=4 for x in b) and not any(1<=x<=2 for x in dt))):
     yield f'w{w}:select:{i}',state(W=put(walkers,w,(1,i)))
  elif phase==1:
   label='resolve' if slots&(1<<target) else 'TORN'
   yield f'w{w}:{label}',state(W=put(walkers,w,(2 if label=='resolve' else 7,target)))
  elif phase==2:
   # Real C0085078 has no close gate. Thunk quarantine can reject.
   reject=policy=='quarantine' and closed&(1<<target)
   yield f'w{w}:{"reject" if reject else "invoke_native"}',state(W=put(walkers,w,(6 if reject else 3,target)))
  elif phase==3:yield f'w{w}:callback_return',state(W=put(walkers,w,(4,target)))
  elif phase in (4,6):yield f'w{w}:release_frame',state(W=put(walkers,w,(5,target)))
def hazards(s):
 b,closed,slots,inverse,dt,walkers=s;h=[]
 if any(w[0]==7 for w in walkers):h.append('torn_tuple')
 if any(w[0]==3 and dt[w[1]]>=3 for w in walkers):h.append('native_access_after_destructor_return')
 if any(dt[i]==4 and any(w[1]==i and w[0] in (1,2,3,4,6) for w in walkers) for i in range(2)):h.append('free_claim_with_reference')
 if any(dt[i]>=1 and 1<=b[i]<=4 for i in range(2)):h.append('destructor_before_constructor_return')
 return h
def explore(policy):
 parents={INITIAL:None};q=deque([INITIAL]);found={};edges_count=0
 while q:
  s=q.popleft()
  for label,n in edges(s,policy):
   edges_count+=1
   if n not in parents:parents[n]=(s,label);q.append(n)
   for hazard in hazards(n):
    if hazard not in found:
     path=[];p=n
     while parents[p] is not None:p,l=parents[p];path.append(l)
     found[hazard]=list(reversed(path))
 return dict(policy=policy,states=len(parents),edges=edges_count,hazards=found)
def main():
 results=[explore(p) for p in POLICIES]
 OUT.write_text(json.dumps(dict(bounds={'owners':2,'walkers':2,'one_construction_per_subject':True,'no_reuse':True},assumptions=['Externally atomic transitions','Complete coverage only for mediated/quarantine','Native callback ignores logical closure','CLAIM_FREE is symbolic only; no physical reclamation'],results=results),indent=2)+'\n')
 for r in results:print(r['policy'],r['states'],r['edges'],list(r['hazards']))
 assert not results[0]['hazards'] and not results[1]['hazards']
 assert all(r['hazards'] for r in results[2:])
if __name__=='__main__':main()
