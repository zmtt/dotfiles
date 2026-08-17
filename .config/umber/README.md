# Umber — palette source

The three Ghostty themes in ~/.config/ghostty/themes (`umber`, `umber-night`,
`umber-light`) plus the Claude Code themes are generated, not hand-written.
Editing the theme files directly works but loses the guarantees below; edit the
knobs here and rebuild instead.

```
python3 build.py          # the three Ghostty themes
python3 audit.py          # every contrast floor and the salience order
python3 claude-chrome.py  # ~/.claude/themes/umber{,-light}.json
python3 neovim.py         # ~/.config/nvim/colors + lualine themes
python3 intellij.py       # Android Studio .icls editor schemes
python3 jetbrains-ui.py   # Android Studio UI theme plugin (umber-theme.jar)
python3 xcode.py          # ~/Library/Developer/Xcode/UserData/FontAndColorThemes
python3 bat-theme.py      # bat/delta .tmTheme, rebuilds bat's cache

python3 render-specimen.py && rsvg-convert -w 2400 specimen.svg -o specimen.png
python3 render-code.py    && rsvg-convert -w 2400 code.svg -o code.png
```

The two renderers matter more than they look. The palette went through three
revisions that every number approved of and that looked lifeless the first time
it was actually rendered and viewed. **Numbers cannot tell you a palette is
flat.** Render it and look before believing an audit.

To check a real screenshot rather than a render:

```
python3 -m venv .venv && .venv/bin/pip install pillow
.venv/bin/python sample-screenshot.py ~/Desktop/shot.png
```

It reports the chroma and hue of every colour actually on screen, which is how
the palette was confirmed to reach eza, starship and fish unaltered.

`build.py` is authoritative: rebuilding always reproduces the shipped files
byte-for-byte unless a knob changed.

## bat and delta are a syntax surface too

Both highlight through Sublime `.tmTheme` files and both default to Monokai
Extended. With delta as the git pager that meant every diff read on this machine
rendered in an unrelated palette. `bat-theme.py` emits Umber `.tmTheme` files;
`~/.config/bat/config` and `git config delta.syntax-theme` select them.

## Android Studio needs two artefacts, not one

An `.icls` themes only the editor pane. The surrounding IDE — tool windows,
tabs, sidebar, status bar — comes from a UI theme, which JetBrains loads only
from a plugin. An Umber editor scheme inside a Solarized UI theme puts two
colour temperatures in one window, and no editor scheme can fix that.

`jetbrains-ui.py` composes the plugin directly. A theme plugin is pure
resources, so there is no Gradle and no compilation.

The key structure is read out of the installed Android Studio at build time
(`themes/expUI/expUI_dark.theme.json` inside the platform jar) rather than
vendored here, so the platform's file stays where it is licensed and new UI keys
arrive with Studio updates. That theme is built from eight ramps — Gray, Blue,
Green, Red, Purple, Teal, Yellow, Orange — each running dark to light, and its
`ui` block references them by name with no raw hex. Retinting the ramps
therefore replaces the theme completely: each step keeps its own lightness and
its position within its ramp, and takes Umber's hue and chroma for that family.
Orange maps to the ember.

Note that `lch()` returns **Lr**, not Oklab `L`. Passing its result through
`l_to_lr()` applies the toe correction twice and darkens everything.

The plugin's `editorBackground`, its `activeTabBackground`, the scheme's `TEXT`
background and its `GUTTER_BACKGROUND` must all carry the same value, or a seam
shows where the editor meets its own tab.

## Editors do not share the terminal's accent set

`editor.py` derives a second accent set for the editor emitters, and it exists
because the two weightings are opposites.

In a terminal, colour marks the exceptional, so warm hues carry chroma and cool
hues recede as chrome. In an editor nearly every glyph is coloured and the
high-frequency tokens are keywords, functions and types. Reusing the terminal
slots paints that scaffold in the three most desaturated colours in the palette
(blue 0.059, cyan 0.062, magenta 0.069) while strings and literals sit at 0.128
— code reads as beige with the strings shouting.

So editors inherit the hue geometry, keeping the family resemblance, but chroma
is re-levelled (spread 0.068 → 0.001) and punctuation is pushed below the
identifiers it separates. `render-code.py` renders a before/after specimen.

## Design rules the generator enforces

**Colours are placed in OKLrCH, not picked.** Plain Oklab lightness is not
perceptually even in the darks, which is where a dark theme lives, so everything
uses Ottosson's toe-corrected `Lr`.

**Warm hues carry more chroma than cool ones.** This gives the palette a centre
of gravity instead of an even spread. Chroma peaks at hue 48 (the ember) and
falls toward the blues.

**Chroma is then weighted by how a slot is used.** Red and yellow are semantic —
untracked files, modified files, errors — and must catch the eye. Magenta and
blue are mostly chrome: branch names, task labels. Persistent chrome must never
be the loudest thing on screen.

**Two different metrics, checked separately.** WCAG contrast measures whether
text can be *read* (floor 4.5:1, or 3.3:1 for the night variant). Chroma
measures whether it *catches the eye*. `audit.py` checks both — a change that
improves one can silently break the other.

## The knobs, in `build.py`

| Knob | Effect |
|---|---|
| `C_WARM` / `C_COOL` | Overall saturation of warm vs cool hues |
| `PEAK` | Hue where chroma is highest — the ember, currently 48 |
| `USAGE` | Per-hue loudness weight. Lower = more recessive |
| `HUES` | Hue angle per ANSI slot |
| `STAGGER` | Per-hue lightness offset, for colour-vision separation |
| `bg_hex` | Ground for each variant |
| `targets` | Contrast targets the neutral ramp is solved to |

`optimise-stagger.py` re-solves `STAGGER` if you change the chroma model. It
searches for maximum worst-case separation across deuteranopia, protanopia and
tritanopia while keeping the lightness spread small.

## After any change

Run `audit.py`. It fails loudly rather than shipping a palette that reads well
in a swatch grid and badly in a terminal.

`adjust-cell-height = 12%` was verified against both JetBrains Mono and Monaspace
Neon and is correct for either. Monaspace has a 5.7% shorter natural line height
but a smaller x-height, and the two cancel: line height per x-height lands at
2.688 vs 2.679. Do not re-derive this from the em box alone, which suggests a
change that perceived crowding does not want.

One caveat the numbers do not capture: measured from a real screenshot, a
glyph's *mean* contrast is roughly half its nominal value, because most of its
pixels are antialiased edge rather than solid fill. The floors here assume that
headroom exists. Do not lower them on the theory that 4.5:1 is comfortable — on
screen that is closer to 2.5:1.
