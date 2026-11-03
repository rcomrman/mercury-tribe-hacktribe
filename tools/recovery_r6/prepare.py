#!/usr/bin/env python3
"""Prepare existing R2 support without replaying earlier missions or changing them."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def prepare():
 b=ROOT/'build/recovery_r2';b.mkdir(parents=True,exist_ok=True)
 f=ROOT/'build/recovery_r1/frames.bin';f.parent.mkdir(parents=True,exist_ok=True)
 sources=['src/md15_bridge.c','src/md21_v14_profiles.c','src/mercury_live.c','src/mercury_events.c','src/mercury_glitch.c','src/lcd_source_mux.c']
 host=b/'frames_host'
 subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-Isrc','tests/recovery_r1/frames.c',*sources,'-o',str(host)],cwd=ROOT,check=True)
 with f.open('wb') as out:subprocess.run([str(host)],stdout=out,check=True,cwd=ROOT)
 expected=json.loads((ROOT/'reports/recovery_r2/results.json').read_text())['frames_sha256']
 assert hashlib.sha256(f.read_bytes()).hexdigest()==expected
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-c','tests/recovery_r2/start.S','-o',str(b/'start.o')],cwd=ROOT,check=True)
 # Exact assembly support from the published R2 orchestrator, not a new wrapper.
 source=(ROOT/'tools/recovery_r2/run.py').read_text()
 asm=source.split("  asm='''",1)[1].split("'''",1)[0]
 (b/'original.S').write_text(asm)
if __name__=='__main__':prepare()
