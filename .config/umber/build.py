from perceptual import (hex_lr, l_to_lr, lch, contrast, solve_lr,
                        worst_separation, write_atomic)
from palette import lum, enforce
from model import EMBER, HUES, STAGGER, SEPARATION_FLOOR, chroma_for
import json, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))


def build(bg_hex, nh, acc_L, br_L, cscale, br_cscale, targets, sel_L, cur_L):
    bg = bg_hex
    dark = lum(bg) < 0.18
    P = {"background": bg}
    P["foreground"] = hex_lr(solve_lr(targets["fg"], bg, 0.020, nh), 0.020, nh)[0]
    for slot, t, c in ((0, targets["s0"], 0.022), (8, targets["s8"], 0.020)):
        P[slot] = hex_lr(solve_lr(t, bg, c, nh), c, nh)[0]
    bg_lr = lch(bg)[0]   # the real ground, not the bg_L parameter
    if dark:
        P[7]  = hex_lr(solve_lr(targets["s7"], bg, 0.016, nh), 0.016, nh)[0]
        P[15] = hex_lr(solve_lr(targets["s15"], bg, 0.010, nh), 0.010, nh)[0]
    else:
        P[7]  = hex_lr(bg_lr - 0.150, 0.018, nh)[0]
        P[15] = hex_lr(bg_lr - 0.055, 0.011, nh)[0]
    P["selection"] = hex_lr(l_to_lr(sel_L), 0.030, nh)[0]
    P["cursor"] = hex_lr(l_to_lr(cur_L), chroma_for(EMBER) * 1.15, EMBER)[0]
    notes = []
    for key, idx in (("red",1),("green",2),("yellow",3),("blue",4),("magenta",5),("cyan",6)):
        H = HUES[key]
        for base, off, sc in ((l_to_lr(acc_L), 0, cscale), (l_to_lr(br_L), 8, br_cscale)):
            C = chroma_for(H, sc)
            hx, clipped, c2 = hex_lr(base + STAGGER[key], C, H)
            P[idx+off] = hx
            if clipped: notes.append(f"{key}{'+' if off else ''} C{C:.3f}->{c2:.3f}")
    return P, notes

DARK, dn = build(nh=60, acc_L=0.745, br_L=0.820,
    cscale=1.0, br_cscale=0.92, sel_L=0.310, cur_L=0.750, bg_hex="#171614",
    targets={"fg":11.0, "s0":1.55, "s8":4.60, "s7":9.8, "s15":14.0})

LIGHT, ln = build(nh=66, acc_L=0.500, br_L=0.430,
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
    sep, pair = worst_separation({NAMES[i]: P[i] for i in range(1, 7)})
    print(f"  separation    worst dE {sep:.4f}  ({pair[0]}/{pair[1]} {pair[2]})")

report("EARTH dark", DARK, dn); report("EARTH light", LIGHT, ln)

# Gate before writing anything, the way the editor emitters do. Writing first
# and reporting after cannot fail a run, and leaves palette.json — the source
# every other emitter reads — ahead of the themes the terminal is using.
FLOOR = {"dark": 4.5, "light": 4.5}
fail = []
for label, P in (("dark", DARK), ("light", LIGHT)):
    bg, sel, f = P["background"], P["selection"], FLOOR[label]
    text = [i for i in range(16) if i not in ((0, 7, 15) if label == "light" else (0,))]
    checks = [("fg/bg", contrast(P["foreground"], bg), f),
              ("dimmest text", min(contrast(P[i], bg) for i in text), f),
              ("fg on selection", contrast(P["foreground"], sel), f),
              ("cursor on bg", contrast(P["cursor"], bg), f)]
    bad = [n for n, x, floor in checks if x < floor]
    ch = {k: lch(P[i])[1] for k, i in
          (("red", 1), ("yellow", 3), ("cyan", 6), ("blue", 4), ("magenta", 5))}
    if min(ch["red"], ch["yellow"]) <= max(ch["cyan"], ch["blue"], ch["magenta"]):
        bad.append("salience")
    sep, pair = worst_separation({NAMES[i]: P[i] for i in range(1, 7)})
    if sep < SEPARATION_FLOOR:
        bad.append(f"separation {pair[0]}/{pair[1]}")
    print(f"  {label:<6} " + "  ".join(f"{n} {x:5.2f}" for n, x, _ in checks)
          + f"   floor {f}  {'PASS' if not bad else 'BELOW: ' + str(bad)}")
    fail += [f"{label}:{n}" for n in bad]
enforce(fail)

write_atomic(_os.path.join(_HERE, "palette.json"),
             json.dumps({"dark": DARK, "light": LIGHT}, indent=1))

OUT = os.path.expanduser("~/.config/ghostty/themes")
os.makedirs(OUT, exist_ok=True)
for fname, P in (("umber", DARK), ("umber-light", LIGHT)):
    hdr = (f"# Umber{' Light' if 'light' in fname else ''} — an earth palette.\n"
           "# Accents placed in OKLrCH. Warm hues carry more chroma than cool ones so the\n"
           "# palette has a centre of gravity; chroma is further weighted by how each slot\n"
           "# is actually used, so persistent chrome never outshouts semantic colour.\n\n")
    body = (f"background = {P['background']}\nforeground = {P['foreground']}\n"
            f"cursor-color = {P['cursor']}\ncursor-text = {P['background']}\n"
            f"selection-background = {P['selection']}\nselection-foreground = {P['foreground']}\n\n")
    write_atomic(os.path.join(OUT, fname),
                 hdr + body + "\n".join(f"palette = {i}={P[i]}" for i in range(16)) + "\n")
print("wrote umber, umber-light")
