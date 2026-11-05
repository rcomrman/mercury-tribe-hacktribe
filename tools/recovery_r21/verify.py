#!/usr/bin/env python3
"""Independent R21 evidence interpreter. It never builds or executes the prototype."""
import gzip,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r21';BASE='33ebf0884ed082dbce0065d53709cdd322042f4b'
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert len(sys.argv) in (3,4) and (len(sys.argv)==3 or sys.argv[3]=='--manifest')
 vsbs=sys.argv[1:3]
 for p,h in zip(vsbs,HASHES):assert sha(Path(p).read_bytes())==h
 audit=json.loads((OUT/'native-map.json').read_text());assert audit['vsb_sha256']==HASHES
 assert len(audit['remaining_access_domains'])==14 and len(audit['removed_from_new_route_candidates'])==10
 assert len(audit['subscriber_roots_not_required'])==3
 contracts={int(k,16):int(v,16) for k,v in audit['contracts'].items()}
 for name in vsbs:
  raw=Path(name).read_bytes()[256:]
  for pc,w in contracts.items():assert struct.unpack_from('<I',raw,pc-0xc0000000)[0]==w
 result=json.loads((OUT/'results.json').read_text());assert len(result['host_runs'])==7 and len(result['host_process_ns'])==7
 rx=re.compile(r'^PASS state=(\d+) init=(\d+) rendered=(\d+) published=(\d+) rejected=(\d+) epoch=(\d+) static=(\d+) bridge=(\d+) ui=(\d+) pool=(\d+) gate=(\d+) presets=(\d+) prolonged_frames=(\d+) prolonged_ns=(\d+) final_hash=([0-9a-f]{8}) pre_hash=([0-9a-f]{8}) mixed_hash=([0-9a-f]{8})$')
 parsed=[]
 for line in result['host_runs']:
  m=rx.match(line);assert m,line;v=list(map(int,m.groups()[:14]));assert v[:13]==[4,1,563,562,6,563,7664,4360,136,3112,24,8,512];parsed.append(v)
  assert len(set(m.groups()[14:]))==3,'full, earlier and partial-copy hashes must differ'
 assert all(n>0 for n in result['host_process_ns'])
 assert len(result['native'])==2
 for row in result['native']:
  assert row['sha256']==HASHES[row['vsb']];assert row['record'][:5]==[0x5232314e,0x21,1,1,1]
  trace=gzip.decompress((OUT/f"native-{row['vsb']}.trace.gz").read_bytes()).decode()
  for pc in ('0xc006ea10:','0xc006ea24:','0xc006ea34:','0xc006ea44:'):assert pc in trace
  for forbidden in ('0xc0070778:','0xc00705dc:','0xc00852b0:','0xc00851b4:'):assert forbidden not in trace
 assert max(x['bytes'] for x in result['stack_usage'])==1200
 src=(ROOT/'tests/recovery_r21/persistent.h').read_text()
 assert 'uint8_t image[3][1024]' in (ROOT/'tests/recovery_r12/pool.h').read_text()
 assert 'MINI_LFO_COUNT 4u' in (ROOT/'src/mini_lfo4.h').read_text() and 'global[12]' in (ROOT/'src/mercury_keys.h').read_text()
 assert 'R21_INIT=1, R21_ACTIVE=2, R21_INACTIVE=3, R21_FAULT=4' in src
 assert 'fixture_authority' in src and 'r21_publish_begin' in src
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
 for path in names:
  old=subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT);assert (ROOT/path).read_bytes()==old,('historical modification',path)
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='recovery/mercury-dust'
 print('PASS independent: fixed 7664-byte engine, 3112-byte R12 pool, four states, 7 prolonged runs.')
 print('PASS independent: 2 native VSB executions, three slot+8 calls each, no subscription/removal blocks.')
 print('PASS independent: 10 route dependencies removed, 14 access domains retained, partial publication counterexample retained.')
 print('PASS historical preservation:',len(names),'files at R20 head unchanged; VSB hashes unchanged.')
 if '--manifest' in sys.argv:
  provenance=json.loads((OUT/'provenance.json').read_text())['sha256']
  for path,h in provenance.items():assert sha((ROOT/path).read_bytes())==h,('R21 manifest',path)
  print('PASS R21 manifest:',len(provenance),'SHA-256 entries.')
if __name__=='__main__':main()
