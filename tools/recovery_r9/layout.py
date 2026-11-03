#!/usr/bin/env python3
"""Read ARM ELF .rodata size constants, independent of host pointer sizes."""
import json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 build=ROOT/'build/recovery_r9';out=ROOT/'reports/recovery_r9';obj=build/'layout.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=arm926ej-s','-marm','-O2','-ffreestanding','-Isrc','-c','tests/recovery_r9/layout.c','-o',str(obj)],cwd=ROOT,check=True)
 data=obj.read_bytes();assert data[:5]==b'\x7fELF\x01' and data[5]==1
 offset=struct.unpack_from('<I',data,32)[0];entry,n,strings=struct.unpack_from('<HHH',data,46)
 sections=[struct.unpack_from('<10I',data,offset+i*entry) for i in range(n)]
 names_section=sections[strings];names=data[names_section[4]:names_section[4]+names_section[5]]
 values=None
 for sec in sections:
  name=names[sec[0]:].split(b'\0',1)[0]
  if name==b'.rodata':values=struct.unpack('<6I',data[sec[4]:sec[4]+sec[5]])
 assert values is not None and values[2:]==(24,2072,3096,1028)
 labels=['existing_md15_bridge','existing_lcd_source_mux','candidate_phase_metadata','candidate_double_images_and_metadata','candidate_triple_images_and_metadata','candidate_epoch_snapshot']
 (out/'arm_layout_costs.json').write_text(json.dumps({'target':'arm-none-eabi ARM926 ARM mode, 32-bit pointers','sizes_bytes':dict(zip(labels,values)),'scope':'layout cost only, not allocated instrument RAM or production interfaces'},indent=2)+'\n')
 print(dict(zip(labels,values)))
if __name__=='__main__':main()
