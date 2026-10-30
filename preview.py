#!/usr/bin/env python3
"""Render a specimen PNG of the built font (needs Pillow)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
path = ROOT / "fonts" / "BeehiveDeseretMono-Regular.ttf"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "specimen.png"
big = ImageFont.truetype(str(path), 96)
cell = 100

rows = [
    [chr(c) for c in range(0x10400, 0x10414)],
    [chr(c) for c in range(0x10414, 0x10428)],
    list("0123456789") + list(".,:;-'\"!?()/"),
    [chr(c) for c in range(0xE000, 0xE007)],
    [chr(c) for c in range(0x10400, 0x10414)],
]
text = "𐐜𐐲 𐐔𐐯𐑆𐐲𐑉𐐯𐐻 𐐊𐑊𐑁𐐲𐐺𐐯𐐻 1847-1869"
img = Image.new("RGB", (cell * 20 + 40, cell * 5 + 150), "#fbf6ea")
d = ImageDraw.Draw(img)
for r, row in enumerate(rows[:4]):
    for i, ch in enumerate(row):
        d.text((20 + i * cell, 10 + r * cell), ch, font=big, fill="#2a1f10")
d.text((20, 10 + 4 * cell + 10), text, font=big, fill="#7a4b12")
img.save(out)
print(out)
