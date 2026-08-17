from perceptual import lch, solve, to_linear, write_atomic
from editor import syntax, surfaces
from palette import contrast, lum, enforce
import json, os, plistlib
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# Retargets the palette to Xcode, the same way neovim.py retargets it to
# Neovim. Surfaces the editor needs (current line, invisibles, doc panel) are
# derived in OKLrCH from palette.json, so build.py stays the single source of
# truth.
P = json.load(open(_os.path.join(_HERE, "palette.json")))

# Syntax colours come from editor.py, for the reason documented there: the
# terminal mutes cool hues as chrome, which in code would leave keywords,
# functions and types as the palette's three most desaturated colours. Xcode
# additionally distinguishes user symbols from SDK ones, so each system variant
# is the same hue lifted to a higher contrast rather than a different colour.
def roles(V):
    fg = V["foreground"]; c = {i: V[str(i)] for i in range(16)}
    X = syntax(V)
    bg = V["background"]
    lift = 1.28 if lum(bg) < 0.18 else 0.80   # system symbols read one step up

    def sys(role):
        L, C, H = lch(X[role])
        return solve(contrast(X[role], bg) * lift, bg, C, H)

    return {
        "plain": fg,
        "comment": c[8],
        "comment.doc": c[8],
        "comment.doc.keyword": c[8],
        "mark": X["constant"],
        "string": X["string"],
        "character": X["string"],
        "number": X["number"],
        "keyword": X["keyword"],
        "preprocessor": X["keyword"],
        "url": X["function"],
        "attribute": X["constant"],
        "declaration.type": X["type"],
        "declaration.other": X["function"],
        "identifier.type": X["type"],
        "identifier.type.system": sys("type"),
        "identifier.class": X["type"],
        "identifier.class.system": sys("type"),
        "identifier.function": X["function"],
        "identifier.function.system": sys("function"),
        "identifier.constant": X["constant"],
        "identifier.constant.system": sys("constant"),
        "identifier.variable": fg,
        "identifier.variable.system": X["member"],
        "identifier.macro": X["keyword"],
        "identifier.macro.system": sys("keyword"),
        "regex": X["escape"],
        "regex.capturename": X["param"],
        "regex.charclass": X["type"],
        "regex.number": X["number"],
        "regex.operator": X["punct"],
        "regex.other": fg,
        "markup.code": X["type"],
        "markup.aside.kind": X["string"],
    }

BASE, BOLD, ITALIC = ("MonaspiceNeNFM-Medium - 12.0", "MonaspiceNeNFM-Bold - 12.0",
                      "MonaspiceNeNFM-MediumItalic - 12.0")
# Prose in doc comments stays in the UI face; only the code spans are monospace.
UIFONT, UIFONT_B, UIFONT_I = (".AppleSystemUIFont - %.1f", ".AppleSystemUIFontBold - %.1f",
                              ".AppleSystemUIFontItalic - %.1f")
FONT = {"comment": ITALIC, "comment.doc": ITALIC,
        "comment.doc.keyword": BOLD, "mark": BOLD}

# Xcode reads these floats as calibrated Generic RGB (gamma 1.8), not sRGB.
# Writing raw sRGB components lifts every dark and washes out every accent, so
# encode through the 1.8 gamma such that Xcode's interpretation displays the
# intended sRGB colour. Verified against on-screen pixels: #171614 written raw
# renders as #1e1d1a, the gamma-1.8 transfer.
def col(hx):
    return " ".join(f"{c ** (1/1.8):.6f}" for c in to_linear(hx)) + " 1"

def theme(V, S):
    bg, fg, sel, cur = V["background"], V["foreground"], V["selection"], V["cursor"]
    c = {i: V[str(i)] for i in range(16)}
    R = roles(V)
    X = syntax(V)
    return {
        "DVTFontAndColorVersion": 1,
        # Xcode falls back to its own defaults for any key a theme omits, which
        # is how an otherwise complete theme leaks: the dimmed-block grey, the
        # scrollbar error marker and the markup fonts all showed through.
        "DVTLineSpacing": 1.12,
        "DVTSourceTextBlockDimBackgroundColor": col(S["line"]),
        "DVTScrollbarMarkerErrorColor": col(X["error"]),
        "DVTSourceTextBackground": col(bg),
        "DVTSourceTextCurrentLineHighlightColor": col(S["line"]),
        "DVTSourceTextInsertionPointColor": col(cur),
        "DVTSourceTextInvisiblesColor": col(S["ghost"]),
        "DVTSourceTextSelectionColor": col(sel),
        "DVTSourceTextSyntaxColors": {f"xcode.syntax.{k}": col(v) for k, v in R.items()},
        "DVTSourceTextSyntaxFonts": {f"xcode.syntax.{k}": FONT.get(k, BASE) for k in R},
        "DVTConsoleTextBackgroundColor": col(bg),
        "DVTConsoleTextInsertionPointColor": col(cur),
        "DVTConsoleTextSelectionColor": col(sel),
        "DVTConsoleDebuggerInputTextColor": col(fg),
        "DVTConsoleDebuggerInputTextFont": BOLD,
        "DVTConsoleDebuggerOutputTextColor": col(fg),
        "DVTConsoleDebuggerOutputTextFont": BASE,
        "DVTConsoleDebuggerPromptTextColor": col(c[4]),
        "DVTConsoleDebuggerPromptTextFont": BOLD,
        "DVTConsoleExectuableInputTextColor": col(fg),
        "DVTConsoleExectuableInputTextFont": BASE,
        "DVTConsoleExectuableOutputTextColor": col(fg),
        "DVTConsoleExectuableOutputTextFont": BASE,
        "DVTMarkupTextBackgroundColor": col(S["panel"]),
        "DVTMarkupTextBorderColor": col(c[0]),
        "DVTMarkupTextNormalColor": col(fg),
        "DVTMarkupTextPrimaryHeadingColor": col(c[3]),
        "DVTMarkupTextSecondaryHeadingColor": col(c[3]),
        "DVTMarkupTextOtherHeadingColor": col(c[3]),
        "DVTMarkupTextLinkColor": col(c[4]),
        "DVTMarkupTextInlineCodeColor": col(c[6]),
        "DVTMarkupTextEmphasisColor": col(fg),
        "DVTMarkupTextStrongColor": col(fg),
        "DVTMarkupTextNormalFont": UIFONT % 11.0,
        "DVTMarkupTextEmphasisFont": UIFONT_I % 11.0,
        "DVTMarkupTextStrongFont": UIFONT_B % 11.0,
        "DVTMarkupTextLinkFont": UIFONT % 11.0,
        "DVTMarkupTextPrimaryHeadingFont": UIFONT_B % 22.0,
        "DVTMarkupTextSecondaryHeadingFont": UIFONT_B % 17.0,
        "DVTMarkupTextOtherHeadingFont": UIFONT_B % 13.0,
        "DVTMarkupTextCodeFont": BASE,
        "DVTScrollbarMarkerAnalyzerColor": col(c[12]),
        "DVTScrollbarMarkerBreakpointColor": col(c[4]),
        "DVTScrollbarMarkerDiffColor": col(c[2]),
        "DVTScrollbarMarkerDiffConflictColor": col(c[1]),
        "DVTScrollbarMarkerRuntimeIssueColor": col(c[5]),
        "DVTScrollbarMarkerWarningColor": col(c[3]),
    }

VARIANTS = (("Umber", P["dark"]), ("Umber Night", P["night"]), ("Umber Light", P["light"]))
FLOOR = {"Umber": 4.5, "Umber Night": 3.3, "Umber Light": 4.5}

OUT = os.path.expanduser("~/Library/Developer/Xcode/UserData/FontAndColorThemes")
os.makedirs(OUT, exist_ok=True)

# Audit first, write only if every floor holds — invisibles are exempt (they
# are deliberately ghosted), comments get the same relaxed floor as neovim.py.
failures = []
built = []
for name, V in VARIANTS:
    S = surfaces(V)
    built.append((name, V, S))
    f = FLOOR[name]; bg = V["background"]
    checks = [(k, contrast(v, bg), f * (0.66 if k.startswith("comment") else 1))
              for k, v in roles(V).items()]
    checks.append(("fg/line", contrast(V["foreground"], S["line"]), f))
    checks.append(("fg/panel", contrast(V["foreground"], S["panel"]), f))
    bad = [n for n, x, floor in checks if x < floor]
    worst = min(checks, key=lambda t: t[1] / t[2])
    print(f"{name:<12} worst {worst[0]} {worst[1]:.2f} (floor {worst[2]:.2f})  "
          f"{'PASS' if not bad else 'BELOW: ' + str(bad)}")
    failures += [f"{name}:{n}" for n in bad]
enforce(failures)

for name, V, S in built:
    write_atomic(os.path.join(OUT, f"{name}.xccolortheme"),
                 plistlib.dumps(theme(V, S), sort_keys=True))
print(f"wrote 3 themes -> {OUT}")
