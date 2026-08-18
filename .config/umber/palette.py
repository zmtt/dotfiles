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


def encode(c):
    c = max(0.0, min(1.0, c))
    return 12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055


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


def enforce(failures):
    """Stop before writing if any floor was missed.

    Every emitter gates the same way. Naming the failures beats the bare
    "contrast floor violated" each one used to raise, which said nothing about
    which variant or which check.
    """
    if failures:
        raise SystemExit("not shipping — floor violated: " + ", ".join(failures))
