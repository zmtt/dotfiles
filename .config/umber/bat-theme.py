"""Build Umber .tmTheme files for bat, which delta also uses.

bat and delta both syntax-highlight through Sublime .tmTheme files, and both
default to Monokai Extended. Since delta is the git pager, every diff read on
this machine was rendering syntax in a palette unrelated to everything else.

Accents come from editor.py for the same reason the other editors use it: bat
colours nearly every glyph, so the terminal's chrome weighting would leave
keywords, types and functions as the most desaturated colours on screen.
"""
import json, os, plistlib, subprocess
from editor import syntax, audit
from perceptual import hex_lr, lch, solve, write_atomic
from palette import contrast, enforce, lum

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "palette.json")))
OUT = os.path.expanduser("~/.config/bat/themes")


def rule(name, scope, fg=None, style=None):
    s = {}
    if fg:
        s["foreground"] = fg
    if style:
        s["fontStyle"] = style
    return {"name": name, "scope": scope, "settings": s}


def build(variant, name):
    V = P[variant]
    X = syntax(V)
    bg, fg = V["background"], V["foreground"]
    dark = lum(bg) < 0.18
    nh = lch(fg)[2]
    bglr = lch(bg)[0]
    d = 1 if dark else -1
    line = hex_lr(bglr + d * 0.045, 0.017, nh)[0]

    settings = [{"settings": {
        "background": bg,
        "foreground": fg,
        "caret": V["cursor"],
        "selection": V["selection"],
        "lineHighlight": line,
        "invisibles": V["8"],
        "gutterForeground": solve(2.6 if dark else 2.9, bg, 0.014, nh),
    }}]

    settings += [
        rule("Comment", "comment, punctuation.definition.comment", X["muted"], "italic"),
        rule("String", "string, string.quoted", X["string"]),
        rule("String escape", "constant.character.escape", X["escape"]),
        rule("Number", "constant.numeric", X["number"]),
        rule("Built-in constant", "constant.language, constant.character", X["constant"]),
        rule("Other constant", "constant.other, variable.other.constant", X["constant"]),
        rule("Keyword", "keyword, keyword.control, keyword.operator.word", X["keyword"]),
        rule("Storage", "storage, storage.type, storage.modifier", X["keyword"]),
        rule("Operator", "keyword.operator, punctuation.separator, "
                         "punctuation.terminator, punctuation.accessor", X["punct"]),
        rule("Punctuation", "punctuation.definition, meta.brace, "
                            "punctuation.section", X["punct"]),
        rule("Function", "entity.name.function, support.function, "
                         "meta.function-call", X["function"]),
        rule("Type", "entity.name.type, entity.name.class, entity.name.struct, "
                     "entity.name.enum, support.type, support.class, "
                     "entity.other.inherited-class", X["type"]),
        rule("Parameter", "variable.parameter", X["param"]),
        rule("Member", "variable.other.member, meta.attribute, "
                       "entity.name.tag", X["member"]),
        rule("Variable", "variable, variable.other", fg),
        rule("Annotation", "meta.annotation, storage.type.annotation, "
                           "entity.name.function.decorator", X["constant"]),
        rule("Tag attribute", "entity.other.attribute-name", X["number"]),
        rule("Invalid", "invalid, invalid.illegal", X["error"]),
        rule("Heading", "markup.heading", X["constant"], "bold"),
        rule("Link", "markup.underline.link", X["function"], "underline"),
        rule("Bold", "markup.bold", None, "bold"),
        rule("Italic", "markup.italic", None, "italic"),
        rule("Diff inserted", "markup.inserted", X["string"]),
        rule("Diff deleted", "markup.deleted", X["error"]),
        rule("Diff changed", "markup.changed", X["number"]),
    ]

    return {"name": name, "settings": settings,
            "uuid": "umber-%s" % variant, "colorSpaceName": "sRGB"}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    # Audit before the first write: a failed gate must not leave one theme
    # rewritten and its sibling stale.
    enforce([f"{v}:{k}" for v in P for k, _ in audit(P[v], syntax(P[v]), 4.5)])
    made = []
    for variant, name in (("dark", "Umber"), ("light", "Umber Light")):
        if variant not in P:
            continue
        theme = build(variant, name)
        path = os.path.join(OUT, "%s.tmTheme" % name)
        write_atomic(path, plistlib.dumps(theme))
        V = P[variant]
        X = syntax(V)
        worst = min((contrast(r["settings"]["foreground"], V["background"]), r["name"])
                    for r in theme["settings"][1:] if r["settings"].get("foreground"))
        print(f"  {name:<12} worst {worst[1]} {worst[0]:.2f}:1")
        made.append(name)

    print(f"\nwrote {len(made)} themes -> {OUT.replace(os.path.expanduser('~'), '~')}")
    # bat only sees a theme after its cache is rebuilt, but the themes are
    # already on disk by now, so a missing bat is worth reporting rather than
    # failing over.
    try:
        subprocess.run(["bat", "cache", "--build"], check=True, timeout=60,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("bat cache rebuilt")
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"bat cache NOT rebuilt ({type(e).__name__}); run: bat cache --build")
