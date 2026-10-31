# Beehive Deseret Mono

A monospace font for the Deseret Alphabet (Unicode U+10400-1044F), with digits and a set of
LDS / Deseret symbols. *Deseret* is the Book of Mormon word for honeybee; the beehive is the
Utah/Deseret emblem.

## Fidelity to the originals

The alphabet was developed 1847-1854 by the University of Deseret Board of Regents under Brigham
Young (George D. Watt made the main contribution to the glyphs, with W. W. Phelps and Parley P. Pratt)
and approved 19 January 1854. Two ligatures (Oi, Ew) were added in 1859, giving 40 letters.

Design principles of the originals, which this font follows:

- One uniform letter height, no ascenders or descenders (Beehive: every letter spans exactly 0-620).
- One monoline stroke, flat-cut ends.
- No case. The Unicode lowercase block (U+10428-1044F) maps to the same shapes as the capitals.
- 40 letters, one per sound, each letter's name is its sound.

The letterforms are redrawn by hand as stroke skeletons (`skeletons.py`). Two references were used
for looking only; no outlines are copied from either:

- the 1869 Deseret Alphabet edition of the Book of Mormon (printed by Russell Bros. for the Deseret
  University; scan on [deseretalphabet.org](https://www.deseretalphabet.org/files/reading-material/)),
  including its printed alphabet chart;
- Noto Sans Deseret (OFL), via `compare.py`, for side-by-side proofs.

What the period type taught us, and what the font now does:

- Strong vertical stress: heavy verticals and thin horizontals, like the Didone-style metal type of
  the day (`CONTRAST` in `skeletons.py`; set it to 1 for a monoline version).
- Bold overall weight; round letters (Long O, Wu, rings) nearly as wide as tall.
- Every letter spans the same height (0-620); there is no case.

Not yet reproduced: the period type's small curled terminals (Kay/Gay, Yee, Ay) and its slightly
uneven letterpress edges. Shapes such as Ay, Ow, Yee, Thee and Es are close approximations.

## Symbols (Private Use Area)

| Code | Glyph |
|------|-------|
| U+E000 | Beehive (skep) |
| U+E001 | Honeybee |
| U+E002 | Sego lily (Utah state flower) |
| U+E003 | Temple (three-spire silhouette) |
| U+E004 | All-seeing eye (as on the 1860 Deseret coinage) |
| U+E005 | Sunstone (Nauvoo) |
| U+E006 | Trumpet (Moroni) |

## Digits and punctuation

`0-9` are drawn in the same monoline style and at the same height as the letters
(`0` and `8` are rounded rectangles so they never read as Long O / Ow).
Also `. , : ; - ' " ! ? ( ) /`.

## Build

    pip install fonttools brotli skia-pathops pillow numpy
    python3 build.py        # -> fonts/BeehiveDeseretMono-Regular.{ttf,woff2}
    python3 preview.py      # -> specimen.png
    python3 compare.py REF.ttf cmp.png

Pipeline: skeleton polylines -> stroked polygons (flat ends, mitred joins) -> overlap union
(skia-pathops) -> Schneider cubic Bézier fitting (`curvefit.py`) -> quadratic TrueType curves.

## Status

v0.3. No hinting or kerning (monospace, so kerning is moot). Licence undecided.
