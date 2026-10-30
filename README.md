# Beehive Deseret

An original geometric font for the Deseret Alphabet (Unicode block U+10400–1044F).
The beehive is the Deseret symbol (*deseret* = honeybee in the Book of Mormon).

The letterforms are my own systematic design, **not** the historical 1850s forms
or any existing Deseret font. The aim is a regular, readable alphabet:

- **Consonants** hang from a vertical stem. Each voiceless/voiced pair shares one
  feature; the voiced letter adds a foot bar on the baseline
  (Pee/Bee, Tee/Dee, Chee/Jee, Kay/Gay, Ef/Vee, Eth/Thee, Es/Zee, Esh/Zhee).
- **Vowels** are stemless open shapes (ring, left arc, right arc, arch, cup, peak).
  Long vowels are tall; short vowels are the same shape at roughly half height.
- **Lowercase** is the capital shape scaled to 78% with a lighter stroke.

Includes space and `. , : - ' ! ?` (Latin text is not covered).

## Build

    pip install fonttools brotli skia-pathops pillow
    python3 build.py        # -> fonts/BeehiveDeseret-Regular.{ttf,woff2}
    python3 preview.py      # -> specimen.png

Open `specimen.html` in a browser for the full chart.

## Status

v0.1: outlines are polygonal (stroked skeletons with overlaps removed), no hinting,
no kerning. Next: curve fitting to quadratics, optical spacing, and a Latin fallback.
