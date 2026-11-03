#!/usr/bin/env python3
"""Independent archive reparse, byte oracles and preservation check against R11."""
import gzip,json,subprocess
from pathlib import Path
from run import ROOT,decode,validate,sha
from models import explore
BASE='f565a58b198fe317dc84fd6ea2123c3e64412b0c'
def main():
 out=ROOT/'reports/recovery_r12';r=json.loads((out/'results.json').read_text());assert not r['exploratory'] and len(r['cases'])==52
 frames=(ROOT/'build/recovery_r12/frames.bin').read_bytes();assert sha(frames)==r['frames_sha256']
 for row in r['cases']:
  stem=f'{row["vsb"]}_{row["case"]}';raw=gzip.decompress((out/(stem+'.records.gz')).read_bytes());events=decode(raw,row['case']);assert events==row['events']
  validate(row['case'],row['exit'],events,gzip.decompress((out/(stem+'.trace.gz')).read_bytes()).decode(),raw,frames)
 for x,y in zip(r['cases'][:26],r['cases'][26:]):assert x['events']==y['events'] and x['exit']==y['exit']
 m=json.loads((out/'models.json').read_text());assert m['bounded_roles']=={str(n):explore(n) for n in (2,3)} and m['byte_copy_cuts']=={'coherent':2,'mixed':1023}
 oldfiles=subprocess.run(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
 # Every previously tracked path, not just artistic directories, must remain intact.
 assert not subprocess.run(['git','diff',BASE,'--',*oldfiles],cwd=ROOT,capture_output=True,check=True).stdout
 archives={}
 for mission in (8,9,10,11):
  files=sorted((ROOT/f'reports/recovery_r{mission}').glob('*.gz'))
  for p in files:gzip.decompress(p.read_bytes())
  archives[str(mission)]={'files':len(files),'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in files}}
 files=[p for folder in ('tests/recovery_r12','tools/recovery_r12','reports/recovery_r12') for p in sorted((ROOT/folder).glob('*')) if p.is_file() and p.name!='provenance.json']
 files.extend(ROOT/p for p in ('RECOVERY_R12_RAPPORT_FR.md','documents/RECOVERY_R12_TRIPLE_BUFFER_ARCHITECTURE_FR.md','tests/run_recovery_r12.sh'))
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; original code RX, private kernel fixtures, deterministic serial interleavings, no MMIO response, no real RTOS/IRQ/FIQ/DMA proof','native_cases':52,'normal_exits':sum(x['exit']==0 for x in r['cases']),'expected_fault_exits':sum(x['exit']==88 for x in r['cases']),'all_preexisting_paths_unchanged':True,'prior_archives_checked_without_replay':archives,'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in files}},indent=2)+'\n')
 print('PASS: 52 cases, 32 V30 images per VSB, native semaphore/priority branches and expected faults; models independently re-enumerated; all R1-R11 tracked files unchanged')
if __name__=='__main__':main()
