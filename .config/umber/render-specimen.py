from perceptual import write_atomic
import json, html, re, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# Read the live font so a specimen can never show a family the terminal is not
# actually using.
_cfg = open(os.path.expanduser("~/.config/ghostty/config")).read()
FONT = (re.search(r'^font-family\s*=\s*"?([^"\n]+)"?', _cfg, re.M) or [None, "monospace"])[1].strip()
STYLE = (re.search(r'^font-style\s*=\s*(\S+)', _cfg, re.M) or [None, ""])[1]
WEIGHT = "500" if STYLE.strip() == "Medium" else "400"
def esc(s): return html.escape(s, quote=False)
P = json.load(open(_os.path.join(_HERE, "palette.json")))

def blend(fg, bg, a):
    f=[int(fg[i:i+2],16) for i in (1,3,5)]; b=[int(bg[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(round(f[k]*a+b[k]*(1-a)) for k in range(3))

def build(V, x, y, w, h, title):
    bg, fg = V["background"], V["foreground"]
    c = lambda i: V[str(i)]
    faint = blend(fg, bg, 0.72)
    rows = [
        [("❯ ", 2), ("git diff --stat", None)],
        [(" amdbcore/data/LabRunner.kt | 12 ", None), ("++++++++", 2), ("----", 1)],
        [("", None)],
        [("@@ -84,7 +84,9 @@", 6), (" suspend fun drain(", None)],
        [("-    val n = queue.size", 1)],
        [("+    val n = queue.size.coerceAtMost(limit)", 2)],
        [("+    require(n >= 0) { \"negative\" }", 2)],
        [("", None)],
        [("❯ ", 2), ("eza -l --git", None)],
        [("drwxr-xr-x  ", 8), ("amdbcore", 4), ("/", 8)],
        [("-rwxr-xr-x  ", 8), ("gradlew", 2)],
        [("lrwxr-xr-x  ", 8), ("latest.log", 6), (" -> raw-0814.log", 8)],
        [("-rw-r--r--  ", 8), ("release.tar.gz", 1)],
        [("", None)],
        [("❯ ", 2), ("rg escrow --stats", None)],
        [("LabRunner.kt", 5), (":", 8), ("84", 2), (":", 8), ("  pump(", None), ("escrow", 3), (", n)", None)],
        [("", None)],
        [("❯ ", 2), ("./gradlew assemble", None)],
        [("FAILURE:", 9), (" Build failed with an exception.", None)],
        [("  note: run with --stacktrace", "faint")],
        [("", None)],
        [("❯ ", 2), ("git pu", None), ("sh origin HEAD", 8), ("  ", None), ("█", "cursor")],
    ]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{bg}"/>',
           f'<clipPath id="k{x}"><rect x="{x}" y="{y}" width="{w}" height="34"/></clipPath>',
           f'<g clip-path="url(#k{x})"><rect x="{x}" y="{y}" width="{w}" height="44" rx="10" fill="{c(0) if title.startswith("UMBER ") else V["selection"]}"/></g>']
    for i, col in enumerate((1, 3, 2)):
        out.append(f'<circle cx="{x+20+i*17}" cy="{y+17}" r="5" fill="{c(col)}"/>')
    out.append(f'<text x="{x+78}" y="{y+22}" font-family="{FONT}" font-weight="{WEIGHT}" font-size="12" fill="{c(8)}" letter-spacing="1.4">{esc(title)}</text>')
    ty = y + 60
    for line in rows:
        # Under xml:space="preserve" any whitespace between tspans renders as a
        # space, so a line's spans must be joined with nothing between them.
        spans = []
        for seg, k in line:
            fill = fg if k is None else (faint if k=="faint" else (V["cursor"] if k=="cursor" else c(k)))
            spans.append(f'<tspan fill="{fill}">{esc(seg)}</tspan>')
        out.append(f'<text x="{x+22}" y="{ty}" font-family="{FONT}" font-weight="{WEIGHT}" font-size="14" xml:space="preserve" fill="{fg}">'
                   + "".join(spans) + '</text>')
        ty += 23
    return "\n".join(out)

W,H = 620, 570
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="630" viewBox="0 0 1300 630">',
     '<rect width="1300" height="630" fill="#909090"/>',
     build(P["dark"], 20, 30, W, H, "UMBER  #171614"),
     build(P["light"], 660, 30, W, H, "UMBER LIGHT  #f8f7f5"), '</svg>']
write_atomic(_os.path.join(_HERE, "specimen.svg"), "\n".join(s))
