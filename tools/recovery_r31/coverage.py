#!/usr/bin/env python3
"""Finite path hitting sets for explicitly selected R13 paths, not firmware dominance."""
import itertools,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r31'
# Each set lists verified named nodes along one selected path, not all paths in its domain.
paths={
 'main_ui':['C002D030','C00836E4','C006F178'],
 'alternate_ui':['C002D030','C0083374'],
 'secondary':['C002D030','C00836E4','C006EAE0'],
 'periodic_worker':['C002A71C','C0015DD0','C0015FA0','C0015AB4'],
 'progress':['C004D860','C006038C','C0015DD0','C0015FA0','C0015AB4'],
 'startup':['C0015EB8','C0015FA0','C0015AB4'],
 'diagnostic':['C00298BC','C0015DD0','C0015FA0','C0015AB4'],
 'direct_comparator':['C0015AB4'],
 'lcd_control7':['C0015DD0','C00162C4'],
 'direct_pixel':['C0015824'],
 'direct_range':['C003F55C','C0015988'],
 'direct_reader':['C0071EC8','C0015900'],
}
def main():
 candidates=sorted(set().union(*map(set,paths.values())));sets=[]
 for n in range(1,len(candidates)+1):
  for x in itertools.combinations(candidates,n):
   if all(set(x)&set(p) for p in paths.values()):sets.append(x)
  if sets:break
 O.mkdir(parents=True,exist_ok=True)
 data={'paths':paths,'candidate_count':len(candidates),'minimum_cardinality':len(sets[0]),'minimum_sets':sets,'scope':'hitting listed paths only; a hit is not verified dominance, atomicity, or authorization'}
 (O/'coverage.json').write_text(json.dumps(data,indent=2)+'\n')
 print('PASS bounded graph:',len(paths),'selected paths;',len(sets),'minimum sets of',len(sets[0]),'nodes; not global coverage')
if __name__=='__main__':main()
