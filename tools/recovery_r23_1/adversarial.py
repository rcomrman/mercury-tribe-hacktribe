#!/usr/bin/env python3
"""Small reproducible traces; physical completions are synthetic events."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from model import State
ROOT=Path(__file__).resolve().parents[2]
CASES={
 'A_collision': [('request_mercury',None,None),('grant_mercury',None,None),('begin_mercury',1,7),('begin_korg',2,4),('complete',2,None),('complete',1,None)],
 'A_reverse_completion': [('request_mercury',None,None),('grant_mercury',None,None),('begin_mercury',1,7),('begin_korg',2,4),('complete',1,None),('complete',2,None)],
 'B_suppressed_shadow': [('korg_frame',None,4),('compare',None,None),('request_mercury',None,None),('grant_mercury',None,None),('begin_mercury',1,7),('complete',1,None),('exit',None,None),('grant_korg',None,None)],
 'C_exit_inflight': [('request_mercury',None,None),('grant_mercury',None,None),('begin_mercury',1,7),('exit',None,None),('grant_korg',None,None),('complete',1,None)],
 'C_fault_late': [('request_mercury',None,None),('grant_mercury',None,None),('begin_mercury',1,7),('fault',None,None),('complete',1,None)],
 'reentry': [('request_mercury',None,None),('request_mercury',None,None)],
 'uncontrolled': [('request_mercury',None,None),('grant_mercury',None,None),('begin_uncontrolled',1,9)],
 'logical_without_ack': [('begin_korg',1,1),('logical_complete',1,None),('request_mercury',None,None),('grant_mercury',None,None)],
 'spontaneous_recovery': [('korg_frame',None,4),('compare',None,None),('begin_korg',1,4),('complete',1,None)],
}
def main():
 results={}
 for name,events in CASES.items():
  s=State();trace=[]
  for op,token,value in events:
   s.event(op,token,value);trace.append(dict(event=op,owner=s.owner,mode=s.mode,framebuffer=s.framebuffer,shadow=s.shadow,lcd=s.lcd,pending=sorted(s.pending),violations=list(s.violations),fault=s.fault))
  results[name]=trace
 assert results['A_collision'][-1]['lcd']==7 and results['A_reverse_completion'][-1]['lcd']==4
 assert 'unrestored_display' in results['B_suppressed_shadow'][-1]['violations']
 assert 'unjustified_grant' in results['logical_without_ack'][-1]['violations']
 out=ROOT/'reports/recovery_r23_1';out.mkdir(parents=True,exist_ok=True)
 (out/'adversarial.json').write_text(json.dumps(results,indent=2)+'\n')
 print('PASS',len(results),'targeted adversarial traces, including late completion, false ACK and two completion orders')
if __name__=='__main__':main()
