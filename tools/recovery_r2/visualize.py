#!/usr/bin/env python3
"""Build an explanatory panel from verified ARM records, no fabricated pixels."""
import gzip,struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'reports/recovery_r2'
def snapshots(name):
 b=gzip.decompress((out/'traces'/name).read_bytes());p=0;shots={}
 while p<len(b):
  r=struct.unpack_from('<16I',b,p);p+=64
  if r[1]==100:shots[r[3]]=b[p:p+1024];p+=1024
 return shots
native=snapshots('0_1_native_page.records.gz');mixed=snapshots('0_12_native_heap_mercury.records.gz')
canvas=Image.new('RGB',(1056,632),'#181b21');draw=ImageDraw.Draw(canvas)
try:font=ImageFont.truetype('DejaVuSans.ttf',18)
except OSError:font=ImageFont.load_default()
panels=[('Page Korg native : Working…',native[1]),('Mercury appelé par le parcours Korg',mixed[131]),('Mercury masqué, redessin Korg forcé',mixed[202]),('Après destruction : effacement partiel',mixed[9])]
for i,(label,b) in enumerate(panels):
 x=8+(i%2)*528;y=8+(i//2)*312
 draw.text((x,y),label,font=font,fill='white')
 im=Image.new('1',(128,64));im.putdata([255*((b[(yy//8)*128+xx]>>(yy%8))&1) for yy in range(64) for xx in range(128)])
 canvas.paste(im.resize((512,256)),(x,y+36))
canvas.save(out/'lifecycle_panel.png')
