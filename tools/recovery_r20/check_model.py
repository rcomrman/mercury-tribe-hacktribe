#!/usr/bin/env python3
"""Independent action interpreter and exhaustive reachability; no model import."""
from collections import deque
INITIAL=((0,0),0,0,0,(0,0),((0,-1),(0,-1)))
ACTIONS=[f'{event}:{i}' for i in range(2) for event in ('close','begin','tuple','publish','inverse','actual_return','admit_destructor','detach','body_return','CLAIM_FREE')]
ACTIONS += [f'w{w}:{event}' for w in range(2) for event in ('select:0','select:1','resolve','TORN','invoke_native','reject','callback_return','release_frame')]
def step(state,action,policy):
 b,c,s,inv,dt,ws=state;b=list(b);dt=list(dt);ws=list(ws)
 held=lambda w:w[0] in (1,2,3,4,6)
 try:
  parts=action.split(':')
  if parts[0].startswith('w'):
   who=int(parts[0][1:]);event=parts[1];phase,target=ws[who]
   if event=='select':
    i=int(parts[2]);assert phase==0 and s&(1<<i)
    if not(policy=='partial_domain' and who==1):assert b[i]==5 and not c&(1<<i) and all(x not in (1,2,3,4) for x in b) and all(x not in (1,2) for x in dt)
    ws[who]=(1,i)
   elif event=='resolve':assert phase==1 and s&(1<<target);ws[who]=(2,target)
   elif event=='TORN':assert phase==1 and not s&(1<<target);ws[who]=(7,target)
   elif event=='invoke_native':assert phase==2 and not(policy=='quarantine' and c&(1<<target));ws[who]=(3,target)
   elif event=='reject':assert phase==2 and policy=='quarantine' and c&(1<<target);ws[who]=(6,target)
   elif event=='callback_return':assert phase==3;ws[who]=(4,target)
   elif event=='release_frame':assert phase in (4,6);ws[who]=(5,target)
   else:raise AssertionError(action)
  else:
   event,i=parts;i=int(i);mask=1<<i
   if event=='close':assert not c&mask;c|=mask
   elif event=='begin':
    assert b[i]==0 and not c&mask and not any(x in (1,2,3,4) for x in b) and not any(held(w) for w in ws) and not any(x in (1,2) for x in dt);b[i]=1
   elif event=='tuple':assert b[i]==1;b[i]=2
   elif event=='publish':assert b[i]==2;b[i]=3;s|=mask
   elif event=='inverse':assert b[i]==3;b[i]=4;inv|=mask
   elif event=='actual_return':assert b[i]==4;b[i]=5
   elif event=='admit_destructor':
    assert policy!='quarantine' and c&mask and b[i]==5 and dt[i]==0 and not any(x in (1,2) for x in dt)
    if policy=='mediated':assert not any(held(w) for w in ws) and not any(x in (1,2,3,4) for x in b)
    elif policy=='partial_domain':assert not held(ws[0]) and not any(x in (1,2,3,4) for x in b)
    else:assert not any(w[0]==3 for w in ws)
    dt[i]=1
   elif event=='detach':assert dt[i]==1;dt[i]=2;s&=~mask;inv&=~mask
   elif event=='body_return':assert dt[i]==2;dt[i]=3
   elif event=='CLAIM_FREE':assert policy=='return_certificate' and dt[i]==3;dt[i]=4
   else:raise AssertionError(action)
 except AssertionError:return None
 return (tuple(b),c,s,inv,tuple(dt),tuple(ws))
def violations(state):
 b,c,s,inv,dt,ws=state;found=set()
 for phase,target in ws:
  if phase==7:found.add('torn_tuple')
  if phase==3 and dt[target]>=3:found.add('native_access_after_destructor_return')
 for i in range(2):
  if dt[i]==4 and any(target==i and phase in (1,2,3,4,6) for phase,target in ws):found.add('free_claim_with_reference')
  if dt[i] and b[i] in (1,2,3,4):found.add('destructor_before_constructor_return')
 return found
def check(result):
 policy=result['policy'];seen={INITIAL};queue=deque([INITIAL]);edges=0;hazards=set()
 while queue:
  s=queue.popleft()
  for action in ACTIONS:
   nxt=step(s,action,policy)
   if nxt is None:continue
   edges+=1;hazards|=violations(nxt)
   if nxt not in seen:seen.add(nxt);queue.append(nxt)
 assert len(seen)==result['states'] and edges==result['edges'],(policy,len(seen),edges)
 assert hazards==set(result['hazards']),(policy,hazards)
 for hazard,path in result['hazards'].items():
  s=INITIAL
  for label in path:
   s=step(s,label,policy);assert s is not None,(policy,label)
  assert hazard in violations(s)
 return len(seen)
