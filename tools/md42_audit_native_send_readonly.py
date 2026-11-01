#!/usr/bin/env python3
"""Read-only evidence: Korg native LCD sender does not propagate low-level
readiness result at its 0xC00160C4 command bridge. ARM opcode checks only;
this does NOT determine whether SPI/DMA really finished on hardware."""
import hashlib,json,struct,sys
from pathlib import Path
BASE=0xC0000000; HEADER=0x100; SIZE=0x200000
HASHES={'81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03',
        '06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052'}
def word(img,a):return struct.unpack_from('<I',img,a-BASE)[0]
def branch_target(addr, op):
 if (op>>25)&7 != 5:return None
 x=op & 0xffffff
 if x & (1<<23):x-=(1<<24)
 return (addr+8+(x<<2))&0xffffffff
def examine(path):
 data=path.read_bytes();sha=hashlib.sha256(data).hexdigest()
 if len(data)!=HEADER+SIZE or sha not in HASHES:raise ValueError('unexpected VSB size/hash: '+path.name)
 img=data[HEADER:]
 checks={
  'LCD page comparator invoked at C0016084':branch_target(0xC0016084,word(img,0xC0016084))==0xC0015AB4,
  'dirty result branches around sender at C0016090':word(img,0xC0016090)==0x0A000003,
  'page send helper called at C00160A0':branch_target(0xC00160A0,word(img,0xC00160A0))==0xC001613C,
  'page helper calls command writer at C001617C':branch_target(0xC001617C,word(img,0xC001617C))==0xC00160C4,
  'command writer calls low-level I/O at C00160F4':branch_target(0xC00160F4,word(img,0xC00160F4))==0xC00183CC,
  'command writer returns without checking I/O result':word(img,0xC00160F8)==0xE24BD004 and word(img,0xC00160FC)==0xE8BD8800,
  'low-level I/O has bounded 1000-count loop':word(img,0xC0018468)==0xE3A03FFA,
  'low-level I/O returns status from local byte':word(img,0xC0018508)==0xE55B3009 and word(img,0xC001850C)==0xE1A00003,
 }
 if not all(checks.values()):raise AssertionError([k for k,v in checks.items() if not v])
 return {'name':path.name,'sha256':sha,'checks':checks,'passed':len(checks),
         'native_sender_io_status_propagated':False,'hardware_tx_complete_proven':False}
if __name__=='__main__':
 if len(sys.argv)!=3:sys.exit('usage: script user_custom.VSB user_backup.VSB')
 a,b=map(lambda s:examine(Path(s)),sys.argv[1:]);print(json.dumps({'evidence':'read-only opcode audit; NOT a SPI oscilloscope trace','firmwares':[a,b]},indent=2))
