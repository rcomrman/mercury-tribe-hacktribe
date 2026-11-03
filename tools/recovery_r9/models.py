#!/usr/bin/env python3
"""Deterministic publication models. No claim about ARM atomics, IRQ or device I/O."""
import itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/recovery_r9'
def schedules():
 for writes in itertools.combinations(range(16),8):
  w=set(writes);yield ''.join('W' if i in w else 'R' for i in range(16))
def shared(order,gate=False):
 source=[0]*8;read=[];wi=0;actions=[]
 # Each action represents a 128-byte page. Atomic page steps are a model simplification.
 if gate:order='W'*8+'R'*8 if order[0]=='W' else 'R'*8+'W'*8
 for a in order:
  if a=='W':source[wi]=1;wi+=1;actions.append(f'write_page_{wi-1}')
  else:read.append(source[len(read)]);actions.append(f'read_page_{len(read)-1}')
 return read,actions

def main():
 OUT.mkdir(parents=True,exist_ok=True);counts={'shared':{'coherent':0,'mixed':0},'phase_serialized':{'coherent':0,'mixed':0}};examples={}
 for order in schedules():
  for policy in counts:
   read,actions=shared(order,policy=='phase_serialized');mixed=len(set(read))>1
   counts[policy]['mixed' if mixed else 'coherent']+=1
   if mixed and policy not in examples:examples[policy]={'schedule':order,'actions':actions,'observed_page_versions':read}
 assert sum(counts['shared'].values())==12870
 assert counts['shared']['mixed']>0 and counts['phase_serialized']['mixed']==0
 # Double buffering does not protect a borrowed old frame after publication changes.
 slots=[[0]*8,[None]*8];published=0;pinned=0
 for i in range(8):slots[1][i]=1
 published=1
 for i in range(8):slots[0][i]=2
 assert slots[pinned]==[2]*8 # old reader was expecting version 0
 examples['double_unpinned']={'actions':['reader borrows slot 0 (version 0)','writer fills slot 1 (version 1)','publish slot 1','writer reuses slot 0 (version 2)'],'reader_expected':0,'reader_observed':2}
 # Explore allocator role choices for 2/3 slots: never select reader or published slot.
 role_checks={}
 for n in (2,3):
  checks=0;blocked=0
  for pub in range(n):
   for reader in range(n):
    free=set(range(n))-{pub,reader}
    for candidate in range(n):
     allowed=candidate in free
     if allowed:assert candidate!=pub and candidate!=reader
     checks+=1
    blocked+=not free
  role_checks[str(n)]={'role_assignments':n*n,'candidate_checks':checks,'states_without_free_slot':blocked}
 assert role_checks['2']['states_without_free_slot']==2
 assert role_checks['3']['states_without_free_slot']==0
 # Single reader held for 128 publications, three roles, no writes to published/held reader.
 slots=[[0]*8,[None]*8,[None]*8];pub=0;reader=0;published_versions=[]
 for version in range(1,129):
  target=min(set(range(3))-{pub,reader});slots[target]=[version]*8;pub=target
  assert slots[reader]==[0]*8;published_versions.append(slots[pub][0])
 assert published_versions==list(range(1,129))
 # Stable private buffers still need exclusion when copying into fixed native source.
 staged,actions=shared(examples['shared']['schedule'])
 assert len(set(staged))>1
 examples['copy_to_native_without_phase']={'schedule':examples['shared']['schedule'],'observed_page_versions':staged}
 # Version check detects interference in staging; cannot undo already published pages.
 examples['memcmp_copy_gap']={'actions':['memcmp(source,shadow) sees equal version 0','writer commits source version 1','unconditional memcpy copies version 1 into shadow','comparator returns cached changed=false'],'source_version':1,'shadow_version':1,'displayed_version_logical_only':0,'model_only':'Interrupting native comparator not executed under QEMU; gap established statically.'}
 epoch_checks=0;accepted=0;rejected=0
 for order in schedules():
  read,_=shared(order)
  # Writer transaction starts with its first W, ends with its eighth W.
  first_w=order.index('W');last_w=order.rindex('W');first_r=order.index('R');last_r=order.rindex('R')
  start_epoch=0 if first_r<first_w else (2 if first_r>last_w else 1)
  end_epoch=0 if last_r<first_w else (2 if last_r>last_w else 1)
  ok=start_epoch==end_epoch and start_epoch%2==0
  if ok:assert len(set(read))==1;accepted+=1
  else:rejected+=1
  epoch_checks+=1
 assert rejected>0 and accepted>0
 # Bounded counter ABA: model with 8 bits; same arithmetic applies to wider counters.
 assert (0+2*128)%256==0
 examples['version_wrap']={'counter_bits':8,'completed_writes':128,'initial_epoch':0,'final_epoch':0,'false_accept_possible':True,'32_bit_equivalent_writes':2**31}
 # Shadow is prepared before attempted transport: demonstrate why equality is not acknowledgement.
 source=1;shadow=1;displayed=0
 assert source==shadow and displayed!=source
 examples['shadow_not_ack']={'source_version':source,'shadow_version':shadow,'displayed_version_logical_only':displayed,'native_comparator_would_report_changed':False}
 pending=1;confirmed=0
 for outcome in (False,False,True):
  if outcome:confirmed=pending;pending=None
  else:assert pending==1 and confirmed==0
 assert confirmed==1 and pending is None
 # Lifetime model: mutation/destruction deferred while either draw or scan has a borrow.
 lifetime=[]
 for draw,scan,transition in itertools.product((0,1),repeat=3):
  allowed=bool(transition and not draw and not scan)
  assert not allowed or (draw==scan==0)
  lifetime.append({'draw_borrow':draw,'scan_borrow':scan,'requested':transition,'destroy_allowed':allowed})
 # A generation-qualified borrowed handle rejects a recycled address.
 handle=(0x1000,7);recycled=(0x1000,8);assert handle[0]==recycled[0] and handle!=recycled
 result={'scope':'SEQUENTIAL ABSTRACT MODELS; no native scheduler, MMIO, DMA or ARM memory model','page_bytes':128,'pages':8,'interleavings_per_policy':12870,'phase_serialized_unique_legal_orders':2,'counts':counts,'counterexamples':examples,'pinned_buffer_roles':role_checks,'triple_publications_under_one_pinned_reader':128,'staged_epoch':{'schedules':epoch_checks,'accepted_coherent':accepted,'rejected':rejected},'lifetime_cases':lifetime,'generation_handle':{'address_reused':True,'generation_rejects_stale_handle':True},'buffer_payload_bytes':{'phase_over_fixed_native_source':0,'double_private_buffers':2048,'triple_private_buffers':3072,'epoch_staging':1024},'cost_limits':'Excludes metadata, alignment, renderer storage, stack and native source/shadow. No free instrument RAM established.'}
 (OUT/'publication_models.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'counts':counts,'roles':role_checks,'epoch':result['staged_epoch']},indent=2))
if __name__=='__main__':main()
