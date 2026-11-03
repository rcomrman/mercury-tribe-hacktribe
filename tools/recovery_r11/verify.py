#!/usr/bin/env python3
"""Reparse all R11 records and preserve earlier evidence/source trees against R10."""
import gzip,hashlib,json,struct,subprocess
from pathlib import Path
from run import ROOT,validate
BASE='2d58ac8a5df4528c052fa287d5d792b34e981a11'
def main():
 out=ROOT/'reports/recovery_r11';r=json.loads((out/'results.json').read_text());assert not r['exploratory'] and len(r['cases'])==64
 for row in r['cases']:
  stem=f'{row["vsb"]}_{row["case"]}';raw=gzip.decompress((out/(stem+'.records.gz')).read_bytes());assert len(raw)%160==0
  events=[struct.unpack_from('<40I',raw,p) for p in range(0,len(raw),160)]
  assert [list(e) for e in events]==row['events'];validate(row['case'],row['exit'],events,gzip.decompress((out/(stem+'.trace.gz')).read_bytes()).decode())
  stages={e[2]:e for e in events};c=row['case']
  if c in (2,3):assert stages[1][4]==(1 if c==2 else 10)
  if c==7:assert stages[1][11]>>16&255==0xa5
  if c in (12,24):assert stages[1][4]==2 and stages[2][4]==0
  if c==25:assert stages[1][4]==0xc06a24e4
  if c==26:assert stages[1][4]==0xc06a2544
  if c in (27,28):assert stages[1][3:5]==(2,2)
  if c in (29,30):assert stages[1][3:5]==(0 if c==29 else 0xffffffce,1)
 for x,y in zip(r['cases'][:32],r['cases'][32:]):assert x['events']==y['events'] and x['exit']==y['exit']
 protected=['src','reference']+[f'{d}/recovery_r{i}' for i in range(1,11) for d in ('tests','tools','reports')]+[f'RECOVERY_R{i}_RAPPORT_FR.md' for i in range(1,11)]+['documents/RECOVERY_R9_ARCHITECTURE_INTEGRATION_FR.md']
 assert not subprocess.run(['git','diff',BASE,'--',*protected],cwd=ROOT,capture_output=True,check=True).stdout
 old_archives={}
 for mission in (8,9,10):
  files=sorted((ROOT/f'reports/recovery_r{mission}').glob('*.gz'))
  for p in files:gzip.decompress(p.read_bytes())
  old_archives[str(mission)]={'gzip_count':len(files),'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 paths=[p for folder in ('tests/recovery_r11','tools/recovery_r11','reports/recovery_r11') for p in sorted((ROOT/folder).glob('*')) if p.is_file() and p.name!='provenance.json']
 paths.extend(ROOT/p for p in ('RECOVERY_R11_RAPPORT_FR.md','documents/RECOVERY_R11_TASK_MAP_FR.md','tests/run_recovery_r11.sh'))
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; original ARM RX; bounded private kernel data; no MMIO; no scheduler emulation','native_cases':64,'normal_exits':sum(x['exit']==0 for x in r['cases']),'fault_exits':sum(x['exit']==88 for x in r['cases']),'previous_trees_unchanged':True,'previous_archives_crc_checked':old_archives,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},indent=2)+'\n')
 print('PASS: 64 native cases, cross-VSB exact snapshots, expected faults/returns, guards; R1-R10 and artistic trees unchanged; archived R8-R10 gzip integrity checked')
if __name__=='__main__':main()
