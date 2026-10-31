"""Centre-line skeletons for every glyph, in font units, centred on x=0.

Deseret letters share one height (0..T) with no ascenders or descenders, as in
the 1850s originals, and are drawn with one monoline stroke. The shapes follow
the historical letterforms; the drawing is original.
"""
import math

T = 620          # outer height of every letter
STROKE = 96       # full (vertical) stroke weight
CONTRAST = 0.5    # horizontal strokes are this fraction of the vertical weight
ICON_STROKE = 66
STEP = 4.0
HSCALE = 1.1     # letters are drawn 10% wider than their skeleton, as in the originals


def arc(cx, cy, rx, ry, a0, a1):
    n = max(2, int(abs(a1 - a0) / STEP))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def ell(cx, cy, rx, ry):
    return arc(cx, cy, rx, ry, 0, 360)


def roundrect(cx, cy, hw, hh, r):
    pts = [(cx + hw, cy - hh + r), (cx + hw, cy + hh - r)]
    for ax, ay, a0 in ((cx + hw - r, cy + hh - r, 0), (cx - hw + r, cy + hh - r, 90),
                       (cx - hw + r, cy - hh + r, 180), (cx + hw - r, cy - hh + r, 270)):
        pts += arc(ax, ay, r, r, a0, a0 + 90)
    return pts + [pts[0]]


def stem(x, y0=0, y1=T):
    return [(x, y0), (x, y1)]


LETTERS = {}
L = LETTERS

L["long_i"] = [ell(0, 200, 150, 160), [(150, 200), (150, 360)] + arc(0, 360, 150, 220, 0, 140)]
L["long_e"] = [arc(0, 445, 140, 135, 25, 270) + arc(0, 175, 150, 135, 90, 335)[1:],
               [(0, 310), (55, 310)]]
L["long_a"] = [ell(0, 185, 150, 145), arc(0, 445, 125, 135, 235, 550)]
L["long_ah"] = [ell(0, 310, 165, 270), [(0, 580), (0, 340)]]
L["long_o"] = [ell(0, 310, 185, 270)]
L["long_oo"] = [ell(0, 310, 185, 270), stem(0)]

L["short_i"] = [stem(0), [(-180, 430), (180, 210)]]
L["short_e"] = [stem(120), arc(-10, 170, 130, 130, -30, -160)]
L["short_a"] = [stem(170), [(-200, 250), (170, 40)]]
L["short_ah"] = [stem(190), [(190, 40), (75, 205), (-10, 40), (-195, 215)]]
L["short_o"] = [stem(-170), arc(0, 560, 170, 110, 180, 350) + [(190, 605)]]
L["short_oo"] = [ell(-20, 445, 125, 135), stem(105, 0, 445)]

L["ay"] = [stem(30, 230), arc(30, 150, 120, 130, 90, -40), ell(-70, 165, 115, 125)]
L["ow"] = [ell(0, 185, 150, 145), ell(0, 450, 125, 130)]
L["wu"] = [[(-155, 620), (-170, 200)] + arc(-85, 200, 85, 160, 180, 360)[1:],
           [(0, 200), (0, 375)],
           arc(85, 200, 85, 160, 180, 360) + [(170, 200), (155, 620)]]
L["yee"] = [[(-150, 620), (0, 0), (150, 620)], arc(0, 470, 215, 100, 205, 335)]
L["h"] = [ell(0, 445, 165, 135), stem(0)]

# Consonants. Voiceless/voiced pairs share a construction.
L["pee"] = [[(-190, 580), (150, 580)], stem(150)]
bee_bowls = [[(165, 580), (-10, 580)] + arc(-10, 445, 155, 135, 90, 270)[1:] + [(-10, 310), (165, 310)],
             arc(-10, 175, 155, 135, 90, 270) + [(-10, 40), (165, 40)]]
L["bee"] = [stem(165)] + bee_bowls
L["tee"] = [stem(130, 0, 430), arc(-20, 430, 150, 150, 190, 0)]
L["dee"] = [ell(-20, 445, 125, 135), stem(130), arc(-20, 175, 150, 135, 90, 270) + [(-20, 40), (130, 40)]]
L["chee"] = [arc(-15, 310, 175, 270, 40, 320)]
L["jee"] = [arc(-10, 445, 120, 135, 45, 330) + [(100, 320), (-40, 0)]]
kay_base = [[(-165, 430), (-165, 200)] + arc(-82, 200, 83, 160, 180, 360)[1:],
            [(0, 200), (0, 375)],
            arc(82, 200, 83, 160, 180, 360) + [(165, 200), (165, 430)],
            arc(0, 430, 165, 150, 0, 180)]
L["kay"] = kay_base
L["gay"] = kay_base + [arc(25, 440, 70, 135, 90, -90)]
L["ef"] = [stem(-150), [(-150, 580), (-30, 580)] + arc(-30, 445, 160, 135, 90, -90)[1:] + [(-30, 310), (-150, 310)]]
L["vee"] = [arc(-20, 445, 150, 135, 150, -90), arc(-20, 175, 160, 135, 90, -150)]
L["eth"] = [[(-140, 620), (-140, 40), (170, 40)]]
L["thee"] = [[(-190, 620), (-45, 330)], [(190, 620), (45, 330)], ell(0, 165, 85, 125)]
L["es"] = [ell(0, 170, 165, 130), ell(0, 465, 100, 105), [(-215, 365), (0, 335), (215, 300)]]
L["zee"] = [ell(0, 190, 150, 150), [(-150, 190), (-150, 360)] + arc(0, 360, 150, 220, 180, 60)]
L["esh"] = [ell(10, 310, 150, 270), stem(-140, 300)]
L["zhee"] = [arc(0, 445, 145, 135, 30, 270) + arc(0, 175, 150, 135, 90, -150)[1:]]
L["er"] = [stem(0), [(-155, 500), (-155, 400)] + arc(0, 400, 155, 150, 180, 360)[1:] + [(155, 400), (155, 500)]]
L["el"] = [[(-165, 620), (-165, 200)] + arc(0, 200, 165, 160, 180, 360)[1:] + [(165, 200), (165, 300)]]
L["em"] = [arc(-40, 310, 190, 270, 110, -110)]
L["en"] = [[(-150, 620), (-150, 215), (150, 420)], stem(150, 0, 451)]
L["eng"] = [stem(-150), stem(150), [(-150, 40), (150, 580)]]
L["oi"] = [stem(110), [(-10, 570), (230, 430)], [(110, 40), (10, 200), (-70, 40), (-200, 200)]]
L["ew"] = [ell(0, 310, 170, 270), stem(0), [(-95, 440), (95, 250)]]

DESERET_ORDER = [
    "long_i", "long_e", "long_a", "long_ah", "long_o", "long_oo",
    "short_i", "short_e", "short_a", "short_ah", "short_o", "short_oo",
    "ay", "ow", "wu", "yee", "h",
    "pee", "bee", "tee", "dee", "chee", "jee", "kay", "gay", "ef", "vee",
    "eth", "thee", "es", "zee", "esh", "zhee", "er", "el", "em", "en", "eng",
    "oi", "ew",
]
assert len(DESERET_ORDER) == 40 and set(DESERET_ORDER) == set(LETTERS)

# ---------------------------------------------------------------- digits
D = {}
D["zero"] = [roundrect(0, 310, 130, 270, 110), [(0, 310)]]
D["one"] = [stem(20), [(-120, 480), (20, 580)]]
D["two"] = [arc(0, 445, 140, 135, 165, -35) + [(-150, 40), (170, 40)]]
D["three"] = [[(-140, 580), (130, 580), (-10, 345)] + arc(-10, 185, 155, 145, 90, -155)[1:]]
D["four"] = [[(110, 620), (-170, 190), (185, 190)], stem(110)]
D["five"] = [[(150, 580), (-100, 580), (-125, 340)] + arc(-5, 195, 150, 155, 125, -155)[1:]]
D["six"] = [ell(0, 190, 150, 150), [(-150, 190), (-150, 330), (70, 590)]]
D["seven"] = [[(-150, 580), (160, 580), (-30, 0)]]
D["eight"] = [roundrect(0, 170, 145, 130, 100), roundrect(0, 450, 120, 130, 90)]
D["nine"] = [ell(0, 430, 150, 150), [(150, 430), (150, 290), (-70, 30)]]
DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

# ---------------------------------------------------------------- punctuation
PUNCT = {
    "period": ([[(0, 60)]], 96),
    "comma": ([[(10, 60), (-30, -120)]], 90),
    "colon": ([[(0, 60)], [(0, 430)]], 96),
    "semicolon": ([[(10, 60), (-30, -120)], [(0, 430)]], 90),
    "hyphen": ([[(-130, 300), (130, 300)]], STROKE),
    "quotesingle": ([[(0, 620), (-16, 440)]], 90),
    "quotedbl": ([[(-60, 620), (-76, 440)], [(60, 620), (44, 440)]], 90),
    "exclam": ([[(0, 620), (0, 200)], [(0, 40)]], 90),
    "question": ([arc(0, 460, 150, 130, 160, -60) + [(0, 280), (0, 200)], [(0, 40)]], 84),
    "parenleft": ([arc(120, 280, 200, 400, 120, 240)], 70),
    "parenright": ([arc(-120, 280, 200, 400, 60, -60)], 70),
    "slash": ([[(-130, -60), (130, 640)]], 70),
}


# ---------------------------------------------------------------- LDS / Deseret symbols
def lens(bx, by, length, width, angle):
    """Pointed petal from base (bx,by) along `angle` degrees from vertical."""
    a = math.radians(angle)
    pts = []
    for side in (1, -1):
        for i in range(0, 21):
            t = i / 20 if side == 1 else 1 - i / 20
            lx = side * width * math.sin(math.pi * t) * 0.5
            ly = length * t
            pts.append((bx + lx * math.cos(a) - ly * math.sin(a),
                        by + lx * math.sin(a) + ly * math.cos(a)))
    return pts


def dome_hw(y, y0=40, ry=540, rx=210):
    u = (y - y0) / ry
    return rx * math.sqrt(max(0.0, 1 - u * u))


SYMBOLS = {
    "beehive": ([
        [(-240, 40), (240, 40)],
        arc(0, 40, 210, 540, 0, 180),
        [(-dome_hw(190), 190), (dome_hw(190), 190)],
        [(-dome_hw(330), 330), (dome_hw(330), 330)],
        [(-dome_hw(470), 470), (dome_hw(470), 470)],
        arc(0, 40, 55, 100, 0, 180),
    ], ICON_STROKE),
    "honeybee": ([
        ell(-10, 250, 170, 115),
        [(-75, 150), (-75, 350)], [(30, 140), (30, 360)],
        ell(-70, 500, 50, 90), ell(55, 480, 50, 90),
        [(160, 250), (255, 250)],
        [(-180, 290), (-250, 360)],
    ], ICON_STROKE),
    "segolily": ([
        lens(0, 120, 440, 150, 0), lens(0, 120, 380, 130, 36), lens(0, 120, 380, 130, -36),
        [(0, 120), (0, 0)],
    ], ICON_STROKE),
    "temple": ([
        [(-250, 40), (250, 40)],
        [(-235, 40), (-235, 330), (-185, 410), (-135, 330), (-135, 40)],
        [(135, 40), (135, 330), (185, 410), (235, 330), (235, 40)],
        [(-65, 40), (-65, 440), (0, 570), (65, 440), (65, 40)],
        [(-135, 200), (135, 200)],
    ], ICON_STROKE),
    "eye": ([
        [(-230 + 460 * i / 40, 270 + 150 * (1 - ((i - 20) / 20) ** 2)) for i in range(41)],
        [(-230 + 460 * i / 40, 270 - 150 * (1 - ((i - 20) / 20) ** 2)) for i in range(41)],
        ell(0, 270, 55, 55),
    ] + [[(235 * math.cos(math.radians(a)), 270 + 235 * math.sin(math.radians(a))),
          (275 * math.cos(math.radians(a)), 270 + 275 * math.sin(math.radians(a)))]
         for a in (90, 55, 125, 20, 160)], ICON_STROKE),
    "sunstone": ([ell(0, 310, 105, 105), [(0, 310)]] +
                 [[(150 * math.cos(math.radians(a)), 310 + 150 * math.sin(math.radians(a))),
                   (235 * math.cos(math.radians(a)), 310 + 235 * math.sin(math.radians(a)))]
                  for a in range(0, 360, 30)], ICON_STROKE),
    "trumpet": ([
        [(-250, 310), (90, 310)],
        [(90, 310), (235, 500)], [(90, 310), (235, 120)], [(235, 120), (235, 500)],
        [(-215, 310)],
    ], ICON_STROKE),
}
PUA = {"beehive": 0xE000, "honeybee": 0xE001, "segolily": 0xE002, "temple": 0xE003,
       "eye": 0xE004, "sunstone": 0xE005, "trumpet": 0xE006}
