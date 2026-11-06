#!/usr/bin/env python3
"""Read-only cross-image integration entry audit; direct ARM branches only."""
import hashlib,json,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r30';BASE=0xc0000000
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
T=[0xc002814c,0xc00839f0,0xc002a71c,0xc00836e4,0xc0015dd0,0xc0015fa0,0xc006e8bc,0xc006ea10]
def scan(data):
 calls={hex(t):[] for t in T}
 for off in range(0,len(data)-3,4):
  w=struct.unpack_from('<I',data,off)[0];condition=w>>28
  if w&0x0e000000==0x0a000000 and condition!=15:
   n=w&0xffffff;n=n-(1<<24) if n&0x800000 else n
   dst=(BASE+off+8+4*n)&0xffffffff
   if dst in T:calls[hex(dst)].append({'pc':hex(BASE+off),'word':hex(w),'conditional':condition!=14,'link':bool(w&0x1000000)})
 return calls
def main():
 assert len(sys.argv)==3;images=[]
 for path,h in zip(sys.argv[1:],H):
  b=Path(path).read_bytes();assert len(b)==0x200100 and hashlib.sha256(b).hexdigest()==h;images.append(b[256:])
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
 calls=[scan(b) for b in images];assert calls[0]==calls[1]
 entries={}
 for t in T:
  spans=[b[t-BASE:t-BASE+32] for b in images];assert spans[0]==spans[1]
  entries[hex(t)]={'first_32_sha256':hashlib.sha256(spans[0]).hexdigest(),'first_instruction':hex(struct.unpack_from('<I',spans[0])[0])}
 O.mkdir(parents=True,exist_ok=True);(O/'integration-audit.json').write_text(json.dumps({'vsb_sha256':H,'entry_bytes':entries,'direct_branch_candidates':calls[0],'limits':'aligned ARM scan includes data and excludes indirect branches and Thumb'},indent=2)+'\n')
 print('PASS 8 entry spans identical on both VSB; direct ARM candidates mapped, indirect coverage unknown')
if __name__=='__main__':main()
