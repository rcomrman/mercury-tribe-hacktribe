#!/usr/bin/env python3
"""Independent archive checks and source preservation against the R8 commit."""
import gzip,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r9';BASE='2a81af1a1a869d73f2d71f7b3d43f6e7c36ee3b5'
def main():
 report=json.loads((OUT/'lcd_results.json').read_text());assert not report['exploratory'];rows=report['cases'];assert len(rows)==40
 for row in rows:
  raw=gzip.decompress((OUT/f'{row["vsb"]}_{row["case"]}.records.gz').read_bytes());assert len(raw)%2112==0
  expected=[]
  for pos in range(0,len(raw),2112):
   h=struct.unpack_from('<16I',raw,pos);assert h[0]==0x52394c43 and h[1]==row['case'] and h[6:8]==(0x39,0xc5)
   a=raw[pos+64:pos+1088];b=raw[pos+1088:pos+2112]
   expected.append({'header':list(h),'source_sha256':hashlib.sha256(a).hexdigest(),'shadow_sha256':hashlib.sha256(b).hexdigest(),'different_bytes':sum(x!=y for x,y in zip(a,b))})
  assert expected==row['events']
 for x,y in zip(rows[:20],rows[20:]):assert x['events']==y['events']
 diff=subprocess.run(['git','diff',BASE,'--','src','reference'],cwd=ROOT,capture_output=True,check=True).stdout;assert not diff
 sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('tests/recovery_r9','tools/recovery_r9','src') for p in sorted((ROOT/folder).glob('*')) if p.is_file()}
 (OUT/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; no MMIO pages mapped; no physical device tested','native_cases':40,'unchanged_src_and_reference':True,'documents_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'RECOVERY_R9_RAPPORT_FR.md',ROOT/'documents/RECOVERY_R9_ARCHITECTURE_INTEGRATION_FR.md')},'source_sha256':sources},indent=2)+'\n')
 print('PASS: 40 archived cases independently parsed; all source/shadow hashes and both guards verified; artistic sources unchanged')
if __name__=='__main__':main()
