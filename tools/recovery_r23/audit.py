#!/usr/bin/env python3
"""Read-only ARM direct-call and LCD contract audit on both original VSB."""
import hashlib,json,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r23';O.mkdir(parents=True,exist_ok=True);BASE=0xc0000000
H=['81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03','06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052']
T=[0xc0015ab4,0xc0015dd0,0xc0015fa0]
def calls(b,t):
 out=[]
 for o in range(0,len(b)-4,4):
  w=struct.unpack_from('<I',b,o)[0]
  if w>>24==0xeb:
   x=w&0xffffff;x=x-(1<<24) if x&0x800000 else x
   if (BASE+o+8+(x<<2))&0xffffffff==t:out.append(BASE+o)
 return out
def main():
 assert len(sys.argv)==3;images=[]
 for p,h in zip(sys.argv[1:],H):
  q=Path(p);raw=q.read_bytes();assert hashlib.sha256(raw).hexdigest()==h;images.append(raw[256:])
 maps=[{hex(t):[hex(x) for x in calls(b,t)] for t in T} for b in images];assert maps[0]==maps[1]
 contracts={'C0015AB4':'compares one 128-byte page and copies changed source bytes to shadow before returning changed','C0015DD0':'command dispatcher; opcode 2 marks request, opcode 3 calls worker synchronously','C0015FA0':'worker consumes descriptor/handles and reaches lower driver; completion/physical ACK not established'}
 (O/'audit.json').write_text(json.dumps({'vsb_sha256':H,'direct_callers':maps[0],'contracts':contracts,'limitations':['indirect calls are not excluded','IRQ/FIQ/DMA and computed aliases are not dominated by this scan']},indent=2)+'\n')
 print('PASS identical direct callers:',sum(map(len,maps[0].values())),'sites;',maps[0])
if __name__=='__main__':main()
