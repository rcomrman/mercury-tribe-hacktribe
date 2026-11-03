#!/usr/bin/env python3
"""Exhaustive bounded participating-access protocol, and explicit bypass/liveness witnesses."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def explore():
 # phase0 idle,1 draw,2 scan; page cursor; source/shadow; pending; committed; read-version.
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
 # A producer appending one event per consumption keeps the drain nonempty.
 occupancy=1;history=[]
 for i in range(256):occupancy-=1;occupancy+=1;history.append(occupancy)
 assert set(history)=={1}
 # Adding a lock to timer only leaves direct progress read in a partial draw.
 bypass=[1]*3+[0]*5;assert len(set(bypass))==2
 result={'scope':'SERIAL ABSTRACT MODEL; metadata actions atomic by assumption; page steps simplify native byte operations; no RTOS, IRQ/FIQ, DMA, cache, transport or independent recovery emulated','participating_protocol':r,'conditional_safety':'All eight-page reads begun through the coordinator see one committed source generation, if every writer/reader participates and no aborted partial draw is returned to IDLE. No liveness claim without return/fairness bounds.','counterexamples':{
 'timer_only':{'draw_pages_done':3,'direct_progress_or_compare_bypass_versions':bypass},
 'copy_only':{'actions':['scan pages0..2 of A without reader lease','serialize and fully publish B','scan pages3..7 of B'],'versions':[0]*3+[1]*5},
 'same_owner_recursive_lock':{'actions':['outer native UI composition incomplete','same thread calls progress draw+scan','recursive lock permits it','reader sees incomplete outer composition'],'coherent':False},
 'nonrecursive_lock':{'actions':['outer DRAW holds lock','synchronous progress requests same lock','caller waits for itself before outer DRAW can finish'],'progress_possible_without_external_action':False},
 'critical_drop':{'actions':['UI gate refuses synchronous progress worker','caller interprets ordinary return as completed critical service'],'semantic_equivalence_proved':False},
 'queue_drain':{'producer_iterations':256,'occupancy_always':1,'empty_boundary_reached':False,'limit':'Finite witness plus inductive repeating transition; not a hardware rate claim.'},
 'blocked_worker':{'phase':'READ or KORG_CRITICAL','caller_can_release_by_cooperative_timeout':False,'independent_abort_authority_proved':False},
 'fatal_bypass':{'phase':'any','diagnostic_uses_same_lcd':True,'safe_global_gate_found':False}},
 'candidate_domain_contract':{'entry':'IDLE and known complete source, no active borrow/reader','critical':'exclude new compositions and periodic scans, execute complete original progress composite; internal draw precedes internal read','exit':'only on actual return; no forced release while native code may still run','remaining':'all callers, fatal entries, hardware waits, latency bounds and IRQ writers must still be qualified'}}
 (ROOT/'reports/recovery_r13/models.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
