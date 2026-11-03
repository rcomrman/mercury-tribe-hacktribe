#!/usr/bin/env python3
"""Reparse R10 and R9 evidence without replaying earlier experiments."""
import gzip,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='43a57b986478992c7082e0615578e7a5c573c7d2'
def verify(folder,name,count):
 report=json.loads((folder/name).read_text());assert not report['exploratory'] and len(report['cases'])==count
 for row in report['cases']:
  raw=gzip.decompress((folder/f'{row["vsb"]}_{row["case"]}.records.gz').read_bytes());assert len(raw)%2112==0;events=[]
  for pos in range(0,len(raw),2112):
   h=struct.unpack_from('<16I',raw,pos);assert h[0]==0x52394c43 and h[1]==row['case'];a=raw[pos+64:pos+1088];b=raw[pos+1088:pos+2112]
   events.append({'header':list(h),'source_sha256':hashlib.sha256(a).hexdigest(),'shadow_sha256':hashlib.sha256(b).hexdigest(),'different_bytes':sum(x!=y for x,y in zip(a,b))})
  assert events==row['events']
 return len(report['cases'])
def main():
 out=ROOT/'reports/recovery_r10';assert verify(out,'results.json',26)==26
 assert verify(ROOT/'reports/recovery_r9','lcd_results.json',40)==40
 targets=['src','reference','tools/recovery_r9','tests/recovery_r9','reports/recovery_r9']
 assert not subprocess.run(['git','diff',BASE,'--',*targets],cwd=ROOT,capture_output=True,check=True).stdout
 paths=[ROOT/'RECOVERY_R10_RAPPORT_FR.md',ROOT/'tests/run_recovery_r10.sh']+[p for d in ('tests/recovery_r10','tools/recovery_r10') for p in (ROOT/d).glob('*') if p.is_file()]+[ROOT/'tests/recovery_r9/lcd.c',ROOT/'tests/recovery_r2/sys.h']
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'native_cases':26,'previous_R9_cases_checked_without_replay':40,'scope':'RESEARCH_ONLY; no MMIO emulation; not a hardware safety proof','source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},'historical_and_artistic_sources_unchanged':True},indent=2)+'\n')
 print('PASS: 26 R10 and 40 archived R9 records independently checked; prior sources unchanged')
if __name__=='__main__':main()
