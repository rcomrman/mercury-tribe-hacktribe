#!/usr/bin/env python3
"""Independent raw image/descriptor/registry lifetime oracles. No runner imports."""
import gzip,hashlib,json,re,struct,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='65d776f53718a1dadbeea1998c01e3a9791475df'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'reports/recovery_r16';r=json.loads((out/'results.json').read_text());assert len(r['cases'])==68
 serial=[1,0,1,1,1,0,1,1,1,2,3,1,2,2,2,0,1,8,1,0xffffffff,0,2,2,1,2,0,1,1,0,1,1,1,0,2]
 rejections={7:1,8:3,11:1,14:1,17:1,18:1,19:1,20:1,23:1,30:1}
 retired_ui={10,12,13,15,20,23,29};retired_lcd={7,8,9,24,31}
 calls={10:2,12:1,13:1,15:1,16:1,21:1,22:1,29:1,32:1,33:1}
 old=bytes([0x11])*1024;bar=bytearray(old)
 for x in range(9,65):bar[896+x]=0x71
 for vi in range(2):
  for case in range(34):
   row=r['cases'][vi*34+case];assert (row['vsb'],row['case'])==(vi,case)
   raw=gzip.decompress((out/f'{vi}_{case}.records.gz').read_bytes());assert raw and len(raw)%2112==0;ev=[];st={}
   for n in range(0,len(raw),2112):
    h=list(struct.unpack_from('<16I',raw,n));assert h[:2]==[0x52394c43,500+case] and h[5]==len(ev) and h[6]==0x39 and h[2]!=99
    src=raw[n+64:n+1088];shadow=raw[n+1088:n+2112];ev.append(dict(header=h,source_sha256=sha(src),shadow_sha256=sha(shadow)));st[h[2]]=(h,src,shadow)
   assert ev==row['events'] and st[0][0][3:5]==[256,24] and st[50][0][3:5]==[128,3176]
   fault=case in (24,26,31);assert row['exit']==(88 if fault else 0)
   stage=89 if fault else 20
   refs0=2 if case==24 else (1 if case in (26,31) else 0)
   state0=2 if case in retired_lcd else 1;producers0=0 if case in retired_lcd else 1
   assert st[stage][0][3:5]==[state0,(producers0<<16)|refs0],(vi,case,'object0')
   gen1=2 if case in (11,14,16) else (0xffffffff if case==20 else 1)
   assert st[stage+100][0][3:5]==[1,gen1]
   assert st[stage+200][0][3:5]==[serial[case],0x1001 if case==6 else 0]
   assert st[stage+300][0][3:5]==[rejections.get(case,0),calls.get(case,0)<<16]
   quiet=(1 if case in (7,8,9) else 0)|(2 if case in retired_ui else 0)
   assert st[stage+400][0][3:5]==[quiet,0 if case in retired_ui else 0x10000]
   src=bytearray(old);shadow=old
   if case==10:src[0]=0xa2
   if case in (12,15,21,22,33):src[0]=0xa1
   if case in (13,26,29):src[0]=0xee
   if case in (16,32):src[0]=0xb1
   if case==25:src=bar
   if case==26:shadow=bytes(src)
   assert st[stage][1:]==(bytes(src),shadow),(vi,case,'image')
   trace=gzip.decompress((out/f'{vi}_{case}.trace.gz').read_bytes())
   if fault:
    assert ev[-1]['header'][2:5]==[90,0x01e260bc,11] and st[1][2]==old and b'0xc0016c18:' in trace
    if case==24:assert b'0xc0015ab4:' not in trace and st[89][0][10]==88 and st[89][0][11]&255==1
    if case==26:assert b'0xc0015ab4:' in trace and b'0xc001613c:' in trace
    if case==31:assert b'0xc00162c4:' in trace and b'0xc0015fa0:' not in trace
   else:assert 90 not in st and ev[-1]['header'][2]==420 and b'0xc001613c:' not in trace
   contrast={0:42,1:7,3:128,4:255,6:42,24:88}
   if case in contrast:
    assert st[stage][0][10]==contrast[case] and st[stage][0][11]&255==(0 if case==3 else 1)
    if case!=3:assert b'0xc0015f44:' in trace
    else:assert b'0xc0015f44:' not in trace
   if case==6:
    assert st[1][0][4]==0x10001 and st[201][0][3:5]==[1,0x1001001]
   if case==9:assert st[1][0][3:5]==[2,1] and st[401][0][3]==0
   if case==10:assert st[61][0][3:5]==[2,1]
   if case==11:assert st[101][0][4]==1 and st[401][0][4]==1 and st[201][0][4]==0x1000000
   if case==13:assert st[401][0][3:5]==[0,1] and st[301][0][4]==0x10001 and st[64][0][3:5]==[0,1]
   if case in (21,30):assert st[64][0][3:5]==[0,1]
   if case==22:assert st[64][0][3:5]==[1,2]
   for e in ev:
    if e['header'][2]==65:assert e['header'][3:5]==[0,37]
   if case==32:assert st[66][0][3:5]==[1,1]
   if case in (10,13,21,22,29,30,32,33):assert b'0xc0070778:' in trace
   if case in (10,13,21,22,29,32,33):assert b'0xc0070688:' in trace and b'0xc007061c:' in trace
   if case in (10,13,21,22,30,33):assert b'0xc00705dc:' in trace
   if case in (5,28):assert st[60][0][3:5]==[1 if case==5 else 0,0] and b'0xc0070af0:' in trace and b'0xc0083fe8:' in trace
   if case==25:assert st[60][0][3:5]==[100,100] and b'0xc006040c:' in trace and b'0xc006038c:' in trace
 for case,(a,b) in enumerate(zip(r['cases'][:34],r['cases'][34:])):
  assert a['events']==b['events'] and a['exit']==b['exit']
  lines=lambda vi:re.findall(rb'^0xc0[01][0-9a-f]{5}:.*$',gzip.decompress((out/f'{vi}_{case}.trace.gz').read_bytes()),re.M)
  assert lines(0)==lines(1)
 # Retained failures are evidence, not successful final runs.
 with tarfile.open(out/'failures/observer_abi_initial.tar.gz','r:gz') as ar:
  initial=json.loads(ar.extractfile('reports/recovery_r16/results.json').read());assert len(initial['cases'])==64
  failed=[(x['vsb'],x['case']) for x in initial['cases'] if x['exit']==161]
  assert failed==[(v,c) for v in range(2) for c in (10,13,21,22,29)]
  assert sum(x['exit']==88 for x in initial['cases'])==6
  for v,c in failed:
   raw=gzip.decompress(ar.extractfile(f'reports/recovery_r16/{v}_{c}.records.gz').read());h=struct.unpack_from('<16I',raw,len(raw)-2112);assert h[:4]==(0x52394c43,500+c,99,161)
  assert b'closure[0]=1;closure[1]' in ar.extractfile('tests/recovery_r16/native.c').read()
 diagnostic=json.loads((out/'failures/observer_abi_diagnostic.json').read_text());raw=gzip.decompress((out/'failures/observer_abi_diagnostic.records.gz').read_bytes())
 rows=[struct.unpack_from('<16I',raw,n) for n in range(0,len(raw),2112)];h=next(h for h in rows if h[2]==65)
 assert (h[3]+int(diagnostic['objA_symbol_address'],16))&0xffffffff==1 and h[4]==37 and diagnostic['observed_this']==1
 comparisons=[];previous='6356568fc4bc31e802a1b9af6fa1b173c6752a99'
 for vi in range(2):
  for case in range(34):
   stem=f'reports/recovery_r16/{vi}_{case}'
   oldraw=gzip.decompress(subprocess.check_output(['git','show',previous+':'+stem+'.records.gz'],cwd=ROOT));newraw=gzip.decompress((ROOT/(stem+'.records.gz')).read_bytes());assert oldraw==newraw
   oldtrace=gzip.decompress(subprocess.check_output(['git','show',previous+':'+stem+'.trace.gz'],cwd=ROOT));newtrace=gzip.decompress((ROOT/(stem+'.trace.gz')).read_bytes())
   native=lambda b:re.findall(rb'^0xc0[01][0-9a-f]{5}:.*$',b,re.M);assert native(oldtrace)==native(newtrace)
   comparisons.append({'vsb':vi,'case':case,'raw_records_identical':True,'native_instruction_lines_identical':True})
 (out/'replay_comparison.json').write_text(json.dumps({'previous_validated_evidence_commit':previous,'scope':'Final launcher replay versus previously published corrected R16 evidence; failed ABI archives kept separate','cases':comparisons},indent=2)+'\n')
 oldfiles=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines();assert not subprocess.check_output(['git','diff',BASE,'--',*oldfiles],cwd=ROOT)
 prior=json.loads((ROOT/'reports/recovery_r15/provenance.json').read_text())
 for n,h in prior['sha256'].items():assert sha((ROOT/n).read_bytes())==h,n
 audit=json.loads((out/'audit.json').read_text());assert len(audit['ranges'])==20
 m=json.loads((out/'models.json').read_text());assert m['registry_commands']['states']==2448 and m['registry_commands']['transitions']==6890 and not m['global_cpu_cessation_proven'] and not m['peripheral_cessation_authority_proven']
 msg='PASS:68 R16 ARM cases;62 normal exits;6 expected GPIO faults;exact cross-VSB records/native lines;typed byte/observer ABI/lease generation/owner/ACK oracles;145 R15 manifest entries and all R1-R15 paths unchanged'
 (out/'independent_verification.log').write_text(msg+'\n');print(msg)
 paths=[p for d in ('tests/recovery_r16','tools/recovery_r16','reports/recovery_r16') for p in sorted((ROOT/d).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p!=out/'provenance.json']
 paths += [p for p in [ROOT/'RECOVERY_R16_RAPPORT_FR.md',ROOT/'tests/run_recovery_r16.sh',*sorted((ROOT/'documents').glob('RECOVERY_R16_*.md'))] if p.exists()]
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; typed opt-in codec and finite externally serialized registry; no native hardware reply/global cessation/forced free','cases':68,'normal_exits':62,'expected_faults':6,'original_vsb_sha256':r['vsb_sha256'],'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}},indent=2)+'\n')
if __name__=='__main__':main()
