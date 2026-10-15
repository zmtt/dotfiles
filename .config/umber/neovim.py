from perceptual import write_atomic, hex_lr, lch
from editor import syntax, audit, surfaces
from palette import contrast, lum, enforce
from model import EMBER, chroma_for
import json, os, re
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# Retargets the palette to Neovim, the same way claude-chrome.py retargets it to
# Claude Code. Everything a terminal never needed — the near-background surface
# ramp, diff washes, search highlight — is derived here in OKLrCH from
# palette.json, so build.py stays the single source of truth.
P = json.load(open(_os.path.join(_HERE, "palette.json")))

def blend(f, b, a):
    F = [int(f[i:i+2], 16) for i in (1, 3, 5)]; B = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(F[k]*a + B[k]*(1-a)) for k in range(3))

# Ghostty's minimum-contrast covers the block cursor too: on a cell background
# under that ratio from cursor-color it swaps the cursor to black or white,
# whichever contrasts more, and the glyph under it (cursor-text) can vanish. The
# cursor lands on CurSearch after every search, so CurSearch is an ember tile
# below the cursor in both variants, as light as the cursor and slot-15 text
# allow. Above the cursor on light it could only sit 1.3:1 from Search, or
# lighter than Search and lost in the page. Both ratios fall as the tile
# lightens toward the cursor, so the passing range is one interval from Lr 0 and
# the bisection finds its edge. Read from ghostty/config, so the audit cannot
# drift from what Ghostty enforces. Ghostty takes the last occurrence of a key
# and lets config-file includes override it, which this parse does not follow.
_GHOSTTY = os.path.expanduser("~/.config/ghostty/config")
_cfg = open(_GHOSTTY).read()
_found = re.findall(r"^\s*minimum-contrast\s*=\s*([\d.]+)", _cfg, re.M)
if not _found or re.search(r"^\s*config-file\s*=", _cfg, re.M):
    raise SystemExit(f"neovim.py: no minimum-contrast in {_GHOSTTY}, or a config-file "
                     "include that could override it")
GHOSTTY_MIN_CONTRAST = float(_found[-1])

def cursearch(V, floor):
    C = chroma_for(EMBER)
    ok = lambda lr: (contrast(V["cursor"], hex_lr(lr, C, EMBER)[0]) >= GHOSTTY_MIN_CONTRAST + 0.1
                     and contrast(V["15"], hex_lr(lr, C, EMBER)[0]) >= floor + 0.1)
    near, far = 0.0, lch(V["cursor"])[0]
    if not ok(near):
        raise ValueError(f"no CurSearch tile below cursor {V['cursor']} keeps "
                         f"{GHOSTTY_MIN_CONTRAST + 0.1} to it and {floor + 0.1} to {V['15']}")
    for _ in range(50):
        mid = (near + far) / 2
        if ok(mid): near = mid
        else: far = mid
    return hex_lr(near, C, EMBER)[0]


# Syntax colours come from editor.py, not from the terminal slots. The terminal
# deliberately mutes cool hues as chrome, which in code would leave keywords,
# functions and types (the scaffold of every line) as the three most
# desaturated colours on screen. Surfaces and diagnostics still derive from the
# palette directly.
def groups(V, S):
    bg, fg, sel, cur = V["background"], V["foreground"], V["selection"], V["cursor"]
    c = {i: V[str(i)] for i in range(16)}
    X = syntax(V)
    mut = c[7] if lum(bg) < 0.18 else c[8]  # muted text; light's slot 7 is a surface
    vt = lambda i: blend(c[i], bg, 0.70)
    return [
        ("Normal", {"fg": fg, "bg": bg}),
        ("NormalFloat", {"fg": fg, "bg": S["panel"]}),
        ("FloatBorder", {"fg": c[8], "bg": S["panel"]}),
        ("FloatTitle", {"fg": c[3], "bg": S["panel"], "bold": True}),
        ("Cursor", {"fg": bg, "bg": cur}),
        ("lCursor", {"link": "Cursor"}),
        ("TermCursor", {"link": "Cursor"}),
        ("CursorLine", {"bg": S["line"]}),
        ("CursorColumn", {"bg": S["line"]}),
        ("ColorColumn", {"bg": S["line"]}),
        ("CursorLineNr", {"fg": c[3], "bold": True}),
        ("LineNr", {"fg": S["linenr"]}),
        ("SignColumn", {"fg": S["linenr"]}),
        ("FoldColumn", {"fg": S["linenr"]}),
        ("Folded", {"fg": c[8], "bg": S["line"]}),
        ("WinSeparator", {"fg": c[0]}),
        ("Visual", {"bg": sel}),
        ("VisualNOS", {"bg": sel}),
        ("Search", {"fg": fg, "bg": S["search"]}),
        ("CurSearch", {"fg": c[15], "bg": S["cursearch"], "bold": True}),
        ("IncSearch", {"link": "CurSearch"}),
        ("Substitute", {"fg": bg, "bg": c[9]}),
        ("MatchParen", {"bg": sel, "bold": True}),
        ("Pmenu", {"fg": fg, "bg": S["panel"]}),
        ("PmenuSel", {"bg": sel}),
        ("PmenuSbar", {"bg": S["panel"]}),
        ("PmenuThumb", {"bg": S["over"]}),
        ("StatusLine", {"fg": mut if lum(bg) < 0.18 else fg, "bg": S["panel"]}),
        ("StatusLineNC", {"fg": c[8], "bg": S["line"]}),
        ("WinBar", {"fg": fg, "bold": True}),
        ("WinBarNC", {"fg": c[8]}),
        ("TabLine", {"fg": c[8], "bg": S["line"]}),
        ("TabLineFill", {"bg": bg}),
        ("TabLineSel", {"fg": fg, "bg": S["panel"], "bold": True}),
        ("Title", {"fg": c[3], "bold": True}),
        ("Directory", {"fg": c[4]}),
        ("NonText", {"fg": S["ghost"]}),
        ("Whitespace", {"fg": S["ghost"]}),
        ("SpecialKey", {"fg": S["ghost"]}),
        ("EndOfBuffer", {"fg": S["ghost"]}),
        ("Conceal", {"fg": c[8]}),
        ("ErrorMsg", {"fg": c[1]}),
        ("WarningMsg", {"fg": c[3]}),
        ("MoreMsg", {"fg": c[2]}),
        ("Question", {"fg": c[4]}),
        ("ModeMsg", {"fg": fg, "bold": True}),
        ("MsgSeparator", {"link": "WinSeparator"}),
        ("QuickFixLine", {"bg": sel}),
        ("WildMenu", {"link": "PmenuSel"}),
        ("DiffAdd", {"bg": S["add"]}),
        ("DiffChange", {"bg": S["change"]}),
        ("DiffDelete", {"fg": S["ghost"], "bg": S["delete"]}),
        ("DiffText", {"bg": S["text"]}),
        ("Added", {"fg": c[2]}),
        ("Changed", {"fg": c[3]}),
        ("Removed", {"fg": c[1]}),
        ("SpellBad", {"undercurl": True, "sp": c[1]}),
        ("SpellCap", {"undercurl": True, "sp": c[4]}),
        ("SpellLocal", {"undercurl": True, "sp": c[6]}),
        ("SpellRare", {"undercurl": True, "sp": c[5]}),
        # syntax — legacy groups; treesitter captures link into these
        ("Comment", {"fg": c[8], "italic": True}),
        ("Constant", {"fg": X["constant"]}),
        ("String", {"fg": X["string"]}),
        ("Character", {"fg": X["string"]}),
        ("Number", {"fg": X["number"]}),
        ("Boolean", {"fg": X["number"]}),
        ("Float", {"fg": X["number"]}),
        ("Identifier", {"fg": fg}),
        ("Function", {"fg": X["function"]}),
        ("Statement", {"fg": X["keyword"]}),
        ("Keyword", {"fg": X["keyword"]}),
        ("Operator", {"fg": X["punct"]}),
        ("Exception", {"fg": X["error"]}),
        ("PreProc", {"fg": X["keyword"]}),
        ("Type", {"fg": X["type"]}),
        ("Special", {"fg": X["constant"]}),
        ("SpecialChar", {"fg": X["escape"]}),
        ("Delimiter", {"fg": X["punct"]}),
        ("SpecialComment", {"fg": c[8], "bold": True}),
        ("Debug", {"fg": X["error"]}),
        ("Underlined", {"fg": X["function"], "underline": True}),
        ("Bold", {"bold": True}),
        ("Italic", {"italic": True}),
        ("Error", {"fg": X["error"]}),
        ("Todo", {"fg": c[11], "bold": True, "italic": True}),
        # treesitter
        ("@variable", {"fg": fg}),
        ("@variable.builtin", {"fg": X["keyword"], "italic": True}),
        ("@variable.parameter", {"fg": X["param"]}),
        ("@variable.member", {"fg": X["member"]}),
        ("@property", {"fg": X["member"]}),
        ("@constant", {"link": "Constant"}),
        ("@constant.builtin", {"fg": X["constant"]}),
        ("@constant.macro", {"fg": c[11]}),
        ("@module", {"fg": fg}),
        ("@label", {"fg": c[13]}),
        ("@string", {"link": "String"}),
        ("@string.escape", {"fg": c[14]}),
        ("@string.regexp", {"fg": c[14]}),
        ("@string.special", {"fg": c[14]}),
        ("@string.special.url", {"fg": c[4], "underline": True}),
        ("@type", {"link": "Type"}),
        ("@type.builtin", {"link": "Type"}),
        ("@attribute", {"fg": c[3]}),
        ("@function", {"link": "Function"}),
        ("@function.builtin", {"fg": c[12]}),
        ("@function.macro", {"fg": c[13]}),
        ("@constructor", {"fg": c[6]}),
        ("@keyword", {"link": "Keyword"}),
        ("@keyword.import", {"fg": c[13]}),
        ("@keyword.directive", {"fg": c[13]}),
        ("@keyword.exception", {"fg": c[9]}),
        ("@operator", {"link": "Operator"}),
        ("@punctuation.delimiter", {"link": "Delimiter"}),
        ("@punctuation.bracket", {"link": "Delimiter"}),
        ("@punctuation.special", {"fg": c[14]}),
        ("@comment.todo", {"link": "Todo"}),
        ("@comment.error", {"fg": c[9], "bold": True}),
        ("@comment.warning", {"fg": c[3], "bold": True, "italic": True}),
        ("@comment.note", {"fg": c[12], "bold": True}),
        ("@markup.heading", {"fg": c[3], "bold": True}),
        ("@markup.strong", {"bold": True}),
        ("@markup.italic", {"italic": True}),
        ("@markup.strikethrough", {"strikethrough": True}),
        ("@markup.underline", {"underline": True}),
        ("@markup.link", {"fg": c[4], "underline": True}),
        ("@markup.link.label", {"fg": c[4]}),
        ("@markup.raw", {"fg": c[6]}),
        ("@markup.quote", {"fg": c[8], "italic": True}),
        ("@markup.list", {"fg": c[5]}),
        ("@tag", {"fg": c[5]}),
        ("@tag.attribute", {"fg": c[3]}),
        ("@tag.delimiter", {"link": "Delimiter"}),
        ("@diff.plus", {"fg": c[2]}),
        ("@diff.minus", {"fg": c[1]}),
        ("@diff.delta", {"fg": c[3]}),
        # diagnostics
        ("DiagnosticError", {"fg": c[1]}),
        ("DiagnosticWarn", {"fg": c[3]}),
        ("DiagnosticInfo", {"fg": c[4]}),
        ("DiagnosticHint", {"fg": c[6]}),
        ("DiagnosticOk", {"fg": c[2]}),
        ("DiagnosticVirtualTextError", {"fg": vt(1)}),
        ("DiagnosticVirtualTextWarn", {"fg": vt(3)}),
        ("DiagnosticVirtualTextInfo", {"fg": vt(4)}),
        ("DiagnosticVirtualTextHint", {"fg": vt(6)}),
        ("DiagnosticUnderlineError", {"undercurl": True, "sp": c[1]}),
        ("DiagnosticUnderlineWarn", {"undercurl": True, "sp": c[3]}),
        ("DiagnosticUnderlineInfo", {"undercurl": True, "sp": c[4]}),
        ("DiagnosticUnderlineHint", {"undercurl": True, "sp": c[6]}),
        ("DiagnosticDeprecated", {"strikethrough": True, "sp": c[8]}),
        # lsp
        ("LspReferenceText", {"bg": S["over"]}),
        ("LspReferenceRead", {"bg": S["over"]}),
        ("LspReferenceWrite", {"bg": S["over"], "underline": True}),
        ("LspInlayHint", {"fg": blend(c[8], bg, 0.85), "italic": True}),
        ("LspSignatureActiveParameter", {"bg": sel, "bold": True}),
        ("LspCodeLens", {"fg": S["linenr"]}),
        # gitsigns
        ("GitSignsAdd", {"fg": c[2]}),
        ("GitSignsChange", {"fg": c[3]}),
        ("GitSignsDelete", {"fg": c[1]}),
        ("GitSignsCurrentLineBlame", {"fg": S["linenr"], "italic": True}),
        # telescope
        ("TelescopeNormal", {"link": "NormalFloat"}),
        ("TelescopeBorder", {"link": "FloatBorder"}),
        ("TelescopePromptNormal", {"fg": fg, "bg": S["over"]}),
        ("TelescopePromptBorder", {"fg": c[8], "bg": S["over"]}),
        ("TelescopePromptTitle", {"fg": bg, "bg": cur, "bold": True}),
        ("TelescopePreviewTitle", {"fg": bg, "bg": c[2], "bold": True}),
        ("TelescopeResultsTitle", {"fg": c[8], "bg": S["panel"]}),
        ("TelescopeSelection", {"bg": sel}),
        ("TelescopeSelectionCaret", {"fg": c[9], "bg": sel}),
        ("TelescopeMatching", {"fg": c[11], "bold": True}),
        # blink.cmp
        ("BlinkCmpMenu", {"link": "Pmenu"}),
        ("BlinkCmpMenuBorder", {"link": "FloatBorder"}),
        ("BlinkCmpMenuSelection", {"link": "PmenuSel"}),
        ("BlinkCmpLabelMatch", {"fg": c[11], "bold": True}),
        ("BlinkCmpDoc", {"link": "NormalFloat"}),
        ("BlinkCmpDocBorder", {"link": "FloatBorder"}),
        ("BlinkCmpSignatureHelp", {"link": "NormalFloat"}),
        ("BlinkCmpGhostText", {"link": "NonText"}),
        # dap
        ("DapBreakpoint", {"fg": c[1]}),
        ("DapBreakpointCondition", {"fg": c[3]}),
        ("DapLogPoint", {"fg": c[4]}),
        ("DapStopped", {"fg": c[11]}),
    ]

FLAGS = ("bold", "italic", "underline", "undercurl", "strikethrough")
def lua_opts(o):
    if "link" in o: return f'{{ link = "{o["link"]}" }}'
    parts = [f'{k} = "{o[k]}"' for k in ("fg", "bg", "sp") if k in o]
    parts += [f"{k} = true" for k in FLAGS if o.get(k)]
    return "{ " + ", ".join(parts) + " }"

HDR = ("-- Umber — an earth palette.\n"
       "-- Generated by umber/neovim.py — do not edit by hand.\n"
       "-- Syntax accents come from umber/editor.py: chroma is level across\n"
       "-- keywords, functions, types, strings and literals, so hue separates\n"
       "-- them and no role is muted relative to another.\n"
       "-- Both variants, picked by 'background', which Neovim sets from the\n"
       "-- terminal (OSC 11, and DEC 2031 when Ghostty follows the appearance).\n"
       "-- Never set 'background' here: Neovim then stops updating it at VimEnter,\n"
       "-- and drops the scheme on the next change.\n")

# Dark first: an unanswered OSC 11 leaves 'background' at its default "dark",
# and check.py's cross-emitter check reads the first Keyword it finds.
def branches(built, body):
    assert [b for _, b, _, _ in built] == ["dark", "light"]
    out = ['if vim.o.background == "dark" then']
    for i, v in enumerate(built):
        if i: out.append("else")
        out += ["  " + l if l else l for l in body(*v)]
    return out + ["end"]

def render(built):
    out = [HDR, 'vim.cmd("highlight clear")',
           'if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end',
           'vim.g.colors_name = "umber"', "", "local set = vim.api.nvim_set_hl"]
    out += branches(built, lambda name, background, V, S:
                    [f'vim.g.terminal_color_{i} = "{V[str(i)]}"' for i in range(16)] + [""]
                    + [f'set(0, "{g}", {lua_opts(o)})' for g, o in groups(V, S)])
    return "\n".join(out) + "\n"

MODES = ("normal", "insert", "visual", "replace", "command", "terminal")
# lualine's "auto" theme dofiles this on every ColorScheme and OptionSet
# background, so it branches the same way the colorscheme does.
def render_lualine(built):
    def body(name, background, V, S):
        bg, fg = V["background"], V["foreground"]
        c = {i: V[str(i)] for i in range(16)}
        accent = {"normal": V["cursor"], "insert": c[2], "visual": c[5],
                  "replace": c[1], "command": c[3], "terminal": c[6]}
        def sec(f, b, gui=None):
            g = f', gui = "{gui}"' if gui else ""
            return f'{{ fg = "{f}", bg = "{b}"{g} }}'
        out = ["return {"]
        for m in MODES:
            out += [f"  {m} = {{", f'    a = {sec(bg, accent[m], "bold")},',
                    f'    b = {sec(fg, S["over"])},', f'    c = {sec(c[8], S["line"])},', "  },"]
        out += ["  inactive = {", f'    a = {sec(c[8], S["line"])},',
                f'    b = {sec(c[8], S["line"])},', f'    c = {sec(c[8], S["line"])},', "  },", "}"]
        return out
    out = ["-- Generated by umber/neovim.py — do not edit by hand."] + branches(built, body)
    return "\n".join(out) + "\n"

VARIANTS = (("umber", "dark", P["dark"]), ("umber-light", "light", P["light"]))
FLOOR = {"umber": 4.5, "umber-light": 4.5}

COLORS = os.path.expanduser("~/.config/nvim/colors")
THEMES = os.path.expanduser("~/.config/nvim/lua/lualine/themes")
os.makedirs(COLORS, exist_ok=True); os.makedirs(THEMES, exist_ok=True)

# Audit first, write only if every floor holds — never ship a bad ramp into the
# live config.
failures = []
built = []
for name, background, V in VARIANTS:
    f = FLOOR[name]; fg, bg = V["foreground"], V["background"]
    S = surfaces(V)
    S["cursearch"] = cursearch(V, f)
    built.append((name, background, V, S))
    checks = [(s, contrast(fg, S[s]), f) for s in ("line", "panel", "over", "add", "change", "delete", "text", "search")]
    checks += [("comment/panel", contrast(V["8"], S["panel"]), f * 0.66),
               ("linenr", contrast(S["linenr"], bg), 1.7),
               ("match/panel", contrast(V["11"], S["panel"]), f * 0.66)]
    G = dict(groups(V, S))
    checks += [("cursearch", contrast(G["CurSearch"]["fg"], G["CurSearch"]["bg"]), f)]
    # Every filled group the cursor can sit on. Cursor only reaches the terminal
    # through TermCursor, as the cursor colour itself, Substitute only shows
    # while the cursor is in the command line, and Telescope titles sit in
    # float borders.
    unreachable = {"Cursor", "Substitute", "TelescopePromptTitle", "TelescopePreviewTitle"}
    fills = sorted((contrast(V["cursor"], o["bg"]), g) for g, o in G.items()
                   if "bg" in o and g not in unreachable)
    # Print the worst fill, or every one below the floor.
    checks += ([(f"cursor/{g}", x, GHOSTTY_MIN_CONTRAST) for x, g in fills if x < GHOSTTY_MIN_CONTRAST]
               or [(f"cursor/{fills[0][1]}", fills[0][0], GHOSTTY_MIN_CONTRAST)])
    bad = [n for n, x, floor in checks if x < floor]
    bad += [f"syntax:{k}" for k, _ in audit(V, syntax(V), f)]
    print(f"{name:<12} " + " ".join(f"{n} {x:4.2f}" for n, x, _ in checks))
    print(f"             floor {f}  {'PASS' if not bad else 'BELOW: ' + str(bad)}")
    failures += [f"{name}:{n}" for n in bad]
enforce(failures)

write_atomic(os.path.join(COLORS, "umber.lua"), render(built))
write_atomic(os.path.join(THEMES, "umber.lua"), render_lualine(built))
print(f"wrote umber ({len(built)} variants) -> {COLORS}, lualine theme -> {THEMES}")
