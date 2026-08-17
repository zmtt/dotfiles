from perceptual import hex_lr, l_to_lr, delta_e
from palette import contrast
import math, random, itertools, json

random.seed(20260814)
KEYS = ["red","green","yellow","blue","magenta","cyan"]
HUES = {"red":33.0,"green":138.0,"yellow":72.0,"blue":250.0,"magenta":340.0,"cyan":196.0}
USAGE = {33.0:1.00, 72.0:1.00, 138.0:0.88, 196.0:0.80, 250.0:0.78, 340.0:0.62}
C_WARM, C_COOL, PEAK = 0.130, 0.074, 48.0
SEMANTIC, CHROME = ["red","yellow"], ["cyan","blue","magenta"]
GROUNDS = {"dark": ("#171614", l_to_lr(0.745), True), "light": ("#f8f7f5", l_to_lr(0.505), False)}

def chroma_for(h):
    warmth = (math.cos(math.radians(h - PEAK)) + 1) / 2
    return (C_COOL + (C_WARM - C_COOL) * warmth) * USAGE[h]

def cols_for(stag, base):
    return {k: hex_lr(base + stag[k], chroma_for(HUES[k]), HUES[k])[0] for k in KEYS}

def hierarchy_ok(stag):
    """Semantic hues must outrank every chrome hue, on BOTH grounds."""
    for bg, base, _ in GROUNDS.values():
        c = {k: contrast(v, bg) for k, v in cols_for(stag, base).items()}
        if min(c[s] for s in SEMANTIC) <= max(c[h] for h in CHROME):
            return False
    return True

def cvd_worst(stag):
    w = 99
    for bg, base, _ in GROUNDS.values():
        cl = list(cols_for(stag, base).values())
        for kind in ("deuteranopia","protanopia","tritanopia"):
            for a,b in itertools.combinations(range(6),2):
                w = min(w, delta_e(cl[a], cl[b], kind))
    return w

CUR = {"red":-0.044,"green":+0.005,"yellow":+0.009,"blue":-0.031,"magenta":-0.030,"cyan":+0.043}
print(f"current      hierarchy {'OK' if hierarchy_ok(CUR) else 'VIOLATED'}   worst CVD dE {cvd_worst(CUR):.3f}")

MAX, best, tried = 0.095, None, 0
for _ in range(40000):
    s = {k: random.uniform(-MAX/2, MAX/2) for k in KEYS}
    if max(s.values()) - min(s.values()) > MAX: continue
    if not hierarchy_ok(s): continue
    tried += 1
    w = cvd_worst(s)
    if best is None or w > best[0]: best = (w, s)

w, stag = best
print(f"constrained  hierarchy OK          worst CVD dE {w:.3f}   ({tried} feasible candidates)")
print(f"spread {max(stag.values())-min(stag.values()):.3f} Lr\n")
for k in KEYS:
    print(f"  {k:<8} {CUR[k]:+.3f} -> {stag[k]:+.3f}")
json.dump(stag, open("stagger2.json","w"), indent=1)
