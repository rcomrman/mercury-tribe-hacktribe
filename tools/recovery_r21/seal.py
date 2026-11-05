#!/usr/bin/env python3
"""Seal the final R21 deliverables without including the manifest itself."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
paths=[ROOT/'RECOVERY_R21_RAPPORT_FR.md']
for folder,pattern in (('documents','RECOVERY_R21_*'),('tests/recovery_r21','*'),('tools/recovery_r21','*'),('reports/recovery_r21','*')):
 for p in (ROOT/folder).glob(pattern):
  if p.is_file() and p.name!='provenance.json':paths.append(p)
paths.append(ROOT/'tests/run_recovery_r21.sh')
data={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
out=ROOT/'reports/recovery_r21/provenance.json';out.write_text(json.dumps({'sha256':data},indent=2)+'\n')
print('sealed',len(data),'R21 files')
