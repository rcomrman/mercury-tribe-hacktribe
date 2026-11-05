#!/usr/bin/env python3
"""Exhaustive abstract LCD suppression/EXIT model; simulation, not native proof."""
import itertools,json
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'reports/recovery_r22';O.mkdir(parents=True,exist_ok=True)
rows=[]
for shadow_before,transfer_inflight,korg_changes,mercury_sent,force_restore,fault in itertools.product((0,1),repeat=6):
 # Equality bits describe whether shadow/physical equal the current Korg frame.
 shadow=shadow_before;physical=shadow_before
 if transfer_inflight: physical=0 # completion order is outside the local interceptor
 if korg_changes: shadow=1       # comparator may copy before a suppressed physical send
 if mercury_sent: physical=0
 if force_restore and not fault: physical=shadow=1
 safe_exit=bool(force_restore and not fault and physical and shadow and not transfer_inflight)
 rows.append(dict(inputs=[shadow_before,transfer_inflight,korg_changes,mercury_sent,force_restore,fault],safe_exit=safe_exit,
  stale_ack=bool(korg_changes and shadow and not physical),needs_global_drain=bool(transfer_inflight)))
(O/'model.json').write_text(json.dumps({'states':rows},indent=2)+'\n')
print('PASS',len(rows),'states;',sum(r['safe_exit'] for r in rows),'safe only with forced complete restore, no fault/inflight transfer; stale-shadow witnesses',sum(r['stale_ack'] for r in rows))
