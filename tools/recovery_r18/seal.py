#!/usr/bin/env python3
"""SHA-256 seal of actual R18 files; manifest excludes itself."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 paths=[p for d in ('tests/recovery_r18','tools/recovery_r18','reports/recovery_r18') for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='provenance.json']
 paths += [p for p in [ROOT/'tests/run_recovery_r18.sh',ROOT/'RECOVERY_R18_RAPPORT_FR.md',*ROOT.glob('documents/RECOVERY_R18_*.md')] if p.exists()]
 data={'base_commit':'c4fe851f64d325bc6311e4aa7cbee85ce2707cab','scope':'RESEARCH_ONLY. Monotonic pool, opt-in immutable fixture callbacks, external serialization; no global destruction or peripheral cessation.','experiments':62,'normal_returns':54,'expected_faults':6,'host_timeouts':2,'vsb_sha256':json.loads((ROOT/'reports/recovery_r18/results.json').read_text())['vsb_sha256'],'toolchain':{x:subprocess.check_output([x,'--version'],text=True).splitlines()[0] for x in ('clang','ld.lld','qemu-arm')},'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
 (ROOT/'reports/recovery_r18/provenance.json').write_text(json.dumps(data,indent=2)+'\n');print('Sealed',len(paths),'actual files')
if __name__=='__main__':main()
