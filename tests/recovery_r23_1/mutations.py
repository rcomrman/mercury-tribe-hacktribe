#!/usr/bin/env python3
"""Run independent behavioral oracles on real source-code mutants in memory."""
import pathlib,sys,types
root=pathlib.Path(__file__).resolve().parents[2]
source=(root/'tools/recovery_r23_1/model.py').read_text()
mutants={
 'exclusivity':("if who != self.owner or who == 'U':",'if False:'),
 'korg_during_mercury':("if who != self.owner or who == 'U':", "if who == 'U':"),
 'exit_inflight':("if self.mode != 'TRANSITION_TO_KORG' or self.pending or self.fault:","if self.mode != 'TRANSITION_TO_KORG' or self.fault:"),
 'logical_ack':("if token not in self.pending: self.violations.append('unknown_completion')\n        elif op == 'exit':", "if token in self.pending: self.pending.pop(token)\n        elif op == 'exit':"),
 'uncontrolled':("if who != self.owner or who == 'U':", "if who != self.owner and who != 'U':"),
 'erase_fault':("self.fault, self.mode = True, 'FAULT'", "self.fault, self.mode = False, 'FAULT'"),
}
def check(S,name):
 s=S()
 if name in ('exclusivity','korg_during_mercury'):
  s.event('request_mercury').event('grant_mercury').event('begin_korg',1,1);return 'unauthorized_transfer' in s.violations
 if name=='exit_inflight':
  s.event('request_mercury').event('grant_mercury').event('begin_mercury',1,0).event('exit').event('grant_korg');return 'unjustified_grant' in s.violations
 if name=='logical_ack':
  s.event('begin_korg',1,1).event('logical_complete',1);return 1 in s.pending and s.lcd==0
 if name=='uncontrolled':
  s.event('begin_uncontrolled',1,1);return 'unauthorized_transfer' in s.violations
 s.event('fault');return s.fault
def load(src,name):
 module=types.ModuleType(name);sys.modules[name]=module;exec(compile(src,name,'exec'),module.__dict__);return module.State
baseline=load(source,'baseline_r231')
for i,(name,(old,new)) in enumerate(mutants.items()):
 assert source.count(old)==1,(name,source.count(old))
 assert check(baseline,name),('baseline failed',name)
 mutated=load(source.replace(old,new),f'mutant_r231_{i}')
 assert not check(mutated,name),('SURVIVED',name)
 print('KILLED',name)
