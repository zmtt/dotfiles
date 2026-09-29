"""Build the variant-dependent half of delta's configuration.

delta is the git pager, so every diff read on this machine goes through it. The
ANSI-named half of its theming lives in ~/.config/git/common.conf and needs no
generation: named slots resolve against whichever Ghostty palette is loaded, so
they follow the variant for free. Everything here is the half that cannot work
that way — a background wash and a syntax-theme name are concrete values, and
the right one depends on which variant is active.

delta cannot pick for itself. It does detect a dark or light terminal
(--detect-dark-light), but detection only flips its own built-in defaults: it
cannot activate a named feature or select a custom syntax-theme, which is where
everything below lives. The choice therefore has to be made before delta starts,
which is what ~/.config/git/umber-delta does on each invocation.

Three traps, all measured rather than assumed, and all now gated rather than
left to a comment:

  - The main [delta] section overrides a feature, not the other way round. A
    key set in both places is pinned to the main section's value and the
    feature silently does nothing. This has already happened once, to
    syntax-theme, so collisions() fails the build on it.
  - minus-non-emph-style follows minus-style on its own, but the empty-line
    markers do not: left alone they keep delta's #3f0001 / #002800, which is
    how a blank added line ends up in a colour from outside the palette.
  - The washes cannot carry a diff for a dichromat. At chroma 0.030 the
    red/green pair sits at a deuteranopic separation of 0.008 dark and 0.011
    light against model.SEPARATION_FLOOR of 0.035, and no hue rotation reaches
    the floor at that chroma without failing tritanopia instead. The red/green
    gutter numbers are what clears it, at 0.046/0.045, so gutter() gates their
    separation and the line-numbers setting that draws them at all.

The washes are editor.surfaces()'s add/delete, the same two Neovim and Android
Studio already paint diffs with, so a diff looks the same wherever it is read.
"""
import json
import os
import subprocess

from editor import surfaces
from palette import contrast, enforce
from perceptual import lch, worst_separation, write_atomic
from model import FLOOR, SEPARATION_FLOOR

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "palette.json")))
OUT = os.path.expanduser("~/.config/git/umber-delta.conf")

# Feature name per variant, and the .tmTheme bat-theme.py emits for it.
VARIANTS = {"dark": ("umber-dark", "Umber"), "light": ("umber-light", "Umber Light")}


def grounds(variant):
    """Every concrete background this file introduces, derived once.

    The gate and the emitted config must read the same values from the same
    place. Deriving them separately is the mirrored-copy failure model.py exists
    to prevent, and it fails silently in the direction that matters: the audit
    passes on the colour it recomputed while the config carries the other one.
    """
    S = surfaces(P[variant])
    return {"minus": S["delete"], "plus": S["add"],
            "blame": (S["line"], S["panel"], S["over"])}


def entries(variant):
    """The feature's keys and values. block() renders these and collisions()
    checks their names, so what this file emits has one definition."""
    G = grounds(variant)
    minus, plus = G["minus"], G["plus"]
    return [
        (variant, "true"),
        ("syntax-theme", f'"{VARIANTS[variant][1]}"'),
        ("minus-style", f'syntax "{minus}"'),
        ("plus-style", f'syntax "{plus}"'),
        # Blank changed lines have no glyph to carry syntax colour, so the wash
        # is the whole signal and has to be stated separately.
        ("minus-empty-line-marker-style", f'normal "{minus}"'),
        ("plus-empty-line-marker-style", f'normal "{plus}"'),
        # Cycled per commit block under `delta --blame`, so these want to be
        # neutral steps that separate adjacent commits, not semantic colour.
        # Quoted because git config ends a value at an unquoted '#', which
        # leaves delta reading an empty palette and refusing to start.
        ("blame-palette", f'"{" ".join(G["blame"])}"'),
    ]


def block(variant):
    return "\n".join([f'[delta "{VARIANTS[variant][0]}"]']
                     + [f"    {k} = {v}" for k, v in entries(variant)])


def git_config(*args):
    """git's own view of the config, which is the one delta will get.

    Parsing the .conf files directly would miss the includes that carry most of
    this and the case folding git applies to key names.
    """
    return subprocess.run(["git", "config", *args],
                          capture_output=True, text=True, cwd=HERE).stdout


def collisions():
    """Emitted keys that a main [delta] section also sets, and so pins out.

    Main-section keys are the ones with a single segment after "delta."; a
    feature's are "delta.<feature>.<key>".
    """
    main = {line.split(" ", 1)[0].split(".", 1)[1]
            for line in git_config("--get-regexp", r"^delta\.[^.]+$").splitlines()
            if line}
    emitted = {k for v in VARIANTS if v in P for k, _ in entries(v)}
    return sorted(main & emitted)


def gutter(variant):
    """Separation of the red/green line numbers, the channel a dichromat reads
    the diff by once the washes have collapsed. Shaped like audit()'s findings
    so the two collect together."""
    dE, _ = worst_separation({"minus": P[variant]["1"], "plus": P[variant]["2"]})
    return (f"{variant}:gutter", dE, SEPARATION_FLOOR)


def audit(variant):
    """Text must stay readable on every ground this file introduces."""
    G = grounds(variant)
    fg, floor = P[variant]["foreground"], FLOOR[variant]
    checked = [("minus", G["minus"]), ("plus", G["plus"])]
    checked += [(f"blame{i}", g) for i, g in enumerate(G["blame"], 1)]
    return [(f"{variant}:{name}", contrast(fg, g), floor) for name, g in checked]


if __name__ == "__main__":
    variants = [v for v in VARIANTS if v in P]
    checks = [c for v in variants for c in audit(v)] + [gutter(v) for v in variants]
    enforce([name for name, got, floor in checks if got < floor])

    wrong = [f"main [delta] also sets {k}" for k in collisions()]
    if git_config("--get", "delta.line-numbers").strip() != "true":
        wrong.append("delta.line-numbers is off, leaving only the washes, which "
                     f"sit under {SEPARATION_FLOOR} for a deuteranope")
    enforce(wrong, "config would defeat this file")

    header = ("# Generated by ~/.config/umber/delta.py — do not edit.\n"
              "# The ANSI-named delta settings live in common.conf; only the values that\n"
              "# differ between variants are here. Selected by DELTA_FEATURES, which\n"
              "# ~/.config/git/umber-delta sets from the macOS appearance.\n\n")
    body = "\n\n".join(block(v) for v in variants)
    write_atomic(OUT, header + body + "\n")

    for variant in variants:
        G = grounds(variant)
        fg = P[variant]["foreground"]
        print(f"  {VARIANTS[variant][0]:<12} "
              f"minus {G['minus']} {contrast(fg, G['minus']):5.2f}:1   "
              f"plus {G['plus']} {contrast(fg, G['plus']):5.2f}:1   "
              f"C {lch(G['minus'])[1]:.3f}/{lch(G['plus'])[1]:.3f}   "
              f"gutter dE {gutter(variant)[1]:.4f}")
    print(f"\nwrote {OUT.replace(os.path.expanduser('~'), '~')}")
