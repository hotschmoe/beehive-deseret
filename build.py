#!/usr/bin/env python3
"""Beehive Deseret: an original geometric font for the Deseret Alphabet.

Every glyph is a skeleton of centre-line strokes (see GLYPH SKELETONS). The
build thickens the strokes into outlines, removes overlaps and writes
TTF + WOFF2.

Design rules (also in README.md):
  * Consonants hang from a vertical stem. Each voiceless/voiced pair shares one
    feature; the voiced letter adds a foot bar on the baseline.
  * Vowels are stemless open shapes. Long vowels are tall, short vowels are
    the same shape at about half the height.
  * Lowercase (U+10428..1044F) is the capital shape scaled down and lightened.
"""
import math
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.removeOverlaps import removeOverlaps

ROOT = Path(__file__).parent
UPM = 1000
CAP_STROKE = 78
LOWER_STROKE = 66
LOWER_SCALE = 0.78
SIDE_BEARING = 62
STEP_DEG = 7.5


def arc(cx, cy, rx, ry, a0, a1):
    n = max(2, int(abs(a1 - a0) / STEP_DEG))
    return [
        (cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
         cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
        for i in range(n + 1)
    ]


def ring(cx, cy, rx, ry):
    return arc(cx, cy, rx, ry, 90, 450)


def cw(poly):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if area < 0 else poly[::-1]


def thicken(path, w):
    """Polyline -> overlapping clockwise polygons (quads + round joints)."""
    r = w / 2
    polys = []
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        dx, dy = x1 - x0, y1 - y0
        d = math.hypot(dx, dy)
        if d == 0:
            continue
        nx, ny = -dy / d * r, dx / d * r
        polys.append(cw([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]))
    for x, y in path:
        polys.append(cw([(x + r * math.cos(t), y + r * math.sin(t))
                         for t in (math.tau * i / 20 for i in range(20))]))
    return polys


# ---------------------------------------------------------------- GLYPH SKELETONS
# Coordinates are for capitals, baseline y=0, cap height 700, centred on x=0.

CAP = 700
FOOT = [(-150, 0), (150, 0)]


def stem(top=CAP, bottom=0):
    return [(0, bottom), (0, top)]


# Consonant features hung from the stem. Each (voiceless, voiced) pair shares one.
CONSONANT_FEATURES = {
    "pee":  [[(0, CAP), (110, CAP)] + arc(110, 540, 160, 160, 90, -90) + [(0, 380)]],
    "tee":  [[(-170, CAP), (170, CAP)]],
    "chee": [[(0, CAP), (240, CAP), (240, 470)]],
    "kay":  [[(250, 680), (0, 340), (250, 0)]],
    "ef":   [[(0, 200), (260, CAP)]],
    "eth":  [ring(235, 570, 105, 105)],
    "es":   [[(0, 350), (260, 350)]],
    "esh":  [[(0, 650), (110, CAP)] + arc(120, 550, 150, 150, 90, 0) + [(270, 380)]],
}

PAIRS = [  # (voiceless name, voiced name, feature)
    ("pee", "bee", "pee"), ("tee", "dee", "tee"), ("chee", "jee", "chee"),
    ("kay", "gay", "kay"), ("ef", "vee", "ef"), ("eth", "thee", "eth"),
    ("es", "zee", "es"), ("esh", "zhee", "esh"),
]


def vowel_shapes(rx, h):
    ry = h / 2
    return {
        "i":  [ring(0, ry, rx, ry)],
        "e":  [arc(0, ry, rx, ry, 52, 308)],
        "a":  [arc(0, ry, rx, ry, 128, -128)],
        "ah": [[(-rx, 0), (-rx, h - rx)] + arc(0, h - rx, rx, rx, 180, 0) + [(rx, 0)]],
        "o":  [[(-rx, h), (-rx, rx)] + arc(0, rx, rx, rx, 180, 360) + [(rx, h)]],
        "oo": [[(-rx, 0), (0, h), (rx, 0)]],
    }


LONG_RX, LONG_H = 250, 660
SHORT_RX, SHORT_H = 175, 360


def skeletons():
    """name -> list of centre-line polylines (capital form)."""
    g = {}
    longs = vowel_shapes(LONG_RX, LONG_H)
    shorts = vowel_shapes(SHORT_RX, SHORT_H)
    for key, nm in zip(["i", "e", "a", "ah", "o", "oo"],
                       ["long_i", "long_e", "long_a", "long_ah", "long_o", "long_oo"]):
        g[nm] = longs[key]
    for key, nm in zip(["i", "e", "a", "ah", "o", "oo"],
                       ["short_i", "short_e", "short_a", "short_ah", "short_o", "short_oo"]):
        g[nm] = shorts[key]
    a_long, ah_long = longs["a"], longs["ah"]
    g["ay"] = a_long + [[(-LONG_RX, 0), (LONG_RX, 0)]]
    g["ow"] = ah_long + [[(0, 0), (0, LONG_H - LONG_RX)]]
    g["wu"] = [[(-270, 520), (-135, 0), (0, 360), (135, 0), (270, 520)]]
    g["yee"] = [[(-210, 560), (0, 100), (210, 560)], [(0, 100), (-90, -210)]]
    g["h"] = [stem_at(-165), stem_at(165), [(-165, 350), (165, 350)]]

    for vl, vd, feat in PAIRS:
        g[vl] = [stem()] + CONSONANT_FEATURES[feat]
        g[vd] = [stem()] + CONSONANT_FEATURES[feat] + [FOOT]

    g["er"] = [stem(), [(0, 360), (260, 0)]]
    g["el"] = [stem(), [(0, 0), (270, 0)]]
    arch = lambda x0: [(x0, 300)] + arc(x0 + 110, 300, 110, 110, 180, 0) + [(x0 + 220, 0)]
    g["en"] = [stem(), arch(0)]
    g["em"] = [stem(), arch(0), arch(220)]
    g["eng"] = [stem(CAP, -220), arch(0)]
    g["oi"] = [[(-LONG_RX, LONG_H), (-LONG_RX, LONG_RX)] + arc(0, LONG_RX, LONG_RX, LONG_RX, 180, 360)
               + [(LONG_RX, LONG_H)], [(0, LONG_RX), (0, 0)]]
    g["ew"] = [ring(0, LONG_H / 2, LONG_RX, LONG_H / 2), [(0, 0), (0, LONG_H)]]
    return g


def stem_at(x):
    return [(x, 0), (x, CAP)]


NAMES = [  # Unicode order, U+10400.. (capital). Lowercase is +0x28.
    "long_i", "long_e", "long_a", "long_ah", "long_o", "long_oo",
    "short_i", "short_e", "short_a", "short_ah", "short_o", "short_oo",
    "ay", "ow", "wu", "yee", "h",
    "pee", "bee", "tee", "dee", "chee", "jee", "kay", "gay", "ef", "vee",
    "eth", "thee", "es", "zee", "esh", "zhee", "er", "el", "em", "en", "eng",
    "oi", "ew",
]
assert len(NAMES) == 40

PUNCT = {  # codepoint -> (glyph name, skeleton polylines, stroke)
    ord("."): ("period", [ring(0, 40, 6, 6)], 100),
    ord(","): ("comma", [[(0, 40), (-30, -130)]], 100),
    ord("-"): ("hyphen", [[(-120, 300), (120, 300)]], CAP_STROKE),
    ord(":"): ("colon", [ring(0, 40, 6, 6), ring(0, 430, 6, 6)], 100),
    ord("'"): ("quotesingle", [[(0, 700), (-14, 520)]], 90),
    ord("!"): ("exclam", [[(0, 700), (0, 190)], ring(0, 30, 6, 6)], 90),
    ord("?"): ("question", [arc(0, 520, 190, 180, 160, -80) + [(0, 250), (0, 190)], ring(0, 30, 6, 6)], 84),
}


def scaled(paths, s):
    return [[(x * s, y * s) for x, y in p] for p in paths]


def build_outline(paths, stroke):
    polys = [poly for p in paths for poly in thicken(p, stroke)]
    xs = [x for poly in polys for x, _ in poly]
    dx = SIDE_BEARING - min(xs)
    polys = [[(x + dx, y) for x, y in poly] for poly in polys]
    adv = round(max(xs) - min(xs) + 2 * SIDE_BEARING)
    return polys, adv


def to_glyph(polys):
    pen = TTGlyphPen(None)
    for poly in polys:
        pts = [(round(x), round(y)) for x, y in poly]
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def notdef():
    pen = TTGlyphPen(None)
    for outer, pts in ((True, [(80, 0), (80, 700), (460, 700), (460, 0)]),
                       (False, [(150, 70), (390, 70), (390, 630), (150, 630)])):
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def main():
    sk = skeletons()
    glyphs, metrics, cmap = {}, {}, {}
    order = [".notdef", "space"]
    glyphs[".notdef"] = notdef()
    metrics[".notdef"] = (540, 80)
    empty = TTGlyphPen(None).glyph()
    glyphs["space"], metrics["space"], cmap[0x20] = empty, (300, 0), "space"

    def add(name, code, paths, stroke):
        polys, adv = build_outline(paths, stroke)
        glyphs[name] = to_glyph(polys)
        metrics[name] = (adv, 0)
        order.append(name)
        if code is not None:
            cmap[code] = name

    for i, nm in enumerate(NAMES):
        add(nm, 0x10400 + i, sk[nm], CAP_STROKE)
    for i, nm in enumerate(NAMES):
        add(nm + ".lc", 0x10428 + i, scaled(sk[nm], LOWER_SCALE), LOWER_STROKE)
    for code, (nm, paths, stroke) in PUNCT.items():
        add(nm, code, paths, stroke)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    # lsb must equal glyph xMin; recompute from the built glyf table.
    glyf = fb.font["glyf"]
    hmtx = {}
    for name in order:
        g = glyf[name]
        g.recalcBounds(glyf)
        hmtx[name] = (metrics[name][0], getattr(g, "xMin", 0))
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=820, descent=-260)
    fb.setupNameTable({
        "familyName": "Beehive Deseret",
        "styleName": "Regular",
        "uniqueFontIdentifier": "BeehiveDeseret-Regular",
        "fullName": "Beehive Deseret Regular",
        "psName": "BeehiveDeseret-Regular",
        "version": "Version 0.1",
        "licenseDescription": "Original design; licence to be decided by the author.",
    })
    fb.setupOS2(sTypoAscender=820, sTypoDescender=-260, sTypoLineGap=0,
                usWinAscent=900, usWinDescent=300, sxHeight=360, sCapHeight=700,
                achVendID="HOTS")
    fb.setupPost()
    removeOverlaps(fb.font)

    out = ROOT / "fonts"
    out.mkdir(exist_ok=True)
    fb.font.save(out / "BeehiveDeseret-Regular.ttf")
    fb.font.flavor = "woff2"
    fb.font.save(out / "BeehiveDeseret-Regular.woff2")
    print(f"built {len(order)} glyphs -> {out}")


if __name__ == "__main__":
    sys.exit(main())
