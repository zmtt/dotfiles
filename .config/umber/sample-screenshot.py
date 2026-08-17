"""Census the colours in a real Ghostty screenshot.

Rendering is the ground truth the numbers only approximate. This finds the
fully-covered cores of coloured glyphs and reports their chroma and hue, so a
screenshot can be checked against palette.json directly.

Needs pillow:  python3 -m venv .venv && .venv/bin/pip install pillow
Then:          .venv/bin/python sample-screenshot.py <path-to-png>
"""
import sys, math, json
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
from collections import Counter
from PIL import Image
from palette import contrast
from perceptual import to_linear, linear_to_oklab

path = sys.argv[1]
ground = sys.argv[2] if len(sys.argv) > 2 else json.load(open(_os.path.join(_HERE, "palette.json")))["dark"]["background"]
im = Image.open(path).convert("RGB")
hexs = lambda t: "#%02x%02x%02x" % t

cand = Counter()
for p in im.getdata():
    if max(p) - min(p) < 26 or sum(p) < 250:
        continue
    cand[p] += 1

print(f"ground {ground}   {im.size[0]}x{im.size[1]}")
print(f"{'colour':<10}{'count':>8}{'contrast':>11}  chroma    hue")
for rgb, n in cand.most_common(14):
    hx = hexs(rgb)
    L, a, b = linear_to_oklab(*to_linear(hx))
    print(f"{hx:<10}{n:>8}{contrast(hx, ground):9.2f}:1  {math.hypot(a,b):.3f}  {math.degrees(math.atan2(b,a))%360:5.1f}")
