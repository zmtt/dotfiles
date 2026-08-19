"""Render a code specimen for the editor palette. Numbers cannot tell you a
syntax theme is flat; this can."""
from perceptual import write_atomic
import json, html, re, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
from editor import syntax

esc = lambda s: html.escape(s, quote=False)
P = json.load(open(_os.path.join(_HERE, "palette.json")))
cfg = open(os.path.expanduser("~/.config/ghostty/config")).read()
FONT = re.search(r'^font-family\s*=\s*"?([^"\n]+)"?', cfg, re.M).group(1).strip()

OLD = {"keyword": "#c394b2", "function": "#88a7c8", "type": "#88c5c5",
       "string": "#92bc84", "number": "#e0a049", "member": "#d4c7be",
       "param": "#d4c7be", "punct": "#c7bdb5", "constant": "#e0a049",
       "escape": "#a4dcdc", "error": "#fa9b86", "muted": "#8a7f75"}

CODE = [
    [("k","suspend fun "),("f","drain"),("p","("),("a","limit"),("p",": "),("t","Int"),
     ("p"," = "),("n","64"),("p","): "),("t","Result"),("p","<"),("t","Unit"),("p","> {")],
    [("p","    "),("k","val "),("v","escrow"),("p"," = "),("v","repository"),("p","."),("m","pending"),
     ("p",".")," ",("f","filter"),("p"," { "),("v","it"),("p","."),("m","state"),
     ("p"," == "),("t","Escrow"),("p","."),("c","HELD"),("p"," }")],
    [("cm","    // hopper reports in cents; MDB reports in units")],
    [("p","    "),("k","val "),("v","total"),("p"," = "),("v","escrow"),("p","."),
     ("f","sumOf"),("p"," { "),("v","it"),("p","."),("m","amount"),("p"," * "),("n","100"),("p"," }")],
    [("p","    "),("k","if"),("p"," ("),("v","total"),("p"," > "),("t","Denomination"),("p","."),("c","MAX"),("p",") {")],
    [("p","        "),("k","return "),("t","Result"),("p","."),("f","failure"),("p","("),
     ("t","OverflowError"),("p","("),("s","\"escrow exceeds hopper\""),("p","))")],
    [("p","    }")],
    [("p","    "),("v","logger"),("p","."),("f","info"),("p","("),
     ("s","\"draining %d\\n\""),("p",", "),("v","total"),("p",")")],
    [("p","    "),("k","return "),("f","runCatching"),("p"," { "),("v","pump"),
     ("p","."),("f","flush"),("p","("),("a","limit"),("p",") }")],
    [("p","}")],
]
KEY = {"k":"keyword","f":"function","t":"type","s":"string","n":"number","c":"constant",
       "m":"member","a":"param","p":"punct","cm":"comment","v":"fg"}

def panel(V, X, x, y, w, h, title):
    bg, fg = V["background"], V["foreground"]
    com = V["8"]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{bg}"/>',
           f'<text x="{x+22}" y="{y+30}" font-family="{FONT}" font-size="12" fill="{com}" letter-spacing="1.3">{esc(title)}</text>']
    ty = y + 66
    for line in CODE:
        # Under xml:space="preserve" any whitespace between tspans renders as a
        # space, so a line's spans must be joined with nothing between them.
        spans = []
        for tag, txt in [t for t in line if isinstance(t, tuple)]:
            role = KEY[tag]
            col = fg if role == "fg" else (com if role == "comment" else X[role])
            it = ' font-style="italic"' if role == "comment" else ''
            spans.append(f'<tspan fill="{col}"{it}>{esc(txt)}</tspan>')
        out.append(f'<text x="{x+22}" y="{ty}" font-family="{FONT}" font-size="14" xml:space="preserve">'
                   + "".join(spans) + '</text>')
        ty += 26
    return "\n".join(out)

V = P["dark"]
W, H = 660, 380
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="420" viewBox="0 0 1380 420">',
     '<rect width="1380" height="420" fill="#8f8f8f"/>',
     panel(V, OLD, 20, 20, W, H, "BEFORE  terminal slots reused"),
     panel(V, syntax(V), 700, 20, W, H, "AFTER  editor-levelled chroma"), '</svg>']
write_atomic(_os.path.join(_HERE, "code.svg"), "\n".join(s))
print("ok")
