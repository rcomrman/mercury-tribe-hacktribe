#!/usr/bin/env python3
"""Bounded closed-world reference/owned-command model, not native concurrency."""
from dataclasses import dataclass,replace
from collections import deque
from pathlib import Path
import json
@dataclass(frozen=True)
class S:
 generation:int=1
 retiring:int=0
 producer:int=1
 serial:int=0
 leases:tuple=() # (serial, generation, holder, kind), individual records
 active:int=0
 stalled:int=0
 command:int=0 #0 none,1 owned/pending,2 entered,3 returned,4 acked
 queue_token:int=0
 copied:int=0
 input_value:int=42
 effect:int=0
 binding_changed:int=0

def successors(s):
 def add(n,**kw):return n,replace(s,**kw)
 if not s.retiring:yield add('retire_stops_external_admission',retiring=1)
 if s.producer:yield add('detach_known_producer',producer=0)
 if not s.binding_changed:yield add('page_root_changes',binding_changed=1)
 if s.input_value==42:yield add('caller_mutates_input',input_value=7)
 # One owned command, scalar captured by value and target retained individually.
 if not s.command and not s.retiring and s.producer and s.serial<4:
  t=s.serial+1
  yield add('capture_owned_byte_and_lease',command=1,copied=s.input_value,queue_token=t,serial=t,leases=s.leases+((t,s.generation,10,1),))
 # Optional independent wrapper lease; release only when not a callback.
 if not s.retiring and s.producer and len(s.leases)<2 and s.serial<4 and not any(t[3]==2 for t in s.leases):
  t=s.serial+1;yield add('external_wrapper_reference',serial=t,leases=s.leases+((t,s.generation,20,2),))
 for t in s.leases:
  if t[3]==2:yield add('owner_releases_wrapper',leases=tuple(x for x in s.leases if x!=t))
 if s.command==1 and len(s.leases)<2 and s.serial<4:
  assert any(t[0]==s.queue_token for t in s.leases)
  t=s.serial+1
  yield add('derive_callback_from_held_command',command=2,serial=t,active=t,leases=s.leases+((t,s.generation,42,4),))
 if s.command==2 and not s.stalled:
  yield add('timeout_retains_callback',stalled=1)
  yield add('real_native_return_and_callback_release',command=3,active=0,effect=s.copied,leases=tuple(t for t in s.leases if t[0]!=s.active))
 if s.command==3:
  yield add('reply_ack_releases_command_target',command=4,queue_token=0,leases=tuple(t for t in s.leases if t[0]!=s.queue_token))
 if s.retiring and not s.producer and not s.leases and s.generation<2:
  yield add('metadata_only_cpu_fixture_rebind',generation=s.generation+1,retiring=0,producer=1)

def explore():
 start=S();seen={start};q=deque([start]);edges=quiet=stalled=0
 while q:
  s=q.popleft();assert len(s.leases)<=2 and len({t[0] for t in s.leases})==len(s.leases)
  assert all(t[1]==s.generation for t in s.leases)
  if s.command in (1,2,3):assert any(t[0]==s.queue_token and t[3]==1 for t in s.leases)
  if s.command==2:assert any(t[0]==s.active and t[3]==4 for t in s.leases)
  if s.command in (3,4):assert s.effect==s.copied
  if s.stalled:assert s.command==2 and s.active and s.leases;stalled+=1
  if s.retiring and not s.producer and not s.leases:quiet+=1;assert s.command not in (1,2,3)
  for name,t in successors(s):
   edges+=1
   if s.retiring:assert name not in ('capture_owned_byte_and_lease','external_wrapper_reference')
   if name=='metadata_only_cpu_fixture_rebind':assert not s.leases and not s.active
   if s.stalled:assert t.active==s.active and any(x[0]==s.active for x in t.leases)
   if t not in seen:seen.add(t);q.append(t)
 return {'states':len(seen),'transitions':edges,'locally_quiet_states':quiet,'stalled_with_callback_retained_states':stalled,'max_generations':2,'max_serial':4,'lease_capacity':2,'closed_world_and_atomic_transitions_assumed':True}
def main():
 r={'registry_commands':explore(),'scope':'Finite known producers/leases, exact owner tokens, truthful release and serialized operations assumed. Not global/native CPU or device cessation.','counterexamples':{'distinct_key_and_this':'registered key and callback this are independent pointers; retaining the key alone omits callback context', 'hidden_alias':'retire+detach+release all known leases -> local quiet; omitted raw wrapper/native subject still calls target','premature_release':'caller releases callback lease before CPU return -> ledger can lie; legal release order is a precondition','native_reverse_edge':'subject removal clears its slot but observer vector can still contain subject pointers','reentry':'inner callback release leaves outer callback token live','aba':'same address reused with new generation/serial; old token rejected, raw pointer can still alias new object','native_sync_deferral':'owned byte preserves value, but delayed descriptor update changes synchronous observations','device':'all known CPU refs released does not provide SPI/DMA drain or safe LCD destruction'},'global_cpu_cessation_proven':False,'peripheral_cessation_authority_proven':False,'native_cancellation_proven':False}
 out=Path(__file__).resolve().parents[2]/'reports/recovery_r16';(out/'models.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',json.dumps(r['registry_commands'],sort_keys=True))
if __name__=='__main__':main()
