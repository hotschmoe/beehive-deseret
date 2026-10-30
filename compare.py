#!/usr/bin/env python3
"""Side-by-side proof: Beehive (left of each pair) vs any reference Deseret TTF.

    python3 compare.py REFERENCE.ttf OUT.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
mine = ImageFont.truetype(str(ROOT / "fonts" / "BeehiveDeseretMono-Regular.ttf"), 120)
ref = ImageFont.truetype(sys.argv[1], 120)
label = ImageFont.load_default(14)
names = ("LongI LongE LongA LongAH LongO LongOO ShI ShE ShA ShAH ShO ShOO Ay Ow Wu Yee H Pee Bee Tee Dee Chee Jee Kay "
         "Gay Ef Vee Eth Thee Es Zee Esh Zhee Er El Em En Eng Oi Ew").split()
cols, cw_, ch = 5, 300, 190
img = Image.new("RGB", (cols * cw_, 8 * ch), "white")
d = ImageDraw.Draw(img)
for i in range(40):
    x, y = (i % cols) * cw_ + 10, (i // cols) * ch + 5
    d.rectangle([x - 5, y, x + cw_ - 15, y + ch - 10], outline="#ddd")
    d.text((x, y), chr(0x10400 + i), font=mine, fill="black")
    d.text((x + 140, y), chr(0x10400 + i), font=ref, fill="#c33")
    d.text((x, y + ch - 32), f"{i} {names[i]}", font=label, fill="#555")
img.save(sys.argv[2])
