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
| Variant switching (light follows macOS) | `~/.config/fish/functions/umber.fish` *(source)* | new shell |
| **Any editor's** syntax: keywords, types, strings | `editor.py` | the affected emitter |
| Neovim UI: floats, diffs, statusline | `neovim.py` | `python3 neovim.py` |
| Android Studio editor pane | `editor.py` or `intellij.py` | `python3 intellij.py && python3 jetbrains-ui.py`, restart |
| Android Studio chrome: tabs, sidebar, toolbar | `jetbrains-ui.py` `RAMPS` | `python3 jetbrains-ui.py`, restart |
| Xcode | `xcode.py` | `python3 xcode.py`, restart |
| `bat` output, or the code inside a diff | `bat-theme.py` | `python3 bat-theme.py` |
| Diff washes, blame ramp, which variant delta uses | `delta.py` | `python3 delta.py` |
| Diff gutter, changed-word highlight | `~/.config/git/common.conf` *(source)* | next diff |
| Claude Code prompt box, "You" label | `claude-chrome.py` | `python3 claude-chrome.py`, restart |
| Claude Code status line | `~/.claude/statusline-command.py` *(source)* | next turn |

## Generated versus source

Everything here is **output**. Editing it is pointless; the next rebuild wins.

```
~/.config/ghostty/themes/umber, umber-light
~/.config/nvim/colors/umber*.lua
~/.config/nvim/lua/lualine/themes/umber*.lua
~/.config/bat/themes/Umber*.tmTheme
~/.claude/themes/umber.json, umber-light.json
~/Library/Application Support/Google/AndroidStudio*/colors/Umber*.icls
~/Library/Application Support/Google/AndroidStudio*/plugins/umber-theme.jar
~/Library/Developer/Xcode/UserData/FontAndColorThemes/Umber*.xccolortheme
~/.config/git/umber-delta.conf             delta's per-variant half
~/.config/umber/palette.json               written by build.py, read by every emitter
~/.config/umber/stagger.json               written by optimise-stagger.py
~/.config/umber/{specimen,code}.svg        written by the renderers
```

These are **source**, edit directly:

```
~/.config/umber/*.py                       the generators
~/.config/ghostty/config                   font, spacing, ligatures, cursor
~/.config/fish/conf.d/umber-theme.fish     shell syntax colours
~/.config/fish/functions/umber.fish        the variant switcher
~/.claude/statusline-command.py            the status line
~/.config/bat/config                       picks Umber per macOS appearance
~/.config/git/common.conf                  delta's ANSI-named half (gutter, emph)
~/.config/git/umber-delta                  the pager wrapper that picks the variant
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
python3 build.py          # the two Ghostty themes
python3 audit.py          # every contrast floor and the salience order
python3 claude-chrome.py  # ~/.claude/themes/umber{,-light}.json
python3 neovim.py         # ~/.config/nvim/colors + lualine themes
python3 intellij.py       # Android Studio .icls editor schemes
python3 jetbrains-ui.py   # Android Studio UI theme plugin (umber-theme.jar)
python3 xcode.py          # ~/Library/Developer/Xcode/UserData/FontAndColorThemes
python3 bat-theme.py      # bat/delta .tmTheme, rebuilds bat's cache
python3 delta.py          # ~/.config/git/umber-delta.conf

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
rendered in an unrelated palette. `bat-theme.py` emits Umber `.tmTheme` files.

Selecting them is the awkward part, because a diff has to follow the variant
the way Ghostty and Neovim do. Both were pinned to the dark theme for a while,
which is invisible until you are in the light variant and the body text of every
diff is sitting at 1.54:1.

bat solves it alone: `--theme=auto:system` reads the macOS appearance on every
invocation. delta cannot. It does detect a dark or light terminal
(`--detect-dark-light`), but detection only chooses between its own built-in
defaults: it cannot activate a named feature or select a custom syntax-theme,
which is where all of Umber's per-variant values live. So delta's config is split
in two. The ANSI-named half lives in `~/.config/git/common.conf` and needs no
switch, because named slots resolve against whichever palette is loaded. The half
that is concrete hex — the `+`/`-` washes, the syntax-theme name, the blame ramp
— is generated per variant into `umber-delta.conf`, and `~/.config/git/umber-delta`
resolves the appearance and sets `DELTA_FEATURES` so delta activates the matching
block.

Three things about delta that are easy to get wrong, all measured rather than
assumed. The first and third are gated by `delta.py` rather than left to a
comment:

- **The main `[delta]` section overrides an active feature**, not the reverse. A
  key set in both places is pinned to the main section's value and the feature
  quietly does nothing. This is why `syntax-theme` had to leave `git/config`
  entirely rather than merely gain a per-variant sibling.
- `BAT_THEME` only reaches delta when `syntax-theme` is unset, so it is no way
  around the above.
- **The washes are not the dichromat's channel**, `line-numbers` is. At the
  chroma a wash sits at, the `+`/`-` pair measures a deuteranopic separation of
  0.008 dark and 0.011 light against a floor of 0.035, and no hue rotation
  clears that without failing tritanopia instead. The red/green gutter numbers
  measure 0.046 and 0.045, so turning `line-numbers` off would quietly drop the
  diff below the floor the rest of the palette is held to.

The washes are `editor.surfaces()`'s `add` and `delete`, the same two Neovim and
Android Studio already paint diffs with, at chroma 0.027–0.031 against a ground
they clear at better than 9:1. Dropping the wash entirely was tried first: with
`keep-plus-minus-markers = false` a removed line and an added line then render
identically in the body, and the only thing separating them is a four-character
number in the gutter. Numbers all passed. It was the render that showed it.

`DELTA_FEATURES` is resolved per invocation by `~/.config/git/umber-delta`, the
script `core.pager` and `interactive.diffFilter` both point at, so a mid-session
appearance flip is picked up by the next diff and git hooks and editor
subprocesses get the same treatment as an interactive shell. Resolving it once
per shell was tried first: Ghostty swaps its palette live, so the stale value
went on painting dark washes onto a light terminal for the rest of the session,
which is the 1.54:1 failure above in a slower form. Forcing a variant by hand
takes the whole feature name, `DELTA_FEATURES="umber-dark side-by-side"`; the
additive `+side-by-side` form adds to the features named in git config, where the
variant is not one, and silently drops the theme.

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

The `ui` block also carries 132 raw hex literals (59 opaque, 73 translucent
ARGB) that no ramp name covers. Opaque chromatic ones are re-hued into the
nearest Umber accent family by `retint_literals` — the git-log current-branch
wash, the run widget's green, the progress counter — keeping their own
lightness and capping chroma at the family's ceiling. The identity palettes
(`RecentProject.*` avatars, `CodeWithMe.*` users, `Recap.*` branding) are
excluded: their whole purpose is to differ per project or user. Translucent
and near-neutral literals pass through, since they blend with the retinted
surfaces, and pure white and black survive because scaling zero chroma leaves
them unchanged. Umber still overrides the surfaces that matter (editor, tabs,
borders, selection) explicitly.

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

**Three different metrics, checked separately.** WCAG contrast measures whether
text can be *read* (floor 4.5:1). Chroma
measures whether it *catches the eye*. `audit.py` checks both — a change that
improves one can silently break the other.

APCA is the third, because WCAG 2 overstates contrast near black. At matched
ratios the dark variant read far weaker than the light one: comments at Lc 34
against 70, body text at 73 against 92. `APCA_FLOOR` gates body text, accents,
syntax roles and comments beside the WCAG floor, in `build.py` and
`editor.audit`. The dark variant sits just above those floors, not well
clear of them: body text at Lc 76.5, the weakest accent at 54, syntax roles at
57 with strings at 52, comments at 39.5. Light text on a dark ground blooms, so
brightness past readability adds glare and no legibility. A version lifted to
Lc 80.7 body and 61 accents read as too bright on screen, though a render at
specimen size could not show it. With `CVD_SAFE` on, the syntax floor of 50
cannot hold: red losing its chroma above about Lc 62 caps the stack, and the
staggers then need a spread it cannot fit.

**Separation is measured for normal vision.** `model.CVD_SAFE` is off, so
`worst_separation` measures trichromat distance only, and every accent and role
sits at one lightness. The dichromat staggers bought separation back at the cost
of calm: types sank below keywords, and the accents never quite sat level. To
design for colour-blind viewers again, set `CVD_SAFE = True` and re-solve
`STAGGER` and `ROLE_STAGGER` with `optimise-stagger.py`.

**The grounds are slate, and chroma is measured against them.** `#161a21` and
`#f3f6fa` sit at chroma 0.015 and 0.006, cool against warm accents, which is the
pairing that makes the ember and ochre glow: red and yellow sit 10 to 16%
further from the ground than on a neutral one. A tinted ground also takes
chroma from the accents nearest its own hue, and uncompensated slate drained
blue by 29%. `perceptual.ground_lift` adds the ground's projected chroma back
to every accent and syntax role, so the cool ones stay within 8% of where a
neutral ground puts them. The neutral hue `nh` follows the ground to 250, so
greys, selection and editor surfaces are one temperature with it. Kept warm,
they put a brown title bar on a slate window. An umber ground (`#1f1915`) was
tried first and muted the warm accents instead. The neutral-ground version is
tagged `umber-neutral` in the dotfiles repo.

**The cool hues lean earthward**: plum at 325 rather than pink at 340, olive at
130, patina at 190, slate at 245.

**Staggers push toward contrast.** A `STAGGER` offset lightens a slot on the
dark ground and darkens it on the light one, so each accent keeps the same rank
in both variants. Applied as a plain Lr offset, it made red the weakest dark
accent and the strongest light one, and left light cyan at 4.62:1.

## The knobs

The palette model lives in `model.py`; the per-variant grounds and contrast
targets are arguments to `build()` in `build.py`.

| Knob | Where | Effect |
|---|---|---|
| `C_WARM` / `C_COOL` | `model.py` | Overall saturation of warm vs cool hues |
| `EMBER` | `model.py` | Hue where chroma peaks, and the cursor/search hue. Currently 48 |
| `USAGE` | `model.py` | Per-hue loudness weight. Lower = more recessive |
| `HUES` | `model.py` | Hue angle per ANSI slot |
| `STAGGER` | `model.py` | Per-hue lightness offset, for colour-vision separation. Zero while `CVD_SAFE` is off |
| `CVD_SAFE` | `model.py` | Measure separation for dichromats (True) or normal vision (False) |
| `ROLE_STAGGER` | `editor.py` | Per-role contrast-target multiplier, the same separation for the editor roles |
| `SEPARATION_FLOOR` | `model.py` | Minimum dichromat-simulated distance any two meaning-carrying colours may sit at |
| `APCA_FLOOR` | `model.py` | Perceptual contrast floors (Lc) for body text, accents, syntax roles, comments |
| `bg_hex` | `build.py` | Ground for each variant |
| `targets` | `build.py` | Contrast targets the neutral ramp is solved to |

`optimise-stagger.py` re-solves `STAGGER` and `ROLE_STAGGER` if you change the
chroma model. It reads the same `model.py` and `editor.py`, so it can no longer
fit a stale copy of either. It searches for maximum worst-case separation across
deuteranopia, protanopia and tritanopia while keeping each spread small, and
holds a contrast margin above the floors so separation cannot buy its last
thousandth by parking a colour on a floor. It also rejects role candidates that
invert salience: an error below a body role or short of its chroma, or `member`
or `param` above plain text. Unconstrained, it found its best separation
exactly that way.

## After any change

Run `audit.py`. It exits non-zero on any floor or salience violation, so it can
gate a script. It is the widest check: it alone tests `faint` text, the
foreground at 0.72 opacity against 0.66 of the floor.

Six emitters gate before writing, each on what it actually emits —
`build.py` on the terminal slots, the salience order and accent separation,
`neovim.py`, `intellij.py`, `xcode.py` and `bat-theme.py` on every syntax role
(contrast and dichromat separation) via `editor.audit`, `intellij.py` and
`xcode.py` additionally on their own surface sets, `delta.py` on the foreground
against every ground it introduces (both diff washes and all three blame steps).
So a violating palette never reaches those, but passing one of them is not the
same as passing `audit.py`. `claude-chrome.py` and `jetbrains-ui.py` consume an
already-audited palette and do not re-gate.

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
