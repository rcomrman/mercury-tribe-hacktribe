#!/usr/bin/env python3
"""Bounded registration transaction: two relations/owners and two one-shot walkers.
No allocator or free. Negative 'retirement' states are model-only contract violations.
"""
import json
from collections import deque
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'reports/recovery_r19/model.json'
def explore(policy):
 # two constructor phases:0 idle,1 reserved,2 tuple,3 published/no inverse,
 # 4 inverse present but native frame live,5 actual return.
 # actors:0 idle,1 context-selected,2 method-resolved,3active,4returned,5released,6rejected,7fault.
 initial=(0,0,0,0,0,0,0,-1,0,-1);seen={initial:None};labels={};todo=deque([initial]);hazards={}
 while todo:
  s=todo.popleft();p=list(s[:2]);closed,retired,pub,inv=s[2:6];actors=[list(s[6:8]),list(s[8:10])];building=any(1<=x<=4 for x in p);frames=any(a[0] in (1,2,3,4,6) for a in actors);moves=[]
  def add(label,pp=p,cc=closed,rr=retired,ss=pub,ii=inv,aa=actors):moves.append((label,(*pp,cc,rr,ss,ii,*aa[0],*aa[1])))
  for i,x in enumerate(p):
   bit=1<<i
   if not closed&bit:add(f'close_{i}',cc=closed|bit)
   if x==0 and not closed&bit and not building and not frames:
    n=p.copy();n[i]=1;add(f'begin_{i}',pp=n)
   elif 1<=x<=4:
    n=p.copy();n[i]+=1;name=['','tuple','publish','inverse','actual_return'][x]
    if x==2:add(f'{"LATE_PUBLISH" if retired&bit else "publish"}_{i}',pp=n,ss=pub|bit)
    elif x==3:add(f'{"LATE_INVERSE" if retired&bit else "inverse"}_{i}',pp=n,ii=inv|bit)
    else:add(f'{name}_{i}',pp=n)
   permitted=False
   if closed&bit and not retired&bit:
    if policy=='guard_before_constructor':permitted=x==5 and not building and not frames
    elif policy=='inverse_empty_only':permitted=not inv&bit
    elif policy=='commit_at_inverse':permitted=x>=4 and not frames and not any(1<=z<=3 for z in p)
   if permitted:
    name='RETIRE_BEFORE_RETURN' if 1<=x<=4 else 'RETIRE_WITH_FRAME' if frames else 'physical_detach'
    add(f'{name}_{i}',rr=retired|bit,ss=pub&~bit,ii=inv&~bit)
  for who,(phase,target) in enumerate(actors):
   if phase==0:
    for i in range(2):
     if not pub&(1<<i):continue
     if policy=='guard_before_constructor' and (building or closed&(1<<i)):continue
     n=[a.copy() for a in actors];n[who]=[1,i];add(f'w{who}:select_{i}',aa=n)
   elif phase==1:
    n=[a.copy() for a in actors];n[who][0]=2 if pub&(1<<target) else 7;add(f'w{who}:resolve' if pub&(1<<target) else f'w{who}:TORN_TUPLE',aa=n)
   elif phase==2:
    n=[a.copy() for a in actors];ok=p[target]==5 and not closed&(1<<target);n[who][0]=3 if ok else 6;add(f'w{who}:invoke' if ok else f'w{who}:reject_uncommitted_or_closed',aa=n)
   elif phase in (3,4,6):
    n=[a.copy() for a in actors];n[who][0]=4 if phase==3 else 5;add(f'w{who}:return' if phase==3 else f'w{who}:release',aa=n)
  for label,n in moves:
   if any(k in label for k in ('RETIRE_BEFORE_RETURN','RETIRE_WITH_FRAME','LATE_PUBLISH','LATE_INVERSE','TORN_TUPLE')):
    kind=label.split('_0')[0].split('_1')[0] if not label.startswith('w') else 'TORN_TUPLE'
    if kind not in hazards:
     path=[label];a=s
     while seen[a] is not None:path.append(labels[a]);a=seen[a]
     hazards[kind]=list(reversed(path))
   if n not in seen:seen[n]=s;labels[n]=label;todo.append(n)
 return {'policy':policy,'states':len(seen),'hazards':hazards}
def main():
 rows=[explore(p) for p in ('guard_before_constructor','permanent_quarantine','inverse_empty_only','commit_at_inverse')]
 assert not rows[0]['hazards'] and not rows[1]['hazards'];assert 'LATE_INVERSE' in rows[2]['hazards'] and 'RETIRE_BEFORE_RETURN' in rows[3]['hazards']
 OUT.write_text(json.dumps({'bounds':{'relations':2,'owners':2,'walkers':2,'constructors_per_relation':1,'callbacks_per_walker':1},'assumptions':['Transitions externally serialized','Immutable anchors and static resource lifetime','Known scope only; no hardware cessation','Native constructor return is distinct from inverse publication'],'results':rows},indent=2)+'\n')
 print('PASS transaction model:',[(r['policy'],r['states'],list(r['hazards'])) for r in rows])
if __name__=='__main__':main()
