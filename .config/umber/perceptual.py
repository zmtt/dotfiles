import math
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

def solve(target, bg, C, H):
    """Binary-search Lr until the colour hits a WCAG contrast target on bg."""
    dark = lum(bg) < 0.18
    lo, hi = (0.30, 0.995) if dark else (0.02, 0.70)
    for _ in range(70):
        mid = (lo + hi) / 2
        if (contrast(hex_lr(mid, C, H)[0], bg) < target) == dark: lo = mid
        else: hi = mid
    return hex_lr((lo + hi) / 2, C, H)[0]

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
