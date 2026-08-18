"""Re-solve model.STAGGER when the chroma model changes.

STAGGER offsets each accent's lightness a little. Perfectly uniform lightness
keeps the palette calm but collapses hues into each other under colour-vision
deficiency, so the offsets buy separation back; the spread is capped to keep the
palette from looking uneven.

This searches for the offsets that maximise the worst-case separation across
deuteranopia, protanopia and tritanopia, on both grounds at once.

It deliberately does NOT constrain the semantic-over-chrome salience ordering.
That ordering is not strictly invariant under STAGGER — gamut clipping depends
on lightness, so realized chroma moves with the offsets — but it was measured
to hold across the whole allowed box, with the tightest margin on the light
ground. build.py now gates on salience directly, which is where that belongs. An earlier version constrained
it using contrast as the proxy — contrast measures legibility, not salience —
and no candidate in 40,000 satisfied it, so the script raised TypeError on every
run instead of reporting that its own constraint was infeasible.
"""
import itertools
import json
import os
import random

from model import HUES, STAGGER, chroma_for
from perceptual import delta_e, hex_lr, l_to_lr

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = list(HUES)
CVDS = ("deuteranopia", "protanopia", "tritanopia")
MAX_SPREAD = 0.095
SAMPLES = 40000

# Accent lightness per ground, mirroring build.py's acc_L for each variant. The
# night variant shares the dark ground and its accents sit between the two, so
# bounding the search on dark and light covers it.
GROUNDS = {"dark": l_to_lr(0.745), "light": l_to_lr(0.500)}


def colours(stagger, base_lr):
    return [hex_lr(base_lr + stagger[k], chroma_for(HUES[k]), HUES[k])[0] for k in KEYS]


def worst_separation(stagger):
    """Smallest perceptual distance between any two accents, across every ground
    and every simulated deficiency. Higher is better."""
    worst = float("inf")
    for base_lr in GROUNDS.values():
        cols = colours(stagger, base_lr)
        for kind in CVDS:
            for a, b in itertools.combinations(range(len(KEYS)), 2):
                worst = min(worst, delta_e(cols[a], cols[b], kind))
    return worst


if __name__ == "__main__":
    current = worst_separation(STAGGER)
    print(f"current  worst separation dE {current:.3f}   "
          f"spread {max(STAGGER.values()) - min(STAGGER.values()):.3f} Lr")

    random.seed(20260814)
    best_score, best = current, None
    for _ in range(SAMPLES):
        cand = {k: random.uniform(-MAX_SPREAD / 2, MAX_SPREAD / 2) for k in KEYS}
        score = worst_separation(cand)
        if score > best_score:
            best_score, best = score, cand

    if best is None:
        print(f"\nno candidate beat the shipped STAGGER in {SAMPLES} samples; nothing to change.")
        raise SystemExit(0)

    print(f"best     worst separation dE {best_score:.3f}   "
          f"spread {max(best.values()) - min(best.values()):.3f} Lr\n")
    for k in KEYS:
        print(f"  {k:<8} {STAGGER[k]:+.3f} -> {best[k]:+.3f}")
    out = os.path.join(HERE, "stagger.json")
    with open(out, "w") as f:
        json.dump(best, f, indent=1)
    print(f"\nwrote {out}; copy into model.STAGGER, then rerun build.py and audit.py")
