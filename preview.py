#!/usr/bin/env python3
"""Render a specimen PNG of the built font (needs Pillow)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
font_path = ROOT / "fonts" / "BeehiveDeseret-Regular.ttf"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "specimen.png"

big = ImageFont.truetype(str(font_path), 120)
small = ImageFont.truetype(str(font_path), 64)
caps = "".join(chr(c) for c in range(0x10400, 0x10428))
lows = "".join(chr(c) for c in range(0x10428, 0x10450))

img = Image.new("RGB", (1500, 1100), "#fbf6ea")
d = ImageDraw.Draw(img)
y = 20
for row in (caps[:14], caps[14:27], caps[27:], lows[:14], lows[14:27], lows[27:]):
    x = 30
    for ch in row:
        d.text((x, y), ch, font=big, fill="#2a1f10")
        x += big.getlength(ch) + 14
    y += 125
d.text((30, y + 10), caps[:12] + " " + lows[:12] + " .,:-'!?", font=small, fill="#7a4b12")
img.save(out)
print(out)
