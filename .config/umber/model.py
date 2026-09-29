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
USAGE = {33.0: 1.00, 72.0: 1.00, 130.0: 0.88, 190.0: 0.80, 245.0: 0.78, 325.0: 0.62}

HUES = {"red": 33.0, "green": 130.0, "yellow": 72.0,
        "blue": 245.0, "magenta": 325.0, "cyan": 190.0}

# Uniform lightness keeps the palette calm, and with CVD_SAFE off hue alone
# holds the accents apart, so every offset is zero. Uniform lightness is also
# what collapses hues for a dichromat: with CVD_SAFE on, re-solve these with
# optimise-stagger.py against the chroma model above.
STAGGER = {"red": 0.0, "green": 0.0, "yellow": 0.0,
           "blue": 0.0, "magenta": 0.0, "cyan": 0.0}

# No two colours that carry distinct meaning may be closer than this for any
# dichromat, measured by perceptual.worst_separation. It is a collapse detector,
# not an optimality target: the floor sits below what the staggers reach, so
# ordinary retuning does not trip it. The case it exists to catch is a set of
# roles at one flat lightness, which passes every contrast check while two of
# its hues sit a dE of 0.004 apart for a dichromat.
SEPARATION_FLOOR = 0.035

# Whose eyes separation is measured for. False measures normal trichromat
# vision only, which frees every accent and role to one even lightness: the
# staggers existed to buy dichromat separation back and cost the palette its
# calm. True restores the three dichromacies, and then STAGGER and
# ROLE_STAGGER need re-solving with optimise-stagger.py.
CVD_SAFE = False

# Accent placement per variant: base lightness (pre-toe Oklab L) and chroma
# scale, plus the readable floor each variant gates against. build.py builds
# from these and optimise-stagger.py scores candidates against them; a mirrored
# copy is exactly the stale-fit failure this module exists to prevent.
ACC_L = {"dark": 0.745, "light": 0.500}
CSCALE = {"dark": 1.00, "light": 1.05}
FLOOR = {"dark": 4.5, "light": 4.5}

# APCA |Lc| floors, gated beside FLOOR because WCAG 2 overstates contrast near
# black: at matched ratios the dark variant read far weaker than the light one
# (comments Lc 34 against 70). APCA's own guidance is Lc 75 for body text, 60
# for content, 45 for large text and 30 for spot-readable. The dark variant
# is held just above these rather than well clear of them: light text on a dark
# ground blooms, and brightness past readability buys glare, not legibility.
# With CVD_SAFE on, syntax cannot hold 50: red loses its chroma above about
# Lc 62 on the dark ground, errors must stay on top, and the staggers then need
# a spread that stack cannot fit.
APCA_FLOOR = {"body": 75, "accent": 52, "syntax": 50, "comment": 38}

def chroma_for(hue, scale=1.0):
    warmth = (math.cos(math.radians(hue - EMBER)) + 1) / 2
    return (C_COOL + (C_WARM - C_COOL) * warmth) * USAGE.get(hue, 1.0) * scale
