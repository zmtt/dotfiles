"""Re-solve the lightness staggers when the chroma model changes.

Two sets of offsets, one objective. Perfectly uniform lightness keeps a palette
calm but collapses hues into each other under colour-vision deficiency, so the
offsets buy separation back; each spread is capped to keep the palette from
looking uneven.

  model.STAGGER        the terminal accents, offsets in Lr
  editor.ROLE_STAGGER  the editor roles, multipliers on each contrast target

Both maximise the same thing: the smallest perceptual distance between any two
colours, across deuteranopia, protanopia and tritanopia, on both variants at
once. That measurement is perceptual.worst_separation, shared with the gates in
build.py, audit.py and editor.audit so the solver and the gate cannot disagree.

The editor set exists because re-levelling chroma per role while solving every
role to one flat contrast target removed both non-hue axes at once, which is
the failure model.STAGGER was already there to prevent.

It deliberately does NOT constrain the semantic-over-chrome salience ordering.
That ordering is not strictly invariant under STAGGER — gamut clipping depends
on lightness, so realized chroma moves with the offsets — but build.py gates on
salience directly, which is where that belongs.

Both solvers do constrain contrast, with a margin above the floor rather than
the floor itself: separation will otherwise buy its last thousandth by pushing
a colour down onto the floor, where any later retune pushes it through.
"""
import json
import math
import os
import random

from editor import ROLE_STAGGER, FAMILY, syntax, separation
from model import ACC_L, CSCALE, FLOOR, HUES, STAGGER, chroma_for
from palette import contrast
from perceptual import hex_lr, l_to_lr, worst_separation

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = list(HUES)
ROLES = list(ROLE_STAGGER)   # family members follow a head, so never appear here
SAMPLES = 40000

MAX_SPREAD = 0.095        # Lr, accents
# Fraction of the contrast target, editor roles. Widening this is where the
# separation/calm tradeoff lives.
MAX_ROLE_SPREAD = 0.36

# Both solvers need the built palette: the accent solver for the grounds it
# checks contrast against, the role solver because roles are solved against a
# whole variant rather than a bare lightness.
PALETTE = json.load(open(os.path.join(HERE, "palette.json")))

# Accent lightness and chroma scale per variant, from the same model.py values
# build.py builds with, so this model is exact rather than a mirrored copy.
GROUNDS = {v: (l_to_lr(ACC_L[v]), CSCALE[v]) for v in ACC_L}

# Separation alone will happily buy its last thousandth by pushing an accent
# down onto its contrast floor, so both solvers hold a margin above it.
ACCENT_MARGIN = 0.30

ROLE_GROUNDS = {v: PALETTE[v] for v in ("dark", "light")}

# Same shape as ACCENT_MARGIN, kept separate because the two constrain
# different derivations and there is no reason they must move together.
ROLE_MARGIN = 0.30


def colours(stagger, base_lr, cscale):
    return {k: hex_lr(base_lr + stagger[k], chroma_for(HUES[k], cscale), HUES[k])[0]
            for k in KEYS}


def accent_score(stagger, margin=ACCENT_MARGIN):
    """Worst separation across both variants, or None if a floor fails.

    Candidates are held to the floor plus the margin; the incumbent is scored
    with margin=0, because the margin is a search constraint, not a shipping
    gate — judging the shipped values against it made an idle run report
    "INFEASIBLE" for a palette that passes every real gate, and recommend
    rewriting it.
    """
    worst = float("inf")
    for name, (base, cscale) in GROUNDS.items():
        cols = colours(stagger, base, cscale)
        bg = PALETTE[name]["background"]
        floor = FLOOR[name] + margin
        if any(contrast(c, bg) < floor for c in cols.values()):
            return None
        worst = min(worst, worst_separation(cols)[0])
    return worst


def role_score(stagger, margin=ROLE_MARGIN):
    """As accent_score, for the editor roles.

    Infeasible candidates score None rather than a low number so that a box
    whose whole interior misses the floor reports as infeasible instead of
    quietly returning its least-bad corner.

    Only the roles the stagger moves are constrained: a floor the solver
    cannot affect is not its constraint to satisfy.
    """
    moved = set(ROLE_STAGGER) | set(FAMILY)
    worst = float("inf")
    for name, V in ROLE_GROUNDS.items():
        S = syntax(V, stagger)
        floor = FLOOR[name] + margin
        if any(contrast(S[r], V["background"]) < floor for r in moved):
            return None
        worst = min(worst, separation(S, V["foreground"])[0])
    return worst


RESTARTS = 6


def climb(score, keys, lo, hi, start, start_score, spread):
    """Walk each coordinate up and down at a shrinking step until nothing helps."""
    best_score, best = start_score, dict(start)
    step = spread / 8
    while step > spread / 2000:
        improved = False
        for k in keys:
            for delta in (step, -step):
                cand = dict(best)
                cand[k] = min(hi, max(lo, cand[k] + delta))
                s = score(cand)
                if s is not None and s > best_score:
                    best_score, best, improved = s, cand, True
        if not improved:
            step /= 2
    return best_score, best


def maximise(score, keys, centre, spread, samples, current, seed):
    """Sample the box, then hill-climb from the best several samples.

    Sampling alone covers the box thinly; climbing from the single best sample
    stays inside one lucky basin. Climbing from the best RESTARTS samples and
    keeping the winner costs a few thousand extra evaluations and makes the
    answer stable across seeds.
    """
    random.seed(seed)
    lo, hi = centre - spread / 2, centre + spread / 2
    # The incumbent is admitted at its margin-free score: legal-but-inside-the-
    # margin must still be the value to beat, or the tool recommends churn.
    cur = score(current, 0)
    scored = [((-math.inf if cur is None else cur), dict(current))]
    for _ in range(samples):
        cand = {k: random.uniform(lo, hi) for k in keys}
        s = score(cand)
        if s is not None:
            scored.append((s, cand))
    scored.sort(key=lambda t: t[0], reverse=True)

    best_score, best = scored[0]
    for s, start in scored[:RESTARTS]:
        cs, cand = climb(score, keys, lo, hi, start, s, spread)
        if cs > best_score:
            best_score, best = cs, cand
    return best_score, (None if best == dict(current) else best)


def report(label, keys, current, cur_score, best_score, best, vfmt, unit):
    """vfmt formats a value; spreads are magnitudes, so they drop any sign flag."""
    sfmt = vfmt.lstrip("+")
    spread = max(current[k] for k in keys) - min(current[k] for k in keys)
    print(f"\n{label}")
    if cur_score is None:
        print(f"  current  ILLEGAL, misses a real contrast floor   spread {spread:{sfmt}} {unit}")
    else:
        print(f"  current  worst separation dE {cur_score:.4f}   spread {spread:{sfmt}} {unit}")
    if best is None:
        print("  no candidate beat it; nothing to change.")
        return False
    print(f"  best     worst separation dE {best_score:.4f}   "
          f"spread {max(best.values()) - min(best.values()):{sfmt}} {unit}")
    for k in keys:
        print(f"    {k:<9} {current[k]:{vfmt}} -> {best[k]:{vfmt}}")
    return True


if __name__ == "__main__":
    acc_cur = accent_score(STAGGER, 0)
    acc_best_score, acc_best = maximise(accent_score, KEYS, 0.0, MAX_SPREAD,
                                        SAMPLES, STAGGER, seed=20260814)
    acc_changed = report("accents (model.STAGGER)", KEYS, STAGGER, acc_cur,
                         acc_best_score, acc_best, "+.3f", "Lr")

    role_cur = role_score(ROLE_STAGGER, 0)
    role_best_score, role_best = maximise(role_score, ROLES, 1.0, MAX_ROLE_SPREAD,
                                          SAMPLES // 8, ROLE_STAGGER, seed=20260818)
    role_changed = report("editor roles (editor.ROLE_STAGGER)", ROLES, ROLE_STAGGER,
                          role_cur, role_best_score, role_best, ".3f", "x target")

    if not (acc_changed or role_changed):
        raise SystemExit(0)

    out = os.path.join(HERE, "stagger.json")
    with open(out, "w") as f:
        json.dump({"accents": acc_best or STAGGER,
                   "roles": role_best or {k: ROLE_STAGGER[k] for k in ROLES}}, f, indent=1)
    print(f"\nwrote {out}; copy accents into model.STAGGER and roles into "
          "editor.ROLE_STAGGER, then rerun build.py, every emitter, and audit.py")
