#!/usr/bin/env python3
"""Compare host V30 reference with ARM comparator shadow, not transmitted pixels."""
import gzip
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r25'
frames=(R/'build/recovery_r25/frames.bin').read_bytes()
sheet=Image.new('RGB',(512,8*84),'#eeeeee');d=ImageDraw.Draw(sheet)
def image(buf):
 im=Image.new('1',(128,64));im.putdata([255*((buf[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);return im.convert('RGB')
for s in range(8):
 rec=gzip.decompress((O/f'0_{s}_0.records.gz').read_bytes())[-2112:];reference=frames[s*4096:s*4096+1024];shadow=rec[1088:2112]
 assert reference==shadow
 sheet.paste(image(reference),(0,s*84+18));sheet.paste(image(shadow),(256,s*84+18))
 d.text((0,s*84),f'Preset {s}: V30',fill='black');d.text((256,s*84),'Shadow ARM, pas transmission',fill='black')
sheet.save(O/'comparaison_v30_shadow.png')
print('PASS visual comparison: V30 reference and ARM shadow, 8 presets')
