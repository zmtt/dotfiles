"""The palette model: the parameters that define Umber, and nothing else.

build.py generates from these; optimise-stagger.py re-solves STAGGER against
them. Both used to carry their own copy, which meant tuning the chroma model in
build.py silently left the optimiser fitting the old one — precisely when you
would run it, since its whole purpose is to re-solve after a model change.
"""
import math

# Warmth sets the centre of gravity: chroma peaks at the ember hue and falls
# away toward the blues.
C_WARM, C_COOL = 0.130, 0.074

# The ember: where chroma peaks, and the hue the cursor and search wash borrow.
EMBER = 48.0

# How loud each hue is allowed to be, on top of warmth. Red and yellow are
# semantic — untracked files, modified files, errors — and must catch the eye.
# Magenta and blue are mostly chrome: branch names, task labels.
USAGE = {33.0: 1.00, 72.0: 1.00, 138.0: 0.88, 196.0: 0.80, 250.0: 0.78, 340.0: 0.62}

HUES = {"red": 33.0, "green": 138.0, "yellow": 72.0,
        "blue": 250.0, "magenta": 340.0, "cyan": 196.0}

# Near-uniform lightness keeps the palette calm, but perfectly uniform lightness
# is what makes hues collapse into each other for colour-blind viewers. Solved
# by optimise-stagger.py against the chroma model above.
STAGGER = {"red": -0.044, "green": +0.005, "yellow": +0.009,
           "blue": -0.031, "magenta": -0.030, "cyan": +0.043}

def chroma_for(hue, scale=1.0):
    warmth = (math.cos(math.radians(hue - EMBER)) + 1) / 2
    return (C_COOL + (C_WARM - C_COOL) * warmth) * USAGE.get(hue, 1.0) * scale
