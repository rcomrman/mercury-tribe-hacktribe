#!/usr/bin/env python3
"""R9 roles reused; new bounded atomic-metadata model, not an ARM memory model."""
import collections,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r9_models',ROOT/'tools/recovery_r9/models.py');r9=importlib.util.module_from_spec(spec);spec.loader.exec_module(r9)
def explore(n):
 # pub, reader, writer, filled, closing, versions, publication count.
 start=(0,-1,-1,0,0,tuple([0]*n),0);seen={start};todo=collections.deque([start]);edges=0;blocked=0;terminal=0
 while todo:
  s=todo.popleft();pub,reader,writer,filled,closing,versions,k=s
  assert writer<0 or writer not in (pub,reader)
  next_states=[]
  if closing and reader<0 and writer<0:terminal+=1
  if not closing:
   next_states.append((pub,reader,writer,filled,1,versions,k))
   if reader<0:next_states.append((pub,pub,writer,filled,0,versions,k))
   if writer<0 and k<4:
    free=set(range(n))-{pub,reader}
    if not free:blocked+=1
    for w in free:
     v=list(versions);v[w]=k+1;next_states.append((pub,reader,w,0,0,tuple(v),k))
   if writer>=0 and not filled:next_states.append((pub,reader,writer,1,0,versions,k))
   if writer>=0 and filled:next_states.append((writer,reader,-1,0,0,versions,k+1))
  if reader>=0:next_states.append((pub,-1,writer,filled,closing,versions,k))
  if writer>=0:next_states.append((pub,reader,-1,0,closing,versions,k))
  for t in next_states:
   # A pinned reader's bytes/version cannot change in any legal transition.
   if reader>=0:assert t[5][reader]==versions[reader]
   edges+=1
   if t not in seen:seen.add(t);todo.append(t)
 return {'states':len(seen),'transitions':edges,'blocked_writer_states':blocked,'closed_states':terminal,'max_publications':4}
def main():
 out=ROOT/'reports/recovery_r12';roles={str(n):explore(n) for n in (2,3)}
 assert roles['2']['blocked_writer_states']>0 and roles['3']['blocked_writer_states']==0
 # Reuse actual R9 fixed-source example helper, without replaying its enumeration.
 order='WWW'+'RRRRRRRR'+'WWWWW';read,_=r9.shared(order);assert read==[1]*3+[0]*5
 # A single scan at each byte-copy cut: granularity finer than R9 page abstraction.
 cuts={'coherent':0,'mixed':0}
 for cut in range(1025):
  image=[1]*cut+[0]*(1024-cut);cuts['coherent' if len(set(image))==1 else 'mixed']+=1
 assert cuts=={'coherent':2,'mixed':1023}
 # No atomic publication/acquire: preemption inside acquire can select a recycled slot.
 split=['reader loads published=0, generation=1','writer publishes slot 1','writer reuses unpinned slot 0 and publishes generation 3','reader stores pin=0; stale generation 1 points to rewritten bytes']
 # Protecting only the memcpy does not protect a subsequent eight-page scan.
 copy_only=['lock: full copy A to fixed source; unlock','reader copies pages 0..2 of A','lock: full copy B to fixed source; unlock','reader copies pages 3..7 of B']
 result={'scope':'DETERMINISTIC SERIAL MODEL; atomic metadata actions assumed, not implemented synchronization; no IRQ, DMA, cache, RTOS or transport emulation','r9_helper_reused':'tools/recovery_r9/models.py:shared','bounded_roles':roles,'byte_copy_cuts':cuts,'counterexamples':{'private_pointer_swap':{'native_fixed_source_changes':False},'unprotected_fixed_copy':{'schedule':order,'shadow_versions':read},'split_acquire':split,'copy_only_lock':copy_only,'nonparticipating_native_writer':['writer A holds proposed semaphore','native C0015988 never takes it','fixed source changes despite count=0'],'cooperative_watchdog':['worker enters polling loop','same task watchdog callback never reached'],'lock_across_worker':['hold source lock across scan/send','worker blocks before returning','reader borrow and lock cannot be released by cooperative caller']},'conditional_invariants':['no write to published or pinned slot','publish only fully filled image','metadata actions serialized','fixed composition and full reader interval participate in exclusion','close rejects new work, drains reader/writer before storage release'],'not_proved':['progress with stalled reader','multiple readers/writers','ARM atomicity and memory visibility','physical transfer acknowledgement']}
 (out/'models.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'roles':roles,'byte_copy_cuts':cuts},indent=2))
if __name__=='__main__':main()
