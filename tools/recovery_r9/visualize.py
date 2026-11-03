#!/usr/bin/env python3
"""Plot native source/shadow evidence; never display a fictional physical LCD."""
import gzip,struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/recovery_r9'
def states(case):
 raw=gzip.decompress((OUT/f'0_{case}.records.gz').read_bytes());result={}
 for pos in range(0,len(raw),2112):
  h=struct.unpack_from('<16I',raw,pos);result[h[2]]=(raw[pos+64:pos+1088],raw[pos+1088:pos+2112])
 return result
def frame(data):
 im=Image.new('L',(128,64));im.putdata([255*((data[y//8*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);return im.resize((384,192),Image.Resampling.NEAREST)
def font(size):
 p=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');return ImageFont.truetype(str(p),size) if p.exists() else ImageFont.load_default()
def panel(src,shadow,title,subtitle):
 im=Image.new('RGB',(1216,288),'#f7f6f2');d=ImageDraw.Draw(im);d.text((16,12),title,font=font(19),fill='#17212b');d.text((16,40),subtitle,font=font(13),fill='#445261')
 for x,label,data in [(16,'Source native',src),(416,'Shadow native',shadow),(816,'Différence XOR',bytes(a^b for a,b in zip(src,shadow)))]:
  d.text((x,67),label,font=font(15),fill='#17212b');im.paste(frame(data),(x,91))
 return im
src,shadow=states(14)[20]
panel(src,shadow,'R9 — une shadow peut mélanger deux versions','Copie ARM originale par pages ; changement synthétique de source après la première page. Aucun LCD physique.').save(OUT/'native_page_interleave.png')
shots=states(15);ims=[]
for stage,label in [(1,'Avant le worker'),(90,'Faute avant envoi, shadow déjà copiée'),(91,'Second appel de diagnostic, aucune différence')]:
 src,shadow=shots[stage];ims.append(panel(src,shadow,'R9 — shadow préparée ≠ transmission confirmée',label+' — QEMU, aucune réponse périphérique simulée.').convert('P'))
ims[0].save(OUT/'shadow_before_send.gif',save_all=True,append_images=ims[1:],duration=1600,loop=0)
print('PASS: two figures generated from complete native records')
