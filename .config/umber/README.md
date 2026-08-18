# Umber — palette source

One palette, generated in OKLrCH, retargeted to Ghostty, fish, Claude Code,
Neovim, Android Studio, Xcode and bat/delta. Nothing here is hand-picked hex.

## Something looks wrong: where to change it

Find the symptom, edit the middle column, run the right. Never edit a generated
theme file — the next rebuild overwrites it.

| Symptom | Edit | Then run |
|---|---|---|
| A colour is wrong **everywhere** at once | `model.py` (the knobs, below) | `build.py`, then every emitter |
| Comments dim, or an accent too loud | `build.py` `targets`, or `model.py` `USAGE` | `build.py`, then every emitter |
| Terminal font, spacing, ligatures, cursor | `~/.config/ghostty/config` *(source)* | reload Ghostty |
| Shell syntax colours: commands, errors | `~/.config/fish/conf.d/umber-theme.fish` *(source)* | new shell |
| Day/night switching (light follows macOS) | `~/.config/fish/functions/umber.fish` *(source)* | new shell |
| **Any editor's** syntax: keywords, types, strings | `editor.py` | the affected emitter |
| Neovim UI: floats, diffs, statusline | `neovim.py` | `python3 neovim.py` |
| Android Studio editor pane | `editor.py` or `intellij.py` | `python3 intellij.py && python3 jetbrains-ui.py`, restart |
| Android Studio chrome: tabs, sidebar, toolbar | `jetbrains-ui.py` `RAMPS` | `python3 jetbrains-ui.py`, restart |
| Xcode | `xcode.py` | `python3 xcode.py`, restart |
| `bat` output, or `git diff` through delta | `bat-theme.py` | `python3 bat-theme.py` |
| Claude Code prompt box, "You" label | `claude-chrome.py` | `python3 claude-chrome.py`, restart |
| Claude Code status line | `~/.claude/statusline-command.py` *(source)* | next turn |

## Generated versus source

Everything here is **output**. Editing it is pointless; the next rebuild wins.

```
~/.config/ghostty/themes/umber, umber-night, umber-light
~/.config/nvim/colors/umber*.lua
~/.config/nvim/lua/lualine/themes/umber*.lua
~/.config/bat/themes/Umber*.tmTheme
~/.claude/themes/umber.json, umber-light.json
~/Library/Application Support/Google/AndroidStudio*/colors/Umber*.icls
~/Library/Application Support/Google/AndroidStudio*/plugins/umber-theme.jar
~/Library/Developer/Xcode/UserData/FontAndColorThemes/Umber*.xccolortheme
~/.config/umber/palette.json               written by build.py, read by every emitter
~/.config/umber/stagger.json               written by optimise-stagger.py
~/.config/umber/{specimen,code}.svg        written by the renderers
```

These are **source**, edit directly:

```
~/.config/umber/*.py                       the generators
~/.config/ghostty/config                   font, spacing, ligatures, cursor
~/.config/fish/conf.d/umber-theme.fish     shell syntax colours
~/.config/fish/functions/umber.fish        the day/night/light switcher
~/.claude/statusline-command.py            the status line
~/.config/bat/config                       selects the bat/delta theme
~/.config/git/config                       [delta] syntax-theme
~/.config/nvim/lua/config/lazy.lua         selects the colorscheme
```

`check.py` verifies the lists above along with everything else:

```
python3 check.py          # classification, runs, idempotency, formats, modes,
                          # cross-emitter agreement, artefact-vs-git drift
python3 check.py --slow   # also runs the sampling optimiser
```

Its MANIFEST must classify every `.py` here, and it fails if one is missing —
so a script cannot be added without saying what it is, and cannot be silently
left out of the checks. Two renderers were broken for several rounds because
the hand-maintained list that preceded it did not include them.

The trap: `~/.claude/statusline-command.py` is hand-written source, while
`~/.claude/themes/umber*.json` sitting beside it is generated. Both are tracked
in the dotfiles repo, which makes them easy to confuse.

Android Studio's two emitters resolve the **newest** `AndroidStudio*` config
directory at runtime, so a Studio upgrade needs a rerun, not a path edit.

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

It reports the chroma and hue of the most common *saturated* colours on screen
— it deliberately skips near-neutrals, so the foreground and background never
appear — which is how the accents were confirmed to reach eza, starship and
fish unaltered.

`build.py` is authoritative: rebuilding reproduces every generated file
byte-for-byte unless a knob changed, the jar included (its zip entries carry a
fixed timestamp so the container is stable too).

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

Each theme declares `editorScheme: /themes/<variant>.xml`, a copy of the `.icls`
placed inside the jar. That copy is what Studio reads while the Umber UI theme is
selected, so an editor-pane change needs `intellij.py` **and then**
`jetbrains-ui.py`. Running `intellij.py` alone rewrites
`~/.../colors/Umber.icls`, which nothing is reading.

The key structure is read out of the installed Android Studio at build time
(`themes/expUI/expUI_dark.theme.json` inside the platform jar) rather than
vendored here, so the platform's file stays where it is licensed and new UI keys
arrive with Studio updates. That theme is built from eight ramps — Gray, Blue,
Green, Red, Purple, Teal, Yellow, Orange — each running dark to light, and its
`ui` block mostly references them by name. Retinting the ramps therefore
recolours everything that goes through them: each step keeps its own lightness
and its position within its ramp, and takes Umber's hue and chroma for that
family. Orange maps to the ember.

It does not recolour everything. The `ui` block also carries 132 raw hex literals (59 opaque, 73 translucent ARGB) that no ramp name covers — `/Recap/*`, `/RecentProject/*/Avatar/*`,
`MainWindow.Tab` and friends — and those ship in JetBrains' own cool greys and
blues. Pure white and black survive too, since scaling zero chroma leaves them
unchanged. Umber overrides the surfaces that matter (editor, tabs, borders,
selection); the long tail of rarely-seen panels stays stock.

Note that `lch()` returns **Lr**, not Oklab `L`. Passing its result through
`l_to_lr()` applies the toe correction twice and darkens everything.

The plugin's `ui.Editor.background`, its `ui.EditorTabs.underlinedTabBackground`,
the scheme's `TEXT` background and its `GUTTER_BACKGROUND` must all carry the
same value, or a seam shows where the editor meets its own tab. Nothing asserts
this — it holds because all four are set from `V["background"]`.

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
is re-levelled: keywords, functions, types, strings and numbers land within 0.001
of each other, against a 0.070 spread across the terminal slots they replace.
Roles that should not compete stay outside that band — punctuation 0.013 and
comments 0.014 below the identifiers they separate, errors 0.130 above. `render-code.py` renders a before/after specimen.

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

## The knobs

The palette model lives in `model.py`; the per-variant grounds and contrast
targets are arguments to `build()` in `build.py`.

| Knob | Where | Effect |
|---|---|---|
| `C_WARM` / `C_COOL` | `model.py` | Overall saturation of warm vs cool hues |
| `EMBER` | `model.py` | Hue where chroma peaks, and the cursor/search hue. Currently 48 |
| `USAGE` | `model.py` | Per-hue loudness weight. Lower = more recessive |
| `HUES` | `model.py` | Hue angle per ANSI slot |
| `STAGGER` | `model.py` | Per-hue lightness offset, for colour-vision separation |
| `bg_hex` | `build.py` | Ground for each variant |
| `targets` | `build.py` | Contrast targets the neutral ramp is solved to |

`optimise-stagger.py` re-solves `STAGGER` if you change the chroma model. It reads
the same `model.py`, so it can no longer fit a stale copy of it. It
searches for maximum worst-case separation across deuteranopia, protanopia and
tritanopia while keeping the lightness spread small.

## After any change

Run `audit.py`. It exits non-zero on any floor or salience violation, so it can
gate a script. It is the widest check: it alone tests `faint` text, the
foreground at 0.72 opacity against 0.66 of the floor.

Four emitters gate before writing, each on what it actually emits —
`build.py` on the terminal slots plus the salience order, `neovim.py` and
`intellij.py` on every syntax role via `editor.audit`, `xcode.py` on its own
role set. So a violating palette never reaches those, but passing one of them is
not the same as passing `audit.py`. `bat-theme.py`, `claude-chrome.py` and
`jetbrains-ui.py` consume an already-audited palette and do not re-gate.

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
