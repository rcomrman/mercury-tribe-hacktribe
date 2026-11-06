#!/usr/bin/env python3
"""Independent evidence audit, including historic preservation and R29 streams."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r30';BASE='62a79b8c3bb74a649d1bf7766dcbc1311122363f'
def main():
 assert len(sys.argv)==3;a=json.loads((O/'integration-audit.json').read_text())
 for name,h in zip(sys.argv[1:],a['vsb_sha256']):
  b=Path(name).read_bytes();assert hashlib.sha256(b).hexdigest()==h;image=b[256:]
  for t,row in a['entry_bytes'].items():
   pos=int(t,16)-0xc0000000;assert hashlib.sha256(image[pos:pos+32]).hexdigest()==row['first_32_sha256']
  for dest,sites in a['direct_branch_candidates'].items():
   for s in sites:
    pc=int(s['pc'],16);w=struct.unpack_from('<I',image,pc-0xc0000000)[0];assert hex(w)==s['word']
    n=w&0xffffff;n=n-(1<<24) if n&0x800000 else n;assert (pc+8+4*n)&0xffffffff==int(dest,16)
 subprocess.run([sys.executable,str(R/'tools/recovery_r29/verify.py')],check=True)
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=R,text=True).splitlines()
 for path in names:
  old=subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=R);assert (R/path).read_bytes()==old,path
 assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='recovery/mercury-dust'
 print('PASS R30 ARM entry and branch bytes; R29 evidence; preserved',len(names),'files at R29 head')
if __name__=='__main__':main()
