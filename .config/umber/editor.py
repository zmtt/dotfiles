"""Editor-side accent derivation, shared by the neovim/xcode/intellij emitters.

A terminal and an editor need opposite weightings and cannot share one accent
set. In a terminal, colour marks the exceptional: errors, modified files, diff
markers. Warm hues therefore carry chroma and cool hues recede as chrome, which
is what palette.json encodes.

In an editor almost every glyph is coloured, and the high-frequency tokens are
keywords, functions and types. Reusing the terminal slots paints that scaffold
in the three most desaturated colours in the palette (blue 0.059, cyan 0.062,
magenta 0.069) while strings and literals sit at 0.128, so code reads as beige
with the strings shouting.

So the hue geometry is inherited, keeping the family resemblance, but chroma is
re-levelled for editor frequency and punctuation is pushed down below the
identifiers it separates.
"""
from perceptual import hex_lr, lch, solve
from palette import contrast, lum
from model import EMBER

# Roughly even chroma: no structural role may be muted relative to another.
# Errors sit higher because they are rare and must interrupt.
SYNTAX_C = 0.100
ERROR_C = 0.130


def syntax(V):
    """Editor accents keyed by role, derived from the palette's own hues."""
    bg = V["background"]
    dark = lum(bg) < 0.18
    hue = {name: lch(V[slot])[2] for name, slot in (
        ("red", "1"), ("green", "2"), ("yellow", "3"),
        ("blue", "4"), ("magenta", "5"), ("cyan", "6"))}

    # Contrast targets, not lightness targets: the ground differs between
    # variants, and a fixed Lr would drift.
    body = 7.6 if dark else 6.2
    quiet = 6.4 if dark else 5.2

    def at(target, h, C=SYNTAX_C):
        return solve(target, bg, C, h)

    fg_h = lch(V["foreground"])[2]
    return {
        "keyword":  at(body, hue["magenta"]),
        "function": at(body, hue["blue"]),
        "type":     at(body, hue["cyan"]),
        "string":   at(quiet, hue["green"]),
        "number":   at(body, hue["yellow"]),
        "constant": at(body, hue["yellow"], SYNTAX_C * 1.15),
        "escape":   at(body, hue["cyan"], SYNTAX_C * 0.85),
        "error":    at(body, hue["red"], ERROR_C),
        # Members read as a distinct family from plain locals without becoming
        # a seventh competing hue.
        "member":   at(9.2 if dark else 8.0, hue["cyan"], 0.045),
        "param":    at(9.6 if dark else 8.6, hue["yellow"], 0.030),
        # Punctuation separates identifiers; it should not compete with them.
        # Below the foreground, above the comments.
        "punct":    solve(6.2 if dark else 5.4, bg, 0.012, fg_h),
        "muted":    solve(5.0 if dark else 4.8, bg, 0.014, fg_h),
    }


def audit(V, S, floor=4.5):
    """Every syntax role must clear the readable floor on its own ground.

    Surfaces are audited by each emitter; this covers the accents, which
    otherwise ship unchecked."""
    bg = V["background"]
    return [(k, round(contrast(v, bg), 2)) for k, v in S.items()
            if contrast(v, bg) < floor]


def surfaces(V):
    """The near-background ramp every editor needs: current line, panels, diff
    washes, search. Derived here rather than per emitter, so a wash tuned once
    cannot drift between Neovim, Android Studio and Xcode."""
    bg = V["background"]
    dark = lum(bg) < 0.18
    bglr, nh = lch(bg)[0], lch(V["foreground"])[2]
    d = 1 if dark else -1
    n = lambda off, C=0.017: hex_lr(bglr + d * off, C, nh)[0]
    hue = {k: lch(V[s])[2] for k, s in (("red", "1"), ("green", "2"), ("yellow", "3"))}
    return {
        "line": n(0.045), "panel": n(0.075), "over": n(0.115, 0.019),
        "ghost":  solve(1.45 if dark else 1.55, bg, 0.014, nh),
        "linenr": solve(1.9 if dark else 2.2, bg, 0.018, nh),
        "add":    hex_lr(bglr + d * 0.070, 0.028, hue["green"])[0],
        "change": hex_lr(bglr + d * 0.070, 0.024, hue["yellow"])[0],
        "delete": hex_lr(bglr + d * 0.060, 0.030, hue["red"])[0],
        "text":   hex_lr(bglr + d * 0.135, 0.045, hue["yellow"])[0],
        "search": hex_lr(bglr + d * 0.160, 0.060, EMBER)[0],
    }
