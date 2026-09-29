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


def enforce(failures, what="floor violated"):
    """Stop before writing if any floor was missed.

    Every emitter gates the same way. Naming the failures beats the bare
    "contrast floor violated" each one used to raise, which said nothing about
    which variant or which check. `what` is for the gates that are not floors:
    delta.py also refuses on a config key that would pin its own output out.
    """
    if failures:
        raise SystemExit(f"not shipping — {what}: " + ", ".join(failures))


def apca(text, ground):
    """APCA 0.0.98G lightness contrast |Lc| of text on ground.

    WCAG 2 overstates contrast near black, so on the dark ground a 4.5:1 pair
    can read far weaker than the same ratio on the light one. This is the
    perceptual check the ratio cannot give; it gates alongside contrast().
    """
    def y(hx):
        r, g, b = (int(hx[i:i+2], 16) / 255 for i in (1, 3, 5))
        v = 0.2126729 * r**2.4 + 0.7151522 * g**2.4 + 0.0721750 * b**2.4
        return v if v > 0.022 else v + (0.022 - v) ** 1.414
    yt, yb = y(text), y(ground)
    if yb > yt:
        s = (yb**0.56 - yt**0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (yb**0.65 - yt**0.62) * 1.14
    return 0.0 if s > -0.1 else -(s + 0.027) * 100
