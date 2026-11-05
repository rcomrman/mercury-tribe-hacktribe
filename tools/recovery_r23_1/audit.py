#!/usr/bin/env python3
"""ARM branch and literal scan: candidates, not a code/data or CFG proof."""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=0xc0000000
HASHES=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
TARGETS=[0xc0015ab4,0xc0015dd0,0xc0015fa0]
def scan(b):
 hits={hex(t):[] for t in TARGETS};literals={hex(t):[] for t in TARGETS+[0xc031b310,0xc031b710,0xc031bb2c]};indirect=[]
 for off in range(0,len(b)-3,4):
  w=struct.unpack_from('<I',b,off)[0];pc=BASE+off;cond=w>>28
  if (w&0x0e000000)==0x0a000000 and cond!=15:
   imm=w&0xffffff;imm=imm-(1<<24) if imm&0x800000 else imm
   dest=(pc+8+imm*4)&0xffffffff
   if dest in TARGETS:hits[hex(dest)].append({'pc':hex(pc),'kind':'BL' if w&0x01000000 else 'B','condition':cond,'word':hex(w)})
  if hex(w) in literals:literals[hex(w)].append(hex(pc))
  if (w&0x0ffffff0) in (0x012fff10,0x012fff30):indirect.append(pc)
 return {'branch_candidates':hits,'literal_candidates':literals,'indirect_bx_blx_candidates':len(indirect)}
def main():
 assert len(sys.argv)==3;results=[]
 for name,h in zip(sys.argv[1:],HASHES):
  raw=Path(name).read_bytes();assert len(raw)==0x200100 and hashlib.sha256(raw).hexdigest()==h
  results.append(scan(raw[256:]));assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
 out=ROOT/'reports/recovery_r23_1';out.mkdir(parents=True,exist_ok=True)
 (out/'arm-audit.json').write_text(json.dumps({'images':results,'same_scan':results[0]==results[1],'limitations':'Candidates include data, unknown Thumb and indirect destinations; no exhaustive CFG.'},indent=2)+'\n')
 for t in TARGETS:
  print(hex(t),len(results[0]['branch_candidates'][hex(t)]),'ARM B/BL candidates on VSB 0')
 print('cross-VSB scan identical:',results[0]==results[1])
if __name__=='__main__':main()
