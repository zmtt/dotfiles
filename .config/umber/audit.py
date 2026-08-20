import json, math
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
from palette import contrast, lum
from perceptual import to_linear, linear_to_oklab, worst_separation
from model import FLOOR, SEPARATION_FLOOR
P = json.load(open(_os.path.join(_HERE, "palette.json")))
def blend(f,b,a):
    F=[int(f[i:i+2],16) for i in (1,3,5)]; B=[int(b[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(round(F[k]*a+B[k]*(1-a)) for k in range(3))
_fail = []
for v in ("dark","light"):
    V=P[v]; bg=V["background"]; f=FLOOR[v]
    text=[i for i in range(16) if i not in ((0,7,15) if v=="light" else (0,))]
    checks=[("body",contrast(V["foreground"],bg)),
            ("comments",contrast(V["8"],bg)),
            ("dimmest",min(contrast(V[str(i)],bg) for i in text)),
            ("faint",contrast(blend(V["foreground"],bg,0.72),bg)),
            ("selection",contrast(V["foreground"],V["selection"])),
            ("cursor",contrast(V["cursor"],bg))]
    bad=[n for n,x in checks if x < f*(0.66 if n=="faint" else 1.0)]
    _fail += [f"{v}:{n}" for n in bad]
    ch={}
    for i,n in ((1,'red'),(2,'green'),(3,'yellow'),(4,'blue'),(5,'magenta'),(6,'cyan')):
        L,a,b=linear_to_oklab(*to_linear(V[str(i)])); ch[n]=math.hypot(a,b)
    ok = min(ch['red'],ch['yellow']) > max(ch['cyan'],ch['blue'],ch['magenta'])
    if not ok: _fail.append(f"{v}:salience")
    sep, pair = worst_separation({n: V[str(i)] for i, n in
        ((1,'red'),(2,'green'),(3,'yellow'),(4,'blue'),(5,'magenta'),(6,'cyan'))})
    if sep < SEPARATION_FLOOR: _fail.append(f"{v}:separation {pair[0]}/{pair[1]} {pair[2]}")
    print(f"{v:<6} " + " ".join(f"{n} {x:5.2f}" for n,x in checks))
    print(f"       floor {f}  {'PASS' if not bad else 'BELOW: '+str(bad)}   "
          f"salience {'HOLDS' if ok else 'VIOLATED'}   separation {sep:.4f}   "
          f"peak lum {lum(V['15']):.3f}")

if _fail:
    raise SystemExit(f"audit failed {_fail} — palette is not shippable")
