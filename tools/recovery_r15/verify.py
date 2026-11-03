#!/usr/bin/env python3
"""Standalone raw archive and contract oracles; no runner/queue imports."""
import gzip,hashlib,json,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='81d6dcbe84d9d75ca817633c8d035b827a9409ad'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'reports/recovery_r15';r=json.loads((out/'results.json').read_text());assert len(r['cases'])==58
 executions={0:[1],1:[1],2:[1,2,3],3:[1,2,3,4],4:[1],6:[1],21:[2],22:[1],24:[1]}
 totals={0:1,1:1,2:3,3:4,4:1,6:1,7:1,21:2,22:1,24:1,25:1}
 metadata={18:(0,1,1,0),0:(0,0,1,1),1:(0,0,1,1),2:(0,0,3,0),3:(1,0,4,1),4:(2,0,1,1),5:(1,0,1,1),6:(1,1,1,1),7:(0,1,1,1),8:(1,0,0,0),21:(0,0,2,2),22:(0,0,1,1),23:(0,1,1,0),24:(0,0,1,1),25:(0,0,1,1),26:(0,0,1,0)} # refused,close,last_id,head
 old=bytes([0x11])*1024;fresh=bytes([0xee])*1024
 for vi in range(2):
  for case in range(29):
   row=r['cases'][vi*29+case];assert (row['vsb'],row['case'])==(vi,case)
   raw=gzip.decompress((out/f'{vi}_{case}.records.gz').read_bytes());assert raw and len(raw)%2112==0;events=[];st={}
   for n in range(0,len(raw),2112):
    h=list(struct.unpack_from('<16I',raw,n));assert h[:2]==[0x52394c43,400+case] and h[5]==len(events) and h[6]==0x39 and h[2]!=99
    src=raw[n+64:n+1088];shadow=raw[n+1088:n+2112];e=dict(header=h,source_sha256=sha(src),shadow_sha256=sha(shadow));events.append(e);st[h[2]]=(h,src,shadow)
   assert events==row['events'] and events[0]['header'][2:5]==[0,128,20]
   fault=case in (17,18);assert row['exit']==(88 if fault else 0)
   stage=89 if fault else 20
   phase=4 if case in (18,23,26) else 0
   count=1 if case in (18,23,26) else 0
   active=count;executed=1 if count else totals.get(case,0);completed=0 if count else executed
   assert st[stage][0][3:5]==[phase,(count<<24)|(active<<20)|(executed<<12)|completed],(vi,case,'gate/queue')
   depth=1 if case in (17,18,19,26) else 0
   life=(1<<20 if case in (12,20,27) else (0x101000 if case==14 else (1<<24 if case==13 else 0)))
   assert st[stage+100][0][3:5]==[depth,life],(vi,case,'lifetime')
   refused,close,last,head=metadata.get(case,(0,0,0,0));meta=(close<<31)|(refused<<24)|(last<<8)|head
   assert st[stage+200][0][4]==meta,(vi,case,'terminal metadata')
   src=bytearray(old);shadow=old
   if case==1:src[:]=fresh
   if case in (10,):src[0]=0xb1
   if case in (11,27,28):src[0]=0xa1
   if case==12:src[0]=0xb1;src[1]=0xa1
   if case in (13,14,17,18,19):src[0]=0xee
   if fault:shadow=bytes(src)
   assert st[stage][1:]==(bytes(src),shadow),(vi,case,'snapshot')
   trace=gzip.decompress((out/f'{vi}_{case}.trace.gz').read_bytes())
   if fault:
    assert events[-1]['header'][2:5]==[90,0x01e260bc,11] and st[1][2]==old
    assert b'0xc002a71c:' in trace and b'0xc0016c18:' in trace
    if case==18:assert st[289][0][3]==3 and st[289][0][4]>>31==1
   else:assert 90 not in st and events[-1]['header'][2]==220 and b'0xc001613c:' not in trace
   for mark,state in ((72,3),(73,4)):
    assert [e['header'][3:5] for e in events if e['header'][2]==mark]==[[i,state] for i in executions.get(case,[])]
   assert [e['header'][3:5] for e in events if e['header'][2]==70]==[[i,0] for i in executions.get(case,[])]
   payload=[e['header'][3:5] for e in events if e['header'][2]==71]
   assert payload==[[0x12345678,0x87654321]]*(len(executions.get(case,[]))-(case==3))+([[0,0]] if case==3 else [])
   if executions.get(case):assert b'0xc003b7fc:' in trace and b'0xc0015dd0:' in trace
   if case in (0,1):assert st[201][0][3]==(1 if case==0 else 2) and st[1][0][4]==0x1000000
   if case==9:assert st[60][0][3:5]==[17,0xdeadbeef] and b'0xc003b7d4:' in trace
   if case in (10,11):assert st[60][0][3:5]==[1,0xb1 if case==10 else 0xa1]
   if case==12:assert st[62][0][3:5]==[1,0] and st[60][0][3]==2
   if case==13:assert st[101][0][3:5]==[1,1<<24] and b'0xc002de78:' in trace
   if case==14:assert st[60][0][3:5]==[1,0]
   if case==15:assert st[60][0][3:5]==[1,0xdeadbeef] and b'0xc002d5b0:' in trace
   if case==16:assert st[60][0][3:5]==[0,0] and b'0xc002a71c:' in trace
   if case==19:assert st[60][0][3:5]==[1,1] and b'0xc0000acc:' in trace
   if case==20:assert st[60][0][3:5]==[1,0]
   if case==25:assert st[1][0][4]==0x1001001 and st[201][0][3]==4
   if case==26:assert st[60][0][3:5]==[0,1] and st[61][0][3:5]==[0,0xc06a2544] and b'0xc0000a00:' in trace
   if case in (27,28):assert st[60][0][3:5]==[1,1]
   if case==28:assert b'0xc002d88c:' in trace and b'0xc002de78:' in trace
   if case in (10,11,12,13,27,28):assert b'0xc002d030:' in trace
 for case,(x,y) in enumerate(zip(r['cases'][:29],r['cases'][29:])):
  assert x['events']==y['events'] and x['exit']==y['exit']
  line=lambda vi:re.findall(rb'^0xc0[01][0-9a-f]{5}:.*$',gzip.decompress((out/f'{vi}_{case}.trace.gz').read_bytes()),re.M)
  assert line(0)==line(1)
 oldfiles=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines();assert not subprocess.check_output(['git','diff',BASE,'--',*oldfiles],cwd=ROOT)
 prior=json.loads((ROOT/'reports/recovery_r14/provenance.json').read_text())
 for n,h in prior['sha256'].items():assert sha((ROOT/n).read_bytes())==h,n
 audit=json.loads((out/'audit.json').read_text());assert len(audit['ranges'])==19
 model=json.loads((out/'models.json').read_text());assert model['conservation']['states']==1360 and model['conservation']['transitions']==4068 and model['conservation']['actual_return_edges']==152 and not model['cancellation_demonstrated'] and not model['native_sync_compatibility']
 message='PASS:58 R15 ARM cases;54 normal exits;4 expected GPIO faults;exact cross-VSB records/native instruction lines;FIFO/argument/ACK/generation/lifetime oracles;155 R14 manifest entries and all R1-R14 paths unchanged'
 (out/'independent_verification.log').write_text(message+'\n');print(message)
 paths=[p for d in ('tests/recovery_r15','tools/recovery_r15','reports/recovery_r15') for p in sorted((ROOT/d).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p!=out/'provenance.json']
 paths += [p for p in [ROOT/'RECOVERY_R15_RAPPORT_FR.md',ROOT/'tests/run_recovery_r15.sh',*sorted((ROOT/'documents').glob('RECOVERY_R15_*.md'))] if p.exists()]
 (out/'provenance.json').write_text(json.dumps({'base_commit':BASE,'scope':'RESEARCH_ONLY; native code RX; known scalar codec and enumerated local refs only; no hardware replies/global quiescence proof','cases':58,'normal_exits':54,'expected_faults':4,'original_vsb_sha256':r['vsb_sha256'],'sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}},indent=2)+'\n')
if __name__=='__main__':main()
