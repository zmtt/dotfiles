import contextlib
import itertools
import math
import os
import tempfile
from palette import oklch_to_srgb, in_gamut, encode, lum, contrast

# ---- OKLr: Ottosson's toe correction. Plain Oklab L is not perceptually
# uniform in the darks; Lr fixes that, which matters a lot for a dark theme.
K1, K2 = 0.206, 0.03
K3 = (1 + K1) / (1 + K2)

def lr_to_l(lr):
    return (lr * (lr + K1)) / (K3 * (lr + K2))

def l_to_lr(l):
    return 0.5 * (K3*l - K1 + math.sqrt((K3*l - K1)**2 + 4*K2*K3*l))

def gamut_map_lr(lr, C, H):
    L = lr_to_l(lr)
    if in_gamut(oklch_to_srgb(L, C, H)):
        return C, False
    lo, hi = 0.0, C
    for _ in range(60):
        mid = (lo + hi) / 2
        if in_gamut(oklch_to_srgb(L, mid, H)): lo = mid
        else: hi = mid
    return lo, True

def hex_lr(lr, C, H):
    """Specify colour in OKLrCH; return sRGB hex."""
    C2, clipped = gamut_map_lr(lr, C, H)
    r, g, b = oklch_to_srgb(lr_to_l(lr), C2, H)
    return "#%02x%02x%02x" % tuple(round(encode(c)*255) for c in (r, g, b)), clipped, C2

def lch(hx):
    """sRGB hex -> (Lr, C, H)."""
    L, a, b = linear_to_oklab(*to_linear(hx))
    return l_to_lr(L), math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360

def solve_lr(target, bg, C, H):
    """Binary-search Lr until the colour hits a WCAG contrast target on bg.

    The bracket is the full Lr range. A narrower one silently returns its own
    bound when the target is unreachable, which reads as a solved value and
    makes the target look like a knob when it is not: dark slot 0 (target 1.55)
    used to emit #4f433a at 1.891:1.
    """
    dark = lum(bg) < 0.18
    lo, hi = (0.0, 1.0)
    if not (contrast(hex_lr(lo, C, H)[0], bg) - target) * (contrast(hex_lr(hi, C, H)[0], bg) - target) <= 0:
        reach = sorted(round(contrast(hex_lr(x, C, H)[0], bg), 3) for x in (lo, hi))
        raise ValueError(f"contrast target {target} unreachable at C={C:.3f} H={H:.1f} "
                         f"on {bg}; reachable range is {reach[0]}..{reach[1]}")
    for _ in range(70):
        mid = (lo + hi) / 2
        if (contrast(hex_lr(mid, C, H)[0], bg) < target) == dark: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def solve(target, bg, C, H):
    """As solve_lr, returning the hex."""
    return hex_lr(solve_lr(target, bg, C, H), C, H)[0]


def write_atomic(path, data):
    """Write via a temp file in the same directory, then rename.

    `open(path, "w").write(render())` truncates the target before render() runs,
    so any failure mid-render leaves a zero-byte theme in the live config.
    Text or binary follows from the payload; callers do not pick a file mode.
    """
    # Resolve first: os.replace swaps the symlink itself, where a plain write
    # would have gone through it.
    path = os.path.realpath(path)
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    mode = os.stat(path).st_mode & 0o777 if os.path.exists(path) else None
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".umber-", suffix=".tmp")
    try:
        binary = isinstance(data, bytes)
        with os.fdopen(fd, "wb" if binary else "w",
                       **({} if binary else {"encoding": "utf-8"})) as f:
            f.write(data)
        # mkstemp forces 0600 and ignores umask; without this the rename would
        # silently downgrade the mode of a file we did not create.
        os.chmod(tmp, mode if mode is not None else 0o644)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise

# ---- colour-vision-deficiency simulation (Viénot 1999, linear RGB) ----
CVD = {
 "protanopia":   ((0.11238, 0.88762, 0.0), (0.11238, 0.88762, 0.0), (0.00401, -0.00401, 1.0)),
 "deuteranopia": ((0.29275, 0.70725, 0.0), (0.29275, 0.70725, 0.0), (-0.02234, 0.02234, 1.0)),
 "tritanopia":   ((1.0, 0.14461, -0.14461), (0.0, 0.85659, 0.14341), (0.0, 0.85659, 0.14341)),
}

def to_linear(hx):
    out = []
    for i in (1, 3, 5):
        v = int(hx[i:i+2], 16) / 255
        out.append(v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4)
    return out

def linear_to_oklab(r, g, b):
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l_, m_, s_ = [max(v, 0.0)**(1/3) for v in (l, m, s)]
    return (0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_,
            1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_,
            0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_)

def simulate(hx, kind):
    r, g, b = to_linear(hx)
    M = CVD[kind]
    return [M[i][0]*r + M[i][1]*g + M[i][2]*b for i in range(3)]

def delta_e(hx1, hx2, kind=None):
    def lab(h):
        return linear_to_oklab(*(simulate(h, kind) if kind else to_linear(h)))
    a, b = lab(hx1), lab(hx2)
    return math.dist(a, b)


CVD_KINDS = tuple(CVD)


def worst_separation(colours, kinds=CVD_KINDS):
    """Closest pair among `colours`, across every simulated deficiency.

    Takes a {name: hex} mapping and returns (dE, (name_a, name_b, kind)).

    Near-uniform lightness is what collapses distinct hues for a dichromat, so
    this single measurement is what both stagger solvers maximise and what both
    gates enforce. It lived only inside optimise-stagger.py, which meant the
    editor accents — derived by a different path, with no stagger at all — were
    never measured by it and shipped at dE 0.004 to 0.007.
    """
    names = list(colours)
    # Convert once per colour per deficiency, not once per pair. delta_e converts
    # both operands on every call, so six colours across three deficiencies cost
    # 90 conversions where 18 suffice, and this is the inner loop of both stagger
    # solvers.
    lab = {(n, k): linear_to_oklab(*(simulate(colours[n], k) if k
                                     else to_linear(colours[n])))
           for n in names for k in kinds}
    worst, pair = float("inf"), None
    for kind in kinds:
        for a, b in itertools.combinations(names, 2):
            d = math.dist(lab[(a, kind)], lab[(b, kind)])
            if d < worst:
                worst, pair = d, (a, b, kind)
    return worst, pair
