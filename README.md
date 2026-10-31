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

Also done from the period type: small ball terminals on free curved stroke ends (Long I/E, Chee, Jee,
Zee, Zhee, Er, El, Em, Ay, Yee, Es, Short O), heavier straight bars than curved hairlines (`BAR`), and
every letter and digit normalised to exactly the same height. `period_proof.py` cuts the 37 letters
printed in the chart and places Beehive beside each for checking.

Spacing: letters in the 1869 text are about 0.75-0.95 of their height wide with gaps of roughly
0.15-0.2 of the height; the 620-unit cell (1.0 x height) holds the widest letter (526) with at least
47 units clear on each side. Automatic measurement on running text is noisy because letters touch.

Not yet reproduced: letterpress edge irregularity, and a few letters (Ow, Long A, Yee, Thee, Es)
remain simplified.

## Ligatures

The 1859 *Deseret News* approved two ligature letters. The `calt` feature applies them, keeping the
monospace grid (the first cell is blanked and the letter is drawn across both cells):

| Sequence | Becomes |
|----------|---------|
| Short I + Long OO (U+1042E U+1042D) | Ew |
| Yee + Long OO (U+10437 U+1042D) | Ew |
| Short AH + Short I (U+10431 U+1042E) | Oi |

Works for capital or lowercase code points. Turn off with `font-feature-settings: "calt" 0`.

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
    python3 compare.py REF.ttf cmp.png          # vs any reference Deseret font
    python3 period_proof.py bom.pdf proof.png   # vs the printed 1869 chart (needs pymupdf)

Pipeline: skeleton polylines -> stroked polygons (flat ends, mitred joins) -> overlap union
(skia-pathops) -> Schneider cubic Bézier fitting (`curvefit.py`) -> quadratic TrueType curves.

## Status

v0.4. No hinting or kerning (monospace, so kerning is moot). Licence undecided.
