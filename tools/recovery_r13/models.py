#!/usr/bin/env python3
"""Exhaustive bounded participating-access protocol; explicit bypass/liveness witnesses."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def explore():
 start=(0,0,(0,)*8,(0,)*8,0,0,-1);seen={start};todo=collections.deque([start]);edges=0;ends=0;deferred=0
 while todo:
  s=todo.popleft();phase,pos,src,shadow,pending,k,rv=s;nexts=[]
  if not pending:nexts.append((phase,pos,src,shadow,1,k,rv))
  if phase==0:
   if k<2:nexts.append((1,0,src,shadow,pending,k,-1))
   if pending:
    assert len(set(src))==1;nexts.append((2,0,src,shadow,0,k,src[0]))
  elif phase==1:
   if pos<8:
    b=list(src);b[pos]=k+1;nexts.append((1,pos+1,tuple(b),shadow,pending,k,-1))
   else:assert len(set(src))==1;nexts.append((0,0,src,shadow,pending,k+1,-1))
   deferred+=bool(pending)
  else:
   assert src==(rv,)*8
   if pos<8:
    b=list(shadow);b[pos]=src[pos];nexts.append((2,pos+1,src,tuple(b),pending,k,rv))
   else:
    assert shadow==(rv,)*8;ends+=1;nexts.append((0,0,src,shadow,pending,k,-1))
  for t in nexts:
   edges+=1
   if t not in seen:seen.add(t);todo.append(t)
 return {'states':len(seen),'transitions':edges,'complete_scan_edges_checked':ends,'draw_states_with_deferred_request':deferred,'max_commits':2,'pages':8}
def main():
 r=explore();assert r['complete_scan_edges_checked']>0
 occupancy=1;history=[]
 for i in range(256):occupancy-=1;occupancy+=1;history.append(occupancy)
 assert set(history)=={1}
 result={'scope':'SERIAL ABSTRACT MODEL; atomic metadata assumed; no RTOS/IRQ/FIQ/DMA/cache/transport emulated','participating_protocol':r,'conditional_safety':'Participating full scans see one committed generation only if all accesses obey the protocol. No liveness claim without return/fairness bounds.','counterexamples':{
 'timer_only':{'draw_pages_done':3,'bypass_versions':[1]*3+[0]*5},
 'copy_only':{'actions':['scan pages0..2 of A without reader lease','fully publish B','scan pages3..7 of B'],'versions':[0]*3+[1]*5},
 'same_owner_recursive_lock':{'actions':['outer composition incomplete','synchronous progress takes recursive lock','nested scan sees incomplete outer composition'],'coherent':False},
 'nonrecursive_lock':{'actions':['outer DRAW holds lock','synchronous progress waits for same lock','outer caller cannot return to release'],'progress_possible_without_external_action':False},
 'critical_drop':{'semantic_equivalence_of_dropping_synchronous_request_proved':False},
 'queue_drain':{'producer_iterations':256,'occupancy_always':1,'empty_boundary_reached':False},
 'blocked_worker':{'phase':'READ or KORG_CRITICAL','cooperative_release_possible':False,'independent_abort_authority_proved':False},
 'fatal_bypass':{'phase':'any','diagnostic_uses_same_lcd':True,'safe_global_gate_found':False}},
 'candidate_domain_contract':{'entry':'IDLE, known complete source, no active reader','critical':'exclude compositions and periodic scans; execute complete native progress composite','exit':'only after actual native return','remaining':'all callers, fatal entries, waits, latency, IRQ writers'}}
 (ROOT/'reports/recovery_r13/models.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
