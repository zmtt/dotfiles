from perceptual import hex_lr, l_to_lr, lch, contrast, write_atomic
from palette import enforce
from editor import surfaces
import json, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

P = json.load(open(_os.path.join(_HERE, "palette.json")))
D, L = P["dark"], P["light"]

# The message box takes the palette's neutral hue, the one every other
# emitter reads off the foreground, so it is a panel of the same material as
# the ground. Hard-coded warm hues left a brown box on the slate ground.
dnh, lnh = lch(D["foreground"])[2], lch(L["foreground"])[2]
dark_box   = hex_lr(l_to_lr(0.300), 0.016, dnh)[0]
dark_hover = hex_lr(l_to_lr(0.375), 0.019, dnh)[0]
light_box   = hex_lr(l_to_lr(0.930), 0.014, lnh)[0]
light_hover = hex_lr(l_to_lr(0.968), 0.010, lnh)[0]

def blend(f, b, a):
    F = [int(f[i:i+2], 16) for i in (1, 3, 5)]; B = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(F[k]*a + B[k]*(1-a)) for k in range(3))

# Claude Code paints almost every role as text on the ground; the panels below
# are fills under text, and accents double as badge fills under inverseText,
# as does `text` itself on a selected row. inverseText is therefore the ground.
# Diff roles are left to the base theme: Umber's olive and brick washes read
# muddy behind Claude Code's uncoloured diff text, where delta and Neovim have
# syntax colour to carry them.
FILLS = ("userMessageBackground", "userMessageBackgroundHover", "composerSidebarBackground",
         "selectionBg", "bashMessageBackgroundColor", "memoryBackgroundColor")
# Faint by design in the base themes too (about 2:1), or only ever animated
# against another role. Comment grey is hint and border text: light's sits at
# 4.15 on its box, so it alone gets 4.0 instead of 4.5.
FAINT = ("subtle", "rate_limit_empty", "inactiveShimmer", "promptBorderShimmer",
         "claudeShimmer", "permissionShimmer", "autoAcceptShimmer", "warningShimmer",
         "fastModeShimmer", "claudeBlueShimmer_FOR_SYSTEM_SPINNER")
GREY = ("inactive", "promptBorder")

def roles(V, dark, box, hover):
    c = {i: V[str(i)] for i in range(16)}; S = surfaces(V)
    bg, fg, ember = V["background"], V["foreground"], V["cursor"]
    return {
        "text": fg, "inverseText": bg,
        "inactive": c[8], "inactiveShimmer": c[7] if dark else blend(c[8], bg, 0.75),
        "subtle": blend(c[8], bg, 0.5),
        "promptBorder": c[8], "promptBorderShimmer": blend(c[8], fg, 0.5),
        "claude": ember, "claudeShimmer": blend(ember, fg, 0.6),
        "clawd_body": ember, "briefLabelClaude": ember, "briefLabelYou": c[4],
        "claudeBlue_FOR_SYSTEM_SPINNER": c[4], "claudeBlueShimmer_FOR_SYSTEM_SPINNER": c[12],
        "permission": c[4], "permissionShimmer": blend(c[4], fg, 0.5),
        "suggestion": c[4], "remember": c[12] if dark else c[4],
        "rate_limit_fill": c[4], "rate_limit_empty": blend(c[4], bg, 0.4),
        "planMode": c[6], "ide": c[4], "background": c[6],
        "autoAccept": c[5], "autoAcceptShimmer": blend(c[5], fg, 0.5),
        "skill": c[5], "merged": c[5], "effortUltra": c[5], "bashBorder": c[13],
        "success": c[2], "error": c[1], "warning": c[3], "warningShimmer": c[11],
        "fastMode": ember, "fastModeShimmer": blend(ember, fg, 0.6),
        "professionalBlue": c[4], "chromeYellow": c[3],
        "red_FOR_SUBAGENTS_ONLY": c[1], "blue_FOR_SUBAGENTS_ONLY": c[4],
        "green_FOR_SUBAGENTS_ONLY": c[2], "yellow_FOR_SUBAGENTS_ONLY": c[3],
        "purple_FOR_SUBAGENTS_ONLY": c[5], "orange_FOR_SUBAGENTS_ONLY": ember,
        "pink_FOR_SUBAGENTS_ONLY": c[13], "cyan_FOR_SUBAGENTS_ONLY": c[6],
        "userMessageBackground": box, "userMessageBackgroundHover": hover,
        "composerSidebarBackground": S["line"], "selectionBg": V["selection"],
        "bashMessageBackgroundColor": blend(c[5], box, 0.08),
        "memoryBackgroundColor": blend(c[4], box, 0.08),
    }

failures = []
themes = []
for name, title, fname, V, box, hover in (
        ("dark", "Umber", "umber", D, dark_box, dark_hover),
        ("light", "Umber Light", "umber-light", L, light_box, light_hover)):
    R = roles(V, name == "dark", box, hover)
    bg, fg = V["background"], V["foreground"]
    # Text roles against the ground and the message box they also sit on;
    # fills against the text drawn on them.
    text = {k: min(contrast(h, bg), contrast(h, box)) for k, h in R.items()
            if k not in FILLS and k not in FAINT and k != "inverseText"}
    fills = {k: contrast(fg, R[k]) for k in FILLS}
    fills |= {f"inverseText/{k}": contrast(R["inverseText"], R[k]) for k in text
              if k not in GREY}
    worst = min(text, key=text.get)
    print(f"{name:<6} box {box}  hover {hover}  worst text {worst} {text[worst]:.2f}  "
          f"worst fill {min(fills.values()):.2f}  box vs ground {contrast(box, bg):.2f}:1")
    failures += [f"{name}:{k} {x:.2f}" for k, x in text.items() if x < (4.0 if k in GREY else 4.5)]
    failures += [f"{name}:{k} {x:.2f}" for k, x in fills.items() if x < 4.5]
    themes.append((fname, {"name": title, "base": name, "overrides": R}))
enforce(failures)

TD = os.path.expanduser("~/.claude/themes")
os.makedirs(TD, exist_ok=True)
for fname, theme in themes:
    write_atomic(f"{TD}/{fname}.json", json.dumps(theme, indent=2))
print(f"\nghostty ground {D['background']} / {L['background']}")
print("statusline:", " ".join(f"{k}={D[k]}" for k in ("1","2","3","5","6","8","0")))
