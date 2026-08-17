from perceptual import hex_lr, l_to_lr, contrast, delta_e, CVD
from palette import lum
import math, json, os, itertools
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# The aesthetic thesis: this is an EARTH palette, not a neutral one with a warm
# ground. Warm hues carry more chroma than cool hues, so the palette has a centre
# of gravity instead of an even spread. Cool hues recede rather than compete.
C_WARM, C_COOL = 0.130, 0.074
PEAK = 48.0     # hue where chroma is highest — the ember

# Warmth sets the centre of gravity; usage weight decides how loud a colour is
# allowed to be. Red and yellow are semantic (errors, modified files) and must
# carry. Magenta and blue are mostly chrome — branch names, task labels — and
# persistent chrome must never be the loudest thing on the screen.
USAGE = {33.0: 1.00, 72.0: 1.00, 138.0: 0.88, 196.0: 0.80, 250.0: 0.78, 340.0: 0.62}

def chroma_for(hue, scale=1.0):
    warmth = (math.cos(math.radians(hue - PEAK)) + 1) / 2      # 1 at PEAK, 0 opposite
    base = C_COOL + (C_WARM - C_COOL) * warmth
    return base * USAGE.get(hue, 1.0) * scale

# Hues pulled toward earth: sage green, teal cyan, rose magenta, slate blue.
HUES = {"red": 33.0, "green": 138.0, "yellow": 72.0,
        "blue": 250.0, "magenta": 340.0, "cyan": 196.0}
# Re-solved against the usage-weighted chroma model rather than the equal-chroma
# one it was first fitted to. Same spread, 43% better worst-case CVD separation.
STAGGER = {"red": -0.044, "green": +0.005, "yellow": +0.009,
           "blue": -0.031, "magenta": -0.030, "cyan": +0.043}

def solve(target, bg, C, H):
    dark = lum(bg) < 0.18
    lo, hi = (0.30, 0.995) if dark else (0.02, 0.70)
    for _ in range(70):
        mid = (lo + hi) / 2
        if (contrast(hex_lr(mid, C, H)[0], bg) < target) == dark: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def build(bg_L, bg_c, bg_h, nh, acc_L, br_L, cscale, br_cscale, targets, sel_L, cur_L, bg_hex=None):
    bg = bg_hex or hex_lr(l_to_lr(bg_L), bg_c, bg_h)[0]
    dark = lum(bg) < 0.18
    P = {"background": bg}
    P["foreground"] = hex_lr(solve(targets["fg"], bg, 0.020, nh), 0.020, nh)[0]
    for slot, t, c in ((0, targets["s0"], 0.022), (8, targets["s8"], 0.020)):
        P[slot] = hex_lr(solve(t, bg, c, nh), c, nh)[0]
    bg_lr = l_to_lr(bg_L)
    if dark:
        P[7]  = hex_lr(solve(targets["s7"], bg, 0.016, nh), 0.016, nh)[0]
        P[15] = hex_lr(solve(targets["s15"], bg, 0.010, nh), 0.010, nh)[0]
    else:
        P[7]  = hex_lr(bg_lr - 0.150, 0.018, nh)[0]
        P[15] = hex_lr(bg_lr - 0.055, 0.011, nh)[0]
    P["selection"] = hex_lr(l_to_lr(sel_L), 0.030, nh)[0]
    P["cursor"] = hex_lr(l_to_lr(cur_L), chroma_for(PEAK) * 1.15, PEAK)[0]
    notes = []
    for key, idx in (("red",1),("green",2),("yellow",3),("blue",4),("magenta",5),("cyan",6)):
        H = HUES[key]
        for base, off, sc in ((l_to_lr(acc_L), 0, cscale), (l_to_lr(br_L), 8, br_cscale)):
            C = chroma_for(H, sc)
            hx, clipped, c2 = hex_lr(base + STAGGER[key], C, H)
            P[idx+off] = hx
            if clipped: notes.append(f"{key}{'+' if off else ''} C{C:.3f}->{c2:.3f}")
    return P, notes

DARK, dn = build(bg_L=0.190, bg_c=0.017, bg_h=52, nh=60, acc_L=0.745, br_L=0.820,
    cscale=1.0, br_cscale=0.92, sel_L=0.310, cur_L=0.800, bg_hex="#171614",
    targets={"fg":11.0, "s0":1.55, "s8":4.60, "s7":9.8, "s15":14.0})

NIGHT, nn = build(bg_L=0.190, bg_c=0.017, bg_h=52, nh=60, acc_L=0.655, br_L=0.712,
    cscale=0.90, br_cscale=0.84, sel_L=0.295, cur_L=0.715, bg_hex="#171614",
    targets={"fg":8.0, "s0":1.50, "s8":4.20, "s7":7.2, "s15":9.8})

LIGHT, ln = build(bg_L=0.964, bg_c=0.014, bg_h=70, nh=66, acc_L=0.500, br_L=0.430,
    cscale=1.05, br_cscale=1.0, sel_L=0.890, cur_L=0.520, bg_hex="#f8f7f5",
    targets={"fg":10.9, "s0":13.0, "s8":4.65, "s7":1.70, "s15":1.12})

NAMES = {1:"red",2:"green",3:"yellow",4:"blue",5:"magenta",6:"cyan"}
def report(label, P, notes):
    bg = P["background"]
    print(f"\n=== {label}  bg {bg}  fg {P['foreground']} {contrast(P['foreground'],bg):.2f}:1 ===")
    print(f"  comments(8) {P[8]} {contrast(P[8],bg):.2f}:1   cursor {P['cursor']}   sel {P['selection']}")
    rs = []
    for i in range(1,7):
        a = contrast(P[i],bg); rs += [a, contrast(P[i+8],bg)]
        print(f"  {NAMES[i]:<8} {P[i]} {a:5.2f}:1  C={chroma_for(HUES[NAMES[i]]):.3f}  bright {P[i+8]}")
    print(f"  accents {min(rs):.2f} .. {max(rs):.2f}:1")
    if notes: print("  gamut:", "; ".join(notes))
    acc = [P[i] for i in range(1,7)]
    for kind in ["deuteranopia","protanopia","tritanopia"]:
        w = min(delta_e(acc[a],acc[b],kind) for a,b in itertools.combinations(range(6),2))
        print(f"  {kind:<13} worst dE {w:.3f}")

report("EARTH dark", DARK, dn); report("NIGHT", NIGHT, nn); report("EARTH light", LIGHT, ln)
json.dump({"dark":DARK,"night":NIGHT,"light":LIGHT}, open(_os.path.join(_HERE, "palette.json"),"w"), indent=1)

OUT = os.path.expanduser("~/.config/ghostty/themes")
for fname, P in (("umber", DARK), ("umber-night", NIGHT), ("umber-light", LIGHT)):
    hdr = (f"# Umber{' Light' if 'light' in fname else ''} — an earth palette.\n"
           "# Accents placed in OKLrCH. Warm hues carry more chroma than cool ones so the\n"
           "# palette has a centre of gravity; chroma is further weighted by how each slot\n"
           "# is actually used, so persistent chrome never outshouts semantic colour.\n\n")
    body = (f"background = {P['background']}\nforeground = {P['foreground']}\n"
            f"cursor-color = {P['cursor']}\ncursor-text = {P['background']}\n"
            f"selection-background = {P['selection']}\nselection-foreground = {P['foreground']}\n\n")
    open(os.path.join(OUT, fname), "w").write(
        hdr + body + "\n".join(f"palette = {i}={P[i]}" for i in range(16)) + "\n")
print("wrote umber + umber-light")

print("\n--- final safety audit ---")
for label, P in (("dark", DARK), ("light", LIGHT)):
    bg, sel, cur = P["background"], P["selection"], P["cursor"]
    text_slots = [i for i in range(16) if i not in ((0, 7, 15) if label == "light" else (0,))]
    worst_sel = min((contrast(P[i], sel), i) for i in text_slots)
    print(f"  {label:<6} fg/bg {contrast(P['foreground'],bg):5.2f}:1   "
          f"fg on selection {contrast(P['foreground'],sel):5.2f}:1   "
          f"worst text slot on selection: {worst_sel[1]} at {worst_sel[0]:.2f}:1")
    print(f"         cursor {cur} vs cursor-text {bg}: {contrast(cur,bg):5.2f}:1   "
          f"dimmest text slot vs bg: {min(contrast(P[i],bg) for i in text_slots):.2f}:1")
