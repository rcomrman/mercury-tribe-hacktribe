#!/usr/bin/env python3
"""Final recheck to run after workspace recovery; NOT executed in checkpoint session."""
import gzip,json,struct,subprocess
from run import ROOT,decode,validate,sha
from models import explore
BASE='9c4ba62541648ff057800c3b98619cdaa30092d8'
def main():
 out=ROOT/'reports/recovery_r13';r=json.loads((out/'results.json').read_text());assert not r['exploratory'] and len(r['cases'])==40
 frames=(ROOT/'build/recovery_r13/frames.bin').read_bytes();assert sha(frames)==r['frames_sha256']
 for row in r['cases']:
  stem=f'{row["vsb"]}_{row["case"]}';raw=gzip.decompress((out/(stem+'.records.gz')).read_bytes());events=decode(raw,row['case']);assert events==row['events']
  validate(row['case'],row['exit'],events,gzip.decompress((out/(stem+'.trace.gz')).read_bytes()).decode(),frames)
 for x,y in zip(r['cases'][:20],r['cases'][20:]):assert x['events']==y['events'] and x['exit']==y['exit']
 assert json.loads((out/'models.json').read_text())['participating_protocol']==explore()
 old=json.loads((ROOT/'reports/recovery_r12/results.json').read_text())
 for row in old['cases']:
  raw=gzip.decompress((ROOT/f'reports/recovery_r12/{row["vsb"]}_{row["case"]}.records.gz').read_bytes());events=[]
  for pos in range(0,len(raw),2112):
   h=struct.unpack_from('<16I',raw,pos);a=raw[pos+64:pos+1088];b=raw[pos+1088:pos+2112];events.append({'header':list(h),'source_sha256':sha(a),'shadow_sha256':sha(b),'different_bytes':sum(x!=y for x,y in zip(a,b))})
  assert events==row['events']
  if row['case'] in (4,17,24):
   snap=next(e for e in events if e['header'][2]==1);n=64 if row['case']==24 else 384;assert snap['shadow_sha256']==sha(bytes([0xee])*n+bytes([0x11])*(1024-n))
 oldfiles=subprocess.run(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
 assert not subprocess.run(['git','diff',BASE,'--',*oldfiles],cwd=ROOT,capture_output=True,check=True).stdout
 paths=[p for d in ('tests/recovery_r13','tools/recovery_r13','reports/recovery_r13') for p in sorted((ROOT/d).glob('*')) if p.is_file() and p.name!='provenance.json']
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; no original instruction changes; serial fixtures only','native_cases':40,'normal_process_exits':sum(x['exit']==0 for x in r['cases']),'expected_fault_exits':sum(x['exit']==88 for x in r['cases']),'r12_cases_reparsed':len(old['cases']),'all_preexisting_paths_unchanged':True,'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}},indent=2)+'\n')
 print('PASS:40 R13 cases;52 R12 archive records; all preexisting paths unchanged')
if __name__=='__main__':main()
