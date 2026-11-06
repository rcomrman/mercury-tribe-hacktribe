#!/usr/bin/env python3
"""Independent bounded minimality check and R29 capture verification."""
import itertools,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];d=json.loads((R/'reports/recovery_r31/coverage.json').read_text());paths=[set(p) for p in d['paths'].values()];cand=sorted(set().union(*paths));n=d['minimum_cardinality']
assert len(paths)==12 and all(all(set(s)&p for p in paths) for s in d['minimum_sets'])
assert not any(all(set(s)&p for p in paths) for k in range(n) for s in itertools.combinations(cand,k))
assert len([s for s in itertools.combinations(cand,n) if all(set(s)&p for p in paths)])==len(d['minimum_sets'])
subprocess.run([sys.executable,str(R/'tools/recovery_r29/verify.py')],check=True)
print('PASS independent set minimality under explicit path model and preserved R29 EXIT streams')
