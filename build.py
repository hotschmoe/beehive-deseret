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
LIGATURES = """
lookup LIG_BLANK { sub [short_i yee short_ah] by blank.liga; } LIG_BLANK;
lookup LIG_EW { sub long_oo by ew.liga; } LIG_EW;
lookup LIG_OI { sub short_i by oi.liga; } LIG_OI;
feature calt {
    sub short_i' lookup LIG_BLANK long_oo' lookup LIG_EW;
    sub yee' lookup LIG_BLANK long_oo' lookup LIG_EW;
    sub short_ah' lookup LIG_BLANK short_i' lookup LIG_OI;
} calt;
"""
BALL = 0.72      # ball-terminal radius as a fraction of the half stroke


def cw(poly):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if area < 0 else poly[::-1]


def thicken(path, w, contrast=1.0, bar=None):
    """Centre-line polyline -> overlapping clockwise polygons, flat ends, mitred joins.

    contrast < 1 thins horizontal strokes relative to vertical ones (vertical stress,
    as in the 1860s metal type): half-width = w/2 * (contrast + (1 - contrast) * |dy|).
    """
    pts = [path[0]]
    for p in path[1:]:
        if math.dist(p, pts[-1]) > 1e-6:
            pts.append(p)
    if len(pts) == 1:
        x, y = pts[0]
        r = w / 2
        return [cw([(x + r * math.cos(t), y + r * math.sin(t)) for t in (math.tau * i / 24 for i in range(24))])]
    closed = len(pts) > 3 and math.dist(pts[0], pts[-1]) < 1e-4
    if closed:
        pts.pop()
    n = len(pts)
    last = n if closed else n - 1
    dirs, radii, polys = [], [], []
    for i in range(last):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        d = math.hypot(x1 - x0, y1 - y0)
        dx, dy = (x1 - x0) / d, (y1 - y0) / d
        c = bar if (bar is not None and d > 70) else contrast
        r = w / 2 * (c + (1 - c) * abs(dy)) * getattr(path, "fine", 1.0)
        dirs.append((dx, dy))
        radii.append(r)
        nx, ny = -dy * r, dx * r
        polys.append(cw([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]))
    for end, flag in enumerate(getattr(path, "balls", (False, False))):
        if flag and not closed:
            (px, py), (qx, qy) = (pts[0], pts[1]) if end == 0 else (pts[-1], pts[-2])
            d = math.hypot(qx - px, qy - py)
            br = w / 2 * BALL
            cx, cy = px + (qx - px) / d * br * 0.5, py + (qy - py) / d * br * 0.5
            polys.append(cw([(cx + br * math.cos(t), cy + br * math.sin(t)) for t in (math.tau * i / 24 for i in range(24))]))
    for i in (range(n) if closed else range(1, n - 1)):
        j = (i - 1) % last
        d1, d2 = dirs[j], dirs[i % last]
        r1, r2 = radii[j], radii[i % last]
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(cross) < 1e-9:
            continue
        s = -1 if cross > 0 else 1
        px, py = pts[i]
        a = (px - s * d1[1] * r1, py + s * d1[0] * r1)
        b = (px - s * d2[1] * r2, py + s * d2[0] * r2)
        poly = [(px, py), a, b]
        t = ((b[0] - a[0]) * d2[1] - (b[1] - a[1]) * d2[0]) / cross
        tip = (a[0] + d1[0] * t, a[1] + d1[1] * t)
        if abs(t) < 3 * max(r1, r2) and d1[0] * d2[0] + d1[1] * d2[1] > -0.9:
            poly = [(px, py), a, tip, b]
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


def outline(paths, stroke, contrast=1.0, bar=None):
    polys = [poly for p in paths for poly in thicken(p, stroke, contrast, bar)]
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


def letter_scale(nm):
    """Horizontal skeleton scale that gives the printed 1869 width/height (stroke weight is kept)."""
    if nm not in sk.ASPECT:
        return sk.HSCALE

    def aspect(s):
        x0, y0, x1, y1 = bbox(outline(sk.scaled(sk.LETTERS[nm], s), sk.STROKE, sk.CONTRAST, sk.BAR))
        return (x1 - x0) / (y1 - y0)

    s0, s1 = 0.7, 1.3
    a0, a1 = aspect(s0), aspect(s1)
    for _ in range(4):
        if abs(a1 - sk.ASPECT[nm]) < 0.002 or a1 == a0:
            break
        s = s0 + (sk.ASPECT[nm] - a0) * (s1 - s0) / (a1 - a0)
        s0, a0, s1, a1 = s1, a1, s, aspect(s)
    return s1


def main():
    glyphs = {".notdef": notdef(), "space": TTGlyphPen(None).glyph()}
    order = [".notdef", "space"]
    shapes = {}
    cmap = {0x20: "space", 0xA0: "space"}

    def add(name, paths, stroke, contrast=1.0, bar=None, fit_height=False):
        contours = outline(paths, stroke, contrast, bar)
        if fit_height:
            _, y0, _, y1 = bbox(contours)
            k = sk.T / (y1 - y0)
            contours = [[(x, (y - y0) * k) for x, y in c] for c in contours]
        x0, _, x1, _ = bbox(contours)
        shapes[name] = (contours, (x0 + x1) / 2)
        glyphs[name] = to_glyph(contours, ADVANCE / 2 - (x0 + x1) / 2)
        order.append(name)
        if x1 - x0 > ADVANCE - 40:
            print(f"warning: {name} is {x1 - x0:.0f} wide", file=sys.stderr)

    for i, nm in enumerate(sk.DESERET_ORDER):
        add(nm, sk.scaled(sk.LETTERS[nm], letter_scale(nm)), sk.STROKE, sk.CONTRAST, sk.BAR, True)
        cmap[0x10400 + i] = nm       # capital
        cmap[0x10428 + i] = nm       # lowercase shares the historical form
    for i, nm in enumerate(sk.DIGITS):
        add(nm, sk.D[nm], sk.STROKE, sk.CONTRAST, sk.BAR, True)
        cmap[0x30 + i] = nm
    codes = {"period": ".", "comma": ",", "colon": ":", "semicolon": ";", "hyphen": "-", "quotesingle": "'",
             "quotedbl": '"', "exclam": "!", "question": "?", "parenleft": "(", "parenright": ")", "slash": "/"}
    for nm, (paths, stroke) in sk.PUNCT.items():
        add(nm, paths, stroke)
        cmap[ord(codes[nm])] = nm
    for nm, (paths, stroke) in sk.SYMBOLS.items():
        add(nm, paths, stroke)
        cmap[sk.PUA[nm]] = nm

    glyphs["blank.liga"] = TTGlyphPen(None).glyph()
    order.append("blank.liga")
    for nm in ("ew", "oi"):
        contours, cx = shapes[nm]
        glyphs[nm + ".liga"] = to_glyph(contours, -cx)
        order.append(nm + ".liga")

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
        "version": "Version 0.5",
        "copyright": "Copyright 2026 hotschmoe. Original design.",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-240, sTypoLineGap=0,
                usWinAscent=860, usWinDescent=260, sxHeight=620, sCapHeight=620,
                achVendID="HOTS", xAvgCharWidth=ADVANCE)
    fb.setupPost(isFixedPitch=1)
    fb.addOpenTypeFeatures(LIGATURES)
    panose = fb.font["OS/2"].panose
    panose.bFamilyType, panose.bProportion = 2, 9
    fb.font["head"].fontRevision = 0.5

    out = ROOT / "fonts"
    out.mkdir(exist_ok=True)
    fb.font.save(out / "BeehiveDeseretMono-Regular.ttf")
    fb.font.flavor = "woff2"
    fb.font.save(out / "BeehiveDeseretMono-Regular.woff2")
    site = ROOT / "docs" / "fonts"
    site.mkdir(parents=True, exist_ok=True)
    for ext in ("ttf", "woff2"):
        (site / f"BeehiveDeseretMono-Regular.{ext}").write_bytes((out / f"BeehiveDeseretMono-Regular.{ext}").read_bytes())
    print(f"built {len(order)} glyphs -> {out}")


if __name__ == "__main__":
    sys.exit(main())
