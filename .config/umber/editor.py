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

Levelling chroma is only half of it. Hue, chroma and lightness are the three
axes that hold roles apart, dichromacy destroys hue, and a single flat contrast
target destroys lightness — leaving nothing. That is what model.STAGGER exists
to prevent on the terminal side, and re-levelling chroma here without an
equivalent reintroduced it exactly: the high-frequency roles shipped at a
worst-case separation of 0.004 (light, tritanopia, function against type) while
the terminal accents alongside them held 0.035 or better.
"""
from perceptual import hex_lr, lch, solve, worst_separation
from palette import contrast, lum
from model import EMBER, SEPARATION_FLOOR

# Roughly even chroma: no structural role may be muted relative to another.
# Errors sit higher because they are rare and must interrupt.
SYNTAX_C = 0.100
ERROR_C = 0.130

# Lightness stagger, as multipliers on each role's contrast target rather than
# absolute Lr — for the same reason the targets themselves are contrast-based:
# the ground differs between variants and a fixed Lr would drift. Solved by
# optimise-stagger.py against both variants at once. Only the roles that carry
# a distinct hue appear here; see FAMILY.
ROLE_STAGGER = {"keyword": 1.110, "function": 1.082, "type": 0.827,
                "string": 0.981, "number": 0.825, "error": 1.169,
                "member": 0.914}

# Roles that are deliberately the same hue and lightness as another, differing
# only in chroma. They are family members rather than competing signals, so they
# follow their head's offset instead of getting one of their own, and they are
# excluded from the separation gate because they cannot be pulled apart.
FAMILY = {"constant": "number", "escape": "type"}


def syntax(V, stagger=None):
    """Editor accents keyed by role, derived from the palette's own hues.

    `stagger` overrides ROLE_STAGGER, which is how optimise-stagger.py measures
    a candidate set against the real derivation instead of a copy of it.
    """
    st = ROLE_STAGGER if stagger is None else stagger
    bg = V["background"]
    dark = lum(bg) < 0.18
    hue = {name: lch(V[slot])[2] for name, slot in (
        ("red", "1"), ("green", "2"), ("yellow", "3"),
        ("blue", "4"), ("magenta", "5"), ("cyan", "6"))}

    # Contrast targets, not lightness targets: the ground differs between
    # variants, and a fixed Lr would drift.
    body = 7.6 if dark else 6.2
    quiet = 6.4 if dark else 5.2
    fg_h = lch(V["foreground"])[2]

    # role -> (contrast target, hue, chroma). One table so the stagger applies
    # in one place.
    spec = {
        "keyword":  (body, hue["magenta"], SYNTAX_C),
        "function": (body, hue["blue"], SYNTAX_C),
        "type":     (body, hue["cyan"], SYNTAX_C),
        "string":   (quiet, hue["green"], SYNTAX_C),
        "number":   (body, hue["yellow"], SYNTAX_C),
        "constant": (body, hue["yellow"], SYNTAX_C * 1.15),
        "escape":   (body, hue["cyan"], SYNTAX_C * 0.85),
        "error":    (body, hue["red"], ERROR_C),
        # Instance variables and properties. Green, on the content side of the
        # taxonomy the editor accents use: warm is content (strings green,
        # literals yellow, errors red), cool is structure (keywords magenta,
        # functions blue, types cyan). The old whisper cyan at C 0.045 measured
        # 0.032 from param and 0.035 from keyword under simulated deficiency on
        # the dark ground — at or under the floor — because cyan is boxed in
        # between function, keyword and the plain foreground. Full chroma
        # because it is a real role carrying real tokens (ivars, properties,
        # instance fields), not a whisper, and it is separated from string —
        # the other green — by the lightness step the stagger provides.
        "member":   (9.2 if dark else 8.0, hue["green"], SYNTAX_C),
        "param":    (9.6 if dark else 8.6, hue["yellow"], 0.030),
        # Punctuation separates identifiers; it should not compete with them.
        # Below the foreground, above the comments.
        "punct":    (6.2 if dark else 5.4, fg_h, 0.012),
        "muted":    (5.0 if dark else 4.8, fg_h, 0.014),
    }
    return {role: solve(target * st.get(FAMILY.get(role, role), 1.0), bg, C, h)
            for role, (target, h, C) in spec.items()}


def separation(S, foreground=None):
    """Worst-case separation among the roles that carry a distinct hue.

    ROLE_STAGGER's keys are exactly those roles: a FAMILY member follows a head
    rather than holding an offset, so it never appears there.

    `foreground` joins the set when given: plain text is a colour every role
    has to stay distinguishable from.
    """
    cand = {k: v for k, v in S.items() if k in ROLE_STAGGER}
    if foreground is not None:
        cand["plain"] = foreground
    return worst_separation(cand)


def audit(V, S, floor=4.5):
    """Every syntax role must clear the readable floor on its own ground, and
    the distinct-hue roles must stay apart under colour-vision deficiency.

    Surfaces are audited by each emitter; this covers the accents, which
    otherwise ship unchecked. Contrast alone was checked here while the roles
    sat at one flat lightness, which contrast cannot see: every role passed at
    7.6:1 while two hues sat a dE of 0.004 apart for a dichromat. Findings are
    (name, measurement) either way, so callers collect both the same way."""
    bg = V["background"]
    bad = [(k, round(contrast(v, bg), 2)) for k, v in S.items()
           if contrast(v, bg) < floor]
    dE, pair = separation(S, V["foreground"])
    if dE < SEPARATION_FLOOR:
        bad.append((f"separation {pair[0]}/{pair[1]} {pair[2]}", round(dE, 4)))
    return bad


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
