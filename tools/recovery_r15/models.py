#!/usr/bin/env python3
"""Independent bounded command conservation spec: 3 requests, capacity2.
Serialized transitions, owned scalar payloads and a generation registry assumed.
"""
from dataclasses import dataclass,replace
from collections import deque
from pathlib import Path
import json
@dataclass(frozen=True)
class S:
 status:tuple=(0,0,0) #0 unseen,1 waiting,2 run,3 done,4 stale,5 submit refused,6 done ack,7 stale ack
 gen:tuple=(0,0,0)
 queue:tuple=()
 issued:int=0
 generation:int=1
 occupied:int=0
 closing:int=0
 stop:int=0
 stalled:int=0
 executed:tuple=()
def successors(s):
 def changed(i,v):return s.status[:i]+(v,)+s.status[i+1:]
 if not s.closing:yield 'close',replace(s,closing=1)
 if not s.stop:yield 'stop_request',replace(s,stop=1)
 if s.generation==1:yield 'page_transition',replace(s,generation=2)
 if 2 not in s.status:yield 'external_domain_toggle',replace(s,occupied=1-s.occupied)
 if s.issued<3:
  i=s.issued
  if s.closing or len(s.queue)==2:yield 'submit_refused',replace(s,issued=i+1,status=changed(i,5))
  else:yield 'submit_owned_scalars',replace(s,issued=i+1,status=changed(i,1),gen=s.gen[:i]+(s.generation,)+s.gen[i+1:],queue=s.queue+(i,))
 if not s.queue:return
 i=s.queue[0];st=s.status[i]
 if st==1 and s.gen[i]!=s.generation:yield 'stale_refusal_retained',replace(s,status=changed(i,4))
 elif st==1 and not s.occupied and not s.stalled:yield 'native_entry',replace(s,status=changed(i,2),executed=s.executed+(i,))
 if st==2:
  if not s.stalled:
   yield 'timeout_retains_authority',replace(s,stalled=1)
   yield 'actual_native_return',replace(s,status=changed(i,3))
 if st in (3,4):yield 'receiver_ack',replace(s,status=changed(i,6 if st==3 else 7),queue=s.queue[1:])
def explore():
 first=S();q=deque([first]);seen={first};edges=returns=retained=0
 while q:
  s=q.popleft();assert len(set(s.executed))==len(s.executed)
  assert sum(st==2 for st in s.status)<=1
  assert set(s.queue)=={i for i,st in enumerate(s.status) if st in (1,2,3,4)}
  accepted={i for i,st in enumerate(s.status) if st not in (0,5)}
  assert accepted==set(s.queue)|{i for i,st in enumerate(s.status) if st in (6,7)}
  assert all(s.status[i] in (2,3,6) for i in s.executed)
  if s.stalled and 2 in s.status:retained+=1
  for name,t in successors(s):
   edges+=1
   if name=='actual_native_return':returns+=1
   if name=='receiver_ack':assert s.status[s.queue[0]] in (3,4)
   if s.stalled and 2 in s.status:assert 2 in t.status and t.queue[0]==s.queue[0]
   if t not in seen:seen.add(t);q.append(t)
 return {'states':len(seen),'transitions':edges,'actual_return_edges':returns,'stalled_with_retained_command_states':retained,'max_commands':3,'capacity':2,'atomic_transitions_assumed':True}
def main():
 r={'conservation':explore(),'cancellation_demonstrated':False,'native_sync_compatibility':False,'counterexamples':{'shallow_copy':'copy pointer word; pointee changes/dies before dispatch -> original argument not retained','ui_boundary':'queue callback wrapper; change wrapper.manager; native invocation resolves new manager','terminal_reply_loss':'recycle DONE slot before acknowledgement -> old result overwritten; final model retains until ACK','reentry':'outer depth1 -> inner depth2 -> inner returns depth1: cannot release outer resources','stop_flag':'request stop; current callback writes source after request','task_state':'wakeup/timeout changes metadata but selected task not executed; CPU access authority remains','hardware':'callback returns; peripheral may still own descriptor/buffer: callback return alone cannot free','sync_deferral':'caller expects result/output before returning; WAIT value cannot substitute native ABI result','ordered_transition':'transition command cannot overtake earlier accepted work without explicit stale-generation policy','deadlock':'synchronous caller waits while holding DRAW; queued CRITICAL needs IDLE -> cycle'},'limits':['Known scalar codec only; target registry and metadata serialization assumed','No native watchdog, cancellation, global CPU cessation or peripheral/DMA drain proven','No runtime command drop/reorder to hide native errors']}
 out=Path(__file__).resolve().parents[2]/'reports/recovery_r15';(out/'models.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',json.dumps(r['conservation'],sort_keys=True))
if __name__=='__main__':main()
