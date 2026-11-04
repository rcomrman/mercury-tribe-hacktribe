#!/usr/bin/env python3
"""Seal current R17 proof files after verification. Manifest excludes itself."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 paths=[p for d in ('tests/recovery_r17','tools/recovery_r17','reports/recovery_r17') for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='provenance.json']
 paths += [ROOT/'tests/run_recovery_r17.sh',ROOT/'RECOVERY_R17_RAPPORT_FR.md',*ROOT.glob('documents/RECOVERY_R17_*.md')]
 versions={cmd:subprocess.check_output([cmd,'--version'],text=True).splitlines()[0] for cmd in ('clang','ld.lld','qemu-arm')}
 data={'base_commit':'60eddcdd2cc06dff43b71d5459b147d8c835457f','scope':'RESEARCH_ONLY; finite opt-in CPU graph, externally serialized. No global cessation, native integration, peripheral reply or free.','experiments':58,'normal_returns':54,'expected_faults':4,'vsb_sha256':json.loads((ROOT/'reports/recovery_r17/results.json').read_text())['vsb_sha256'],'toolchain':versions,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
 (ROOT/'reports/recovery_r17/provenance.json').write_text(json.dumps(data,indent=2)+'\n');print('Sealed',len(data['sha256']),'SHA-256 entries')
if __name__=='__main__':main()
