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


def audit(V, S):
    """Every syntax role must clear the readable floor on its own ground."""
    bg = V["background"]
    floor = 4.5
    bad = [(k, round(contrast(v, bg), 2)) for k, v in S.items()
           if contrast(v, bg) < floor]
    return bad
