#!/usr/bin/env python3
"""Seal actual R19 sources/evidence. No invented hashes; manifest excludes itself."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 paths=[p for d in ('tests/recovery_r19','tools/recovery_r19','reports/recovery_r19') for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='provenance.json']
 paths += [p for p in [ROOT/'tests/run_recovery_r19.sh',ROOT/'RECOVERY_R19_RAPPORT_FR.md',*ROOT.glob('documents/RECOVERY_R19_*.md')] if p.exists()]
 data={'base_commit':'6808871b54c10e130e085ab4e658bc8bf3cbf1bb','scope':'RESEARCH_ONLY. Externally serialized constructor reservations, immutable fixture anchors, no native integration/free/global destruction or peripheral response.','experiments':62,'normal_returns':50,'expected_faults':8,'controlled_incomplete_constructor_exits':2,'host_timeouts':2,'vsb_sha256':json.loads((ROOT/'reports/recovery_r19/results.json').read_text())['vsb_sha256'],'toolchain':{x:subprocess.check_output([x,'--version'],text=True).splitlines()[0] for x in ('clang','ld.lld','qemu-arm')},'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
 (ROOT/'reports/recovery_r19/provenance.json').write_text(json.dumps(data,indent=2)+'\n');print('Sealed',len(data['sha256']),'actual R19 files')
if __name__=='__main__':main()
