#!/usr/bin/env python3
"""Read ARM32 layout constants, reusing the R9 ELF section parsing method."""
import json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 obj=ROOT/'build/recovery_r12/layout.o';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-Isrc','-c','tests/recovery_r12/layout.c','-o',str(obj)],cwd=ROOT,check=True)
 b=obj.read_bytes();assert b[:6]==b'\x7fELF\x01\x01';off=struct.unpack_from('<I',b,32)[0];entry,n,strings=struct.unpack_from('<HHH',b,46);secs=[struct.unpack_from('<10I',b,off+i*entry) for i in range(n)];ns=secs[strings];names=b[ns[4]:ns[4]+ns[5]]
 for sec in secs:
  if names[sec[0]:].split(b'\0',1)[0]==b'.rodata':values=struct.unpack('<7I',b[sec[4]:sec[4]+sec[5]])
 assert values==(40,8,2088,3112,1040,4348,1060),values
 labels=['candidate_metadata','handle','double_layout','triple_pool','candidate_staging_copy','existing_md15_bridge','existing_mux']
 (ROOT/'reports/recovery_r12/arm_layout.json').write_text(json.dumps({'target':'ARM926 ARM32','sizes_bytes':dict(zip(labels,values)),'r9_comparison':{'metadata':24,'double':2072,'triple':3096},'extra_r12_metadata_bytes':16,'limits':'Double is a separately measured two-image layout; native test pool always physically holds three images even in logical double mode. No free RAM, stack margin, IRQ latency or cache costs proved. Existing bridge already includes mux and two images; not additive.'},indent=2)+'\n');print(dict(zip(labels,values)))
if __name__=='__main__':main()
