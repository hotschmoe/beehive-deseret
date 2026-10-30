#!/usr/bin/env python3
"""Build Beehive Deseret (monospace) from stroke skeletons.

skeletons.py -> thicken to polygons -> union (skia-pathops) -> Bézier fit
(curvefit.py) -> quadratic TrueType outlines -> TTF + WOFF2.
"""
import math
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from pathops import Path as PoPath

import skeletons as sk
from curvefit import fit_contour

ROOT = Path(__file__).parent
UPM = 1000
ADVANCE = 620
CU2QU_ERR = 1.0


def cw(poly):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if area < 0 else poly[::-1]


def thicken(path, w):
    """Centre-line polyline -> overlapping clockwise polygons with flat ends and mitred joins."""
    r = w / 2
    pts = [path[0]]
    for p in path[1:]:
        if math.dist(p, pts[-1]) > 1e-6:
            pts.append(p)
    if len(pts) == 1:
        x, y = pts[0]
        return [cw([(x + r * math.cos(t), y + r * math.sin(t)) for t in (math.tau * i / 24 for i in range(24))])]
    closed = len(pts) > 3 and math.dist(pts[0], pts[-1]) < 1e-4
    if closed:
        pts.pop()
    n = len(pts)
    polys = []
    last = n if closed else n - 1
    dirs = []
    for i in range(last):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        d = math.hypot(x1 - x0, y1 - y0)
        dx, dy = (x1 - x0) / d, (y1 - y0) / d
        dirs.append((dx, dy))
        nx, ny = -dy * r, dx * r
        polys.append(cw([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]))
    for i in (range(n) if closed else range(1, n - 1)):
        d1, d2 = dirs[i - 1], dirs[i % len(dirs)]
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        dot = d1[0] * d2[0] + d1[1] * d2[1]
        if abs(cross) < 1e-9 and dot > 0:
            continue
        s = -1 if cross > 0 else 1
        px, py = pts[i]
        a = (px - s * d1[1] * r, py + s * d1[0] * r)
        b = (px - s * d2[1] * r, py + s * d2[0] * r)
        poly = [(px, py), a, b]
        if 1 + dot > 0.2:
            k = 1 / (1 + dot)
            poly = [(px, py), a, (px + ((a[0] - px) + (b[0] - px)) * k, py + ((a[1] - py) + (b[1] - py)) * k), b]
        polys.append(cw(poly))
    return polys


def union_contours(polys):
    path = PoPath()
    pen = path.getPen()
    for poly in polys:
        pen.moveTo(poly[0])
        for p in poly[1:]:
            pen.lineTo(p)
        pen.closePath()
    path.simplify(fix_winding=True, keep_starting_points=False)
    rec = RecordingPen()
    path.draw(rec)
    contours, cur = [], []
    for op, args in rec.value:
        if op in ("moveTo", "lineTo"):
            cur.append(args[0])
        elif op in ("closePath", "endPath") and cur:
            contours.append(cur)
            cur = []
    return contours


def area(poly):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) / 2


def outline(paths, stroke):
    polys = [poly for p in paths for poly in thicken(p, stroke)]
    contours = union_contours(polys)
    biggest = max(contours, key=lambda c: abs(area(c)))
    if area(biggest) > 0:
        contours = [c[::-1] for c in contours]
    return contours


def bbox(contours):
    xs = [x for c in contours for x, _ in c]
    ys = [y for c in contours for _, y in c]
    return min(xs), min(ys), max(xs), max(ys)


def to_glyph(contours, dx):
    pen = TTGlyphPen(None)
    q = Cu2QuPen(pen, CU2QU_ERR, reverse_direction=False)
    for c in contours:
        c = [(x + dx, y) for x, y in c]
        start, ops = fit_contour(c)
        q.moveTo(tuple(round(v, 2) for v in start))
        for op in ops:
            if op[0] == "L":
                q.lineTo(op[1])
            else:
                q.curveTo(op[1], op[2], op[3])
        q.closePath()
    return pen.glyph()


def notdef():
    pen = TTGlyphPen(None)
    for pts in ([(100, 0), (100, 620), (500, 620), (500, 0)], [(180, 80), (420, 80), (420, 540), (180, 540)]):
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def main():
    glyphs = {".notdef": notdef(), "space": TTGlyphPen(None).glyph()}
    order = [".notdef", "space"]
    cmap = {0x20: "space", 0xA0: "space"}

    def add(name, paths, stroke):
        contours = outline(paths, stroke)
        x0, _, x1, _ = bbox(contours)
        glyphs[name] = to_glyph(contours, ADVANCE / 2 - (x0 + x1) / 2)
        order.append(name)
        if x1 - x0 > ADVANCE - 40:
            print(f"warning: {name} is {x1 - x0:.0f} wide", file=sys.stderr)

    for i, nm in enumerate(sk.DESERET_ORDER):
        add(nm, [[(x * sk.HSCALE, y) for x, y in p] for p in sk.LETTERS[nm]], sk.STROKE)
        cmap[0x10400 + i] = nm       # capital
        cmap[0x10428 + i] = nm       # lowercase shares the historical form
    for i, nm in enumerate(sk.DIGITS):
        add(nm, sk.D[nm], sk.STROKE)
        cmap[0x30 + i] = nm
    codes = {"period": ".", "comma": ",", "colon": ":", "semicolon": ";", "hyphen": "-", "quotesingle": "'",
             "quotedbl": '"', "exclam": "!", "question": "?", "parenleft": "(", "parenright": ")", "slash": "/"}
    for nm, (paths, stroke) in sk.PUNCT.items():
        add(nm, paths, stroke)
        cmap[ord(codes[nm])] = nm
    for nm, (paths, stroke) in sk.SYMBOLS.items():
        add(nm, paths, stroke)
        cmap[sk.PUA[nm]] = nm

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    glyf = fb.font["glyf"]
    hmtx = {}
    for name in order:
        g = glyf[name]
        g.recalcBounds(glyf)
        hmtx[name] = (ADVANCE if name != ".notdef" else ADVANCE, getattr(g, "xMin", 0))
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=800, descent=-240)
    fb.setupNameTable({
        "familyName": "Beehive Deseret Mono",
        "styleName": "Regular",
        "uniqueFontIdentifier": "BeehiveDeseretMono-Regular",
        "fullName": "Beehive Deseret Mono Regular",
        "psName": "BeehiveDeseretMono-Regular",
        "version": "Version 0.2",
        "licenseDescription": "Original design; licence to be decided by the author.",
    })
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-240, sTypoLineGap=0,
                usWinAscent=860, usWinDescent=260, sxHeight=620, sCapHeight=620,
                achVendID="HOTS", xAvgCharWidth=ADVANCE)
    fb.setupPost(isFixedPitch=1)
    panose = fb.font["OS/2"].panose
    panose.bFamilyType, panose.bProportion = 2, 9
    fb.font["head"].fontRevision = 0.2

    out = ROOT / "fonts"
    out.mkdir(exist_ok=True)
    fb.font.save(out / "BeehiveDeseretMono-Regular.ttf")
    fb.font.flavor = "woff2"
    fb.font.save(out / "BeehiveDeseretMono-Regular.woff2")
    print(f"built {len(order)} glyphs -> {out}")


if __name__ == "__main__":
    sys.exit(main())
