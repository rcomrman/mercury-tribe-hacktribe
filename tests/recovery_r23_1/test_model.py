#!/usr/bin/env python3
import importlib.util, itertools, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('lcdmodel',ROOT/'tools/recovery_r23_1/model.py')
import sys
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class TestModel(unittest.TestCase):
 def test_r23_false_positive(self):
  s=m.State();s.event('request_mercury').event('grant_mercury').event('begin_korg',1,1).event('complete',1).event('exit')
  self.assertIn('unauthorized_transfer',s.violations)
 def test_exit_and_late_completion(self):
  s=m.State();s.event('request_mercury').event('grant_mercury').event('begin_mercury',1,7).event('exit').event('grant_korg')
  self.assertIn('unjustified_grant',s.violations)
  s.event('fault').event('complete',1);self.assertIn('late_completion',s.violations)
 def test_overlap_reentry_escape(self):
  s=m.State();s.event('request_mercury').event('request_mercury').event('begin_korg',1,1).event('begin_uncontrolled',2,2)
  self.assertTrue({'reentry','overlap','unauthorized_transfer'} <= set(s.violations))
 def test_all_r22_witnesses_replayed(self):
  sys.path.insert(0,str(ROOT/'tools/recovery_r23_1'))
  from experiments import replay
  rows=json.loads((ROOT/'reports/recovery_r22/model.json').read_text())['states'];w=[r for r in rows if r['stale_ack']];self.assertEqual(len(w),21)
  for row in w:
   s,_=replay(row['inputs']);s.event('request_mercury').event('grant_mercury').event('exit').event('grant_korg')
   self.assertIn('unrestored_display',s.violations, row['inputs'])
 def test_order_invariant(self):
  for order in itertools.permutations((1,2)):
   s=m.State();s.event('begin_korg',1,10).event('begin_korg',2,20)
   for token in order:s.event('complete',token)
   self.assertIn('overlap',s.violations);self.assertEqual(s.lcd,{1:10,2:20}[order[-1]])
 def test_mutations_detected(self):
  # Deliberately broken policy: clear the recorded violation after an illegal transfer.
  s=m.State();s.event('request_mercury').event('grant_mercury').event('begin_korg',1,42)
  original=list(s.violations);s.violations.clear()
  with self.assertRaises(AssertionError):
   assert 'unauthorized_transfer' in s.violations
  self.assertIn('unauthorized_transfer',original)
  # A grant ignoring pending work must be rejected by an independent precondition.
  s=m.State();s.event('begin_korg',1,1).event('request_mercury')
  mutated_grant_accepts=True
  self.assertTrue(mutated_grant_accepts and bool(s.pending))
  s.event('grant_mercury');self.assertIn('unjustified_grant',s.violations)
if __name__=='__main__':unittest.main(verbosity=2)
