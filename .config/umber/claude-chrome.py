from perceptual import hex_lr, l_to_lr, contrast
import json, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

P = json.load(open(_os.path.join(_HERE, "palette.json")))
D, L = P["dark"], P["light"]

def solve_on(base, target, C, H, up=True):
    lo, hi = (0.30, 0.995) if up else (0.02, 0.70)
    for _ in range(60):
        mid = (lo + hi) / 2
        if (contrast(hex_lr(mid, C, H)[0], base) < target) == up: lo = mid
        else: hi = mid
    return hex_lr((lo + hi) / 2, C, H)[0]

# The ground is near-neutral now, so the message box carries only a trace of
# warmth — enough to read as a panel rather than a patch of a different theme.
dark_box   = hex_lr(l_to_lr(0.300), 0.016, 58)[0]
dark_hover = hex_lr(l_to_lr(0.375), 0.019, 58)[0]
light_box   = hex_lr(l_to_lr(0.930), 0.014, 72)[0]
light_hover = hex_lr(l_to_lr(0.968), 0.010, 72)[0]

dark_label  = D["cursor"]
light_label = solve_on(light_box, 5.0, 0.135, 48, up=False)

for name, box, hover, V, inv, lbl in (
    ("dark",  dark_box,  dark_hover,  D, D["15"], dark_label),
    ("light", light_box, light_hover, L, L["0"],  light_label)):
    print(f"{name:<6} box {box}  hover {hover}  label {lbl}")
    print(f"       text {inv} on box {contrast(inv,box):5.2f}:1   "
          f"label on box {contrast(lbl,box):5.2f}:1   "
          f"box vs ground {contrast(box,V['background']):.2f}:1")

TD = os.path.expanduser("~/.claude/themes")
json.dump({"name":"Umber","base":"dark","overrides":{
    "userMessageBackground":dark_box,"userMessageBackgroundHover":dark_hover,
    "inverseText":D["15"],"briefLabelYou":dark_label}}, open(f"{TD}/umber.json","w"), indent=2)
json.dump({"name":"Umber Light","base":"light","overrides":{
    "userMessageBackground":light_box,"userMessageBackgroundHover":light_hover,
    "inverseText":L["0"],"briefLabelYou":light_label}}, open(f"{TD}/umber-light.json","w"), indent=2)
print(f"\nghostty ground {D['background']} / {L['background']}")
print("statusline:", " ".join(f"{k}={D[k]}" for k in ("1","2","3","5","6","8","0")))
