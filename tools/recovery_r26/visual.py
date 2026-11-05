#!/usr/bin/env python3
import gzip
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'reports/recovery_r26';frames=(O/'arm-frames.bin').read_bytes()
sheet=Image.new('RGB',(512,672),'white');d=ImageDraw.Draw(sheet)
def img(buf):
 im=Image.new('1',(128,64));im.putdata([255*((buf[(y//8)*128+x]>>(y%8))&1) for y in range(64) for x in range(128)]);return im.convert('RGB')
for s in range(8):
 r=gzip.decompress((O/f'0_{s}.records.gz').read_bytes())[2112:4224];a=frames[s*4096:s*4096+1024];b=r[1088:2112];assert a==b
 sheet.paste(img(a),(0,s*84+18));sheet.paste(img(b),(256,s*84+18));d.text((0,s*84),f'V30 ARM preset {s}',fill='black');d.text((256,s*84),'Shadow ARM Korg',fill='black')
sheet.save(O/'comparaison_arm_shadow.png')
