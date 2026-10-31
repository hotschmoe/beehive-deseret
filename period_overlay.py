#!/usr/bin/env python3
"""Detail sheets: 1869 chart letter | Beehive | overlay (chart red, Beehive blue), large.

    python3 period_overlay.py bookofmormdeseretalpha00.pdf OUTDIR [first last]

Writes OUTDIR/overlay_N.png with 8 letters per sheet.
"""
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
import skeletons as sk

NAMES = sk.DESERET_ORDER[:]
NAMES.remove("oi")
NAMES.remove("ew")
ZOOM = 3
PER = 8

pdf, outdir = sys.argv[1], Path(sys.argv[2])
outdir.mkdir(parents=True, exist_ok=True)
page = fitz.open(pdf)[1].get_pixmap(dpi=500)
gray = np.array(Image.frombytes("RGB", (page.width, page.height), page.samples).convert("L"))
h = gray.shape[0]
dark = gray < 120


def bands(x0, x1, y0, y1, gap=10, minh=30):
    prof = dark[y0:y1, x0:x1].sum(axis=1) > 1
    res, start, last = [], None, None
    for i, v in enumerate(prof):
        if v:
            start = i if start is None else start
            last = i
        elif start is not None and i - last > gap:
            if last - start >= minh:
                res.append((start + y0, last + y0))
            start = None
    if start is not None and last - start >= minh:
        res.append((start + y0, last + y0))
    return res


def letter_box(x0, y0, y1):
    cols = dark[y0:y1, x0:x0 + 125].sum(axis=0) > 0
    xs = np.flatnonzero(cols)
    a = xs[0]
    b = a
    for x in xs:
        if x - b > 4:
            break
        b = x
    return x0 + a, x0 + b


left = bands(340, 455, int(h * .2), int(h * .93))
right = bands(1365, 1480, int(h * .17), int(h * .93))
boxes = [(340, a, b) for a, b in left] + [(1365, a, b) for a, b in right]
assert len(boxes) == len(NAMES), len(boxes)

font = ImageFont.truetype(str(ROOT / "fonts" / "BeehiveDeseretMono-Regular.ttf"), 700)
label = ImageFont.load_default(16)


def mine(ch, hh):
    tile = Image.new("L", (1400, 1400), 255)
    ImageDraw.Draw(tile).text((100, 50), ch, font=font, fill=0)
    g = tile.crop(Image.eval(tile, lambda v: 255 - v).getbbox())
    s = hh / g.height
    return g.resize((max(1, round(g.width * s)), hh), Image.LANCZOS)


lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(NAMES))
tiles = []
stats = []
for i in range(lo, hi):
    nm = NAMES[i]
    x0, a, b = boxes[i]
    xa, xb = letter_box(x0, a, b)
    ref = Image.fromarray(gray[a:b + 1, xa:xb + 1])
    hh = ref.height * ZOOM
    ref = ref.resize((ref.width * ZOOM, hh), Image.LANCZOS)
    m = mine(chr(0x10428 + sk.DESERET_ORDER.index(nm)), hh)
    w = max(ref.width, m.width) + 20
    ov = Image.new("RGB", (w, hh + 20), "white")
    rr = np.array(ref.convert("L")) < 140
    mm = np.array(m.convert("L")) < 140
    canvas = np.full((hh + 20, w, 3), 255, np.uint8)
    ox_r, ox_m = (w - ref.width) // 2, (w - m.width) // 2
    canvas[10:10 + hh, ox_r:ox_r + ref.width][rr] = (230, 40, 40)
    sub = canvas[10:10 + hh, ox_m:ox_m + m.width]
    both = mm & np.all(sub == (230, 40, 40), axis=2)
    sub[mm] = (40, 70, 230)
    sub[both] = (70, 20, 90)
    tiles.append((nm, ref, m, Image.fromarray(canvas), hh))
    inter = (rr_full := np.zeros((hh, w), bool))
    rr_full[:, ox_r:ox_r + ref.width] = rr
    mm_full = np.zeros((hh, w), bool)
    mm_full[:, ox_m:ox_m + m.width] = mm
    stats.append((nm, ref.width / hh, m.width / hh, (rr_full & mm_full).sum() / (rr_full | mm_full).sum(), mm.sum() / rr.sum()))

for s in range(0, len(tiles), PER):
    chunk = tiles[s:s + PER]
    colw = [max(t[1].width, t[2].width, t[3].width) for t in chunk]
    rowh = max(t[4] for t in chunk) + 50
    cw3 = max(t[1].width + t[2].width + t[3].width for t in chunk) + 80
    sheet = Image.new("RGB", (cw3 * 2, rowh * ((len(chunk) + 1) // 2)), "white")
    d = ImageDraw.Draw(sheet)
    for k, (nm, ref, m, ov, hh) in enumerate(chunk):
        x, y = (k % 2) * cw3, (k // 2) * rowh
        d.text((x + 6, y + 4), nm, fill=(150, 30, 30), font=label)
        sheet.paste(ref.convert("RGB"), (x + 10, y + 28))
        sheet.paste(m.convert("RGB"), (x + 10 + ref.width + 30, y + 28))
        sheet.paste(ov, (x + 10 + ref.width + m.width + 60, y + 18))
    p = outdir / f"overlay_{s // PER + (lo // PER)}.png"
    sheet.save(p)
    print(p)

print(f"{'letter':9} {'ref w/h':>8} {'mine w/h':>9} {'IoU':>6} {'ink ratio':>9}")
for nm, ra, ma, iou, ink in stats:
    print(f"{nm:9} {ra:8.2f} {ma:9.2f} {iou:6.2f} {ink:9.2f}")
print(f"mean IoU {np.mean([s[3] for s in stats]):.3f}")
