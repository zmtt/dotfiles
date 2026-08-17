import math

def oklch_to_srgb(L, C, H):
    h = math.radians(H); a = C*math.cos(h); b = C*math.sin(h)
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bl= -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    return (r, g, bl)

def in_gamut(rgb, eps=1e-4):
    return all(-eps <= c <= 1+eps for c in rgb)

def gamut_map(L, C, H):
    """Binary-search chroma down until the colour fits in sRGB."""
    if in_gamut(oklch_to_srgb(L, C, H)):
        return C, False
    lo, hi = 0.0, C
    for _ in range(60):
        mid = (lo+hi)/2
        if in_gamut(oklch_to_srgb(L, mid, H)): lo = mid
        else: hi = mid
    return lo, True

def encode(c):
    c = max(0.0, min(1.0, c))
    return 12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055

def hexof(L, C, H):
    C2, clipped = gamut_map(L, C, H)
    rgb = oklch_to_srgb(L, C2, H)
    out = "#%02x%02x%02x" % tuple(round(encode(c)*255) for c in rgb)
    return out, clipped, C2

def lum(hx):
    def ch(v):
        v = int(hx[v:v+2], 16)/255
        return v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4
    r, g, b = ch(1), ch(3), ch(5)
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi+0.05)/(lo+0.05)
