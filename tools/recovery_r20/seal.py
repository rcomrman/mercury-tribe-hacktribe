#!/usr/bin/env python3
"""Hash actual R20 deliverables, excluding this manifest and a running launcher log."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r20'
def main():
 paths=[p for folder in ('tests/recovery_r20','tools/recovery_r20','reports/recovery_r20') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name not in ('provenance.json','launcher-validation.log')]
 paths += [p for p in [ROOT/'tests/run_recovery_r20.sh',ROOT/'RECOVERY_R20_RAPPORT_FR.md',*ROOT.glob('documents/RECOVERY_R20_*.md')] if p.exists()]
 data=dict(base_commit='dce3fdc74b8dd0a0168f8ae920375fab52c6b31a',resumed_phase1_commit='a220be8a5ac338f5bf8af79d838a8e8e05127fca',scope='RESEARCH_ONLY; externally serialized fixtures; no native patch, firmware, free, flash or hardware trial',runs=48,normal_returns=32,controlled_stops_before_free=8,expected_faults=6,host_timeouts=2,vsb_sha256=json.loads((OUT/'results.json').read_text())['vsb_sha256'],toolchain={tool:subprocess.check_output([tool,'--version'],text=True).splitlines()[0] for tool in ('clang','ld.lld','qemu-arm')},sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))})
 (OUT/'provenance.json').write_text(json.dumps(data,indent=2)+'\n');print('Sealed',len(paths),'actual R20 files. Launcher transcript excluded while running; Git preserves it.')
if __name__=='__main__':main()
