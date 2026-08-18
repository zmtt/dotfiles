"""Verify the whole toolchain. One command, no hand-maintained coverage list.

Every earlier round of this project was verified by running a remembered list of
scripts. A list you maintain by hand has gaps you cannot see: two renderers sat
broken through several passes that each reported "all generators OK", because
the renderers were never in the list.

So MANIFEST below must classify every .py file in this directory, and the first
check fails if one is missing. Adding a script without saying what it is is
itself an error. Everything else here is derived from that classification.

    python3 check.py            fast checks
    python3 check.py --slow     also runs the sampling optimiser
"""
import glob
import json
import os
import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

LIBRARY = "library"      # imported only; must import cleanly with no side effects
GENERATOR = "generator"  # run with no arguments; writes themes
AUDIT = "audit"          # run with no arguments; must exit 0
TOOL = "tool"            # slow or interactive; only run under --slow
MANUAL = "manual"        # needs arguments or the venv; not runnable here
SELF = "self"

MANIFEST = {
    "model.py": LIBRARY, "palette.py": LIBRARY, "perceptual.py": LIBRARY,
    "editor.py": LIBRARY, "studio.py": LIBRARY,
    "build.py": GENERATOR, "claude-chrome.py": GENERATOR, "neovim.py": GENERATOR,
    "intellij.py": GENERATOR, "jetbrains-ui.py": GENERATOR, "xcode.py": GENERATOR,
    "bat-theme.py": GENERATOR,
    "render-specimen.py": GENERATOR, "render-code.py": GENERATOR,
    "audit.py": AUDIT,
    "optimise-stagger.py": TOOL,
    "sample-screenshot.py": MANUAL,
    "check.py": SELF,
}

# Where generated artefacts land. Anything outside these is a bug.
OUTPUTS = {
    "ghostty": "~/.config/ghostty/themes/umber*",
    "nvim": "~/.config/nvim/colors/umber*.lua",
    "lualine": "~/.config/nvim/lua/lualine/themes/umber*.lua",
    "bat": "~/.config/bat/themes/Umber*.tmTheme",
    "claude": "~/.claude/themes/umber*.json",
    "xcode": "~/Library/Developer/Xcode/UserData/FontAndColorThemes/Umber*.xccolortheme",
    "icls": "~/Library/Application Support/Google/AndroidStudio*/colors/Umber*.icls",
    "jar": "~/Library/Application Support/Google/AndroidStudio*/plugins/umber-theme.jar",
    "palette": "~/.config/umber/palette.json",
}

# Which generator is responsible for which family. MANIFEST makes "I added a
# script" impossible to forget; this makes "I added a script that writes
# somewhere new" impossible to forget too, which is the same hole on the other
# axis. An empty list means the script produces nothing worth verifying.
WRITES = {
    "build.py": ["ghostty", "palette"], "neovim.py": ["nvim", "lualine"],
    "bat-theme.py": ["bat"], "claude-chrome.py": ["claude"], "xcode.py": ["xcode"],
    "intellij.py": ["icls"], "jetbrains-ui.py": ["jar"],
    "render-specimen.py": [], "render-code.py": [],
}

# GIT_DIR and friends in the environment silently retarget an explicit
# --git-dir's index. That produced a false reading earlier in this project.
GIT_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

failures = []
notes = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(name)
    return ok


def run(script, timeout=300):
    return subprocess.run([sys.executable, os.path.join(HERE, script)],
                          capture_output=True, text=True, timeout=timeout, cwd=HERE)


def paths(pattern):
    return sorted(glob.glob(os.path.expanduser(pattern)))


def tail(result):
    lines = result.stderr.strip().splitlines()
    return lines[-1] if result.returncode and lines else ""


def digest():
    """Content of every generated artefact, keyed by path."""
    out = {}
    for pattern in OUTPUTS.values():
        for p in paths(pattern):
            out[p] = open(p, "rb").read()
    return out


def main(slow=False):
    # A stale bytecode cache can make a reverted source file still behave as its
    # broken version, which has produced false results more than once here.
    for cache in glob.glob(os.path.join(HERE, "__pycache__")):
        for f in glob.glob(os.path.join(cache, "*")):
            os.unlink(f)
        os.rmdir(cache)

    print("manifest")
    on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(HERE, "*.py"))}
    missing = sorted(on_disk - set(MANIFEST))
    stale = sorted(set(MANIFEST) - on_disk)
    check("every .py is classified", not missing, f"unclassified: {missing}" if missing else "")
    check("no stale manifest entries", not stale, f"missing from disk: {stale}" if stale else "")
    gens = {n for n, k in MANIFEST.items() if k == GENERATOR}
    check("every generator declares what it writes", gens == set(WRITES),
          f"{sorted(gens ^ set(WRITES))}" if gens != set(WRITES) else "")
    claimed = {k for keys in WRITES.values() for k in keys}
    check("every output family has a generator", claimed == set(OUTPUTS),
          f"{sorted(claimed ^ set(OUTPUTS))}" if claimed != set(OUTPUTS) else "")

    print("\nimports and runs")
    for name, kind in sorted(MANIFEST.items()):
        if kind == LIBRARY:
            r = subprocess.run([sys.executable, "-c", f"import importlib;importlib.import_module('{name[:-3]}')"],
                               capture_output=True, text=True, cwd=HERE)
            check(f"{name} imports", r.returncode == 0, tail(r))
        elif kind in (GENERATOR, AUDIT):
            r = run(name)
            check(f"{name} runs", r.returncode == 0, tail(r))
        elif kind == TOOL and slow:
            r = run(name, timeout=1800)
            check(f"{name} runs", r.returncode == 0, tail(r))
        elif kind == TOOL:
            notes.append(f"{name} skipped (use --slow)")
        elif kind == MANUAL:
            notes.append(f"{name} needs arguments or the venv; not run here")
        elif kind != SELF:
            # Otherwise a typo in a MANIFEST value matches no branch and the
            # script is silently never run, which is what MANIFEST prevents.
            check(f"{name} has a known kind", False, f"unknown kind {kind!r}")

    print("\nidempotency")
    expected = {p for pattern in OUTPUTS.values() for p in paths(pattern)}
    before = digest()
    for name, kind in sorted(MANIFEST.items()):
        if kind == GENERATOR:
            run(name)
    after = digest()
    changed = sorted(os.path.basename(k) for k in before if before.get(k) != after.get(k))
    check("a second run reproduces every artefact", not changed, f"differ: {changed}" if changed else "")
    check("no artefact vanished", expected <= set(after),
          f"missing: {sorted(os.path.basename(p) for p in expected - set(after))}"
          if expected - set(after) else "")
    check("every declared output family produced files",
          all(paths(pat) for pat in OUTPUTS.values()),
          f"empty: {[k for k, pat in OUTPUTS.items() if not paths(pat)]}"
          if not all(paths(pat) for pat in OUTPUTS.values()) else "")

    print("\nemitted formats")
    for p in paths(OUTPUTS["icls"]):
        try:
            ET.parse(p); ok = True
        except Exception as e:
            ok = False; notes.append(f"{p}: {e}")
        check(f"{os.path.basename(p)} is XML", ok)
    for key in ("xcode", "bat"):
        for p in paths(OUTPUTS[key]):
            try:
                plistlib.load(open(p, "rb")); ok = True
            except Exception:
                ok = False
            check(f"{os.path.basename(p)} is a plist", ok)
    for p in paths(OUTPUTS["claude"]):
        try:
            json.load(open(p)); ok = True
        except Exception:
            ok = False
        check(f"{os.path.basename(p)} is JSON", ok)
    for p in paths(OUTPUTS["jar"]):
        z = zipfile.ZipFile(p)
        check("jar is intact", z.testzip() is None)
        schemes = [n for n in z.namelist() if n.startswith("themes/") and n.endswith(".xml")]
        declared = [n for n in z.namelist() if n.endswith(".theme.json")]
        check("jar carries an editor scheme per theme", len(schemes) == len(declared),
              f"{len(schemes)} scheme(s), {len(declared)} theme(s)")

    print("\nfile modes")
    bad = [p for pattern in OUTPUTS.values() for p in paths(pattern)
           if os.stat(p).st_mode & 0o777 != 0o644]
    check("every artefact is 0644", not bad,
          f"{[os.path.basename(p) for p in bad]}" if bad else "")

    print("\ncross-emitter agreement")
    P = json.load(open(os.path.join(HERE, "palette.json")))
    sys.path.insert(0, HERE)
    from editor import syntax
    want = syntax(P["dark"])
    seen = {}
    lua = open(paths(OUTPUTS["nvim"])[-1]).read() if paths(OUTPUTS["nvim"]) else ""
    for role, group in (("keyword", "Keyword"), ("type", "Type"), ("function", "Function")):
        m = re.search(rf'"{group}", {{ fg = "(#[0-9a-f]{{6}})"', lua)
        seen.setdefault(role, set()).add(m.group(1) if m else None)
    icls = open([p for p in paths(OUTPUTS["icls"]) if p.endswith("Umber.icls")][0]).read()
    for role, key in (("keyword", "DEFAULT_KEYWORD"), ("type", "DEFAULT_CLASS_NAME"),
                      ("function", "DEFAULT_FUNCTION_DECLARATION")):
        m = re.search(rf'name="{key}".*?FOREGROUND" value="([0-9a-f]{{6}})"', icls, re.S)
        seen[role].add("#" + m.group(1) if m else None)
    tm = plistlib.load(open([p for p in paths(OUTPUTS["bat"]) if p.endswith("Umber.tmTheme")][0], "rb"))
    byname = {r["name"]: r["settings"].get("foreground") for r in tm["settings"] if "name" in r}
    for role, group in (("keyword", "Keyword"), ("type", "Type"), ("function", "Function")):
        seen[role].add(byname.get(group))
    for role, values in sorted(seen.items()):
        check(f"{role} agrees across editors", values == {want[role]},
              f"{sorted(v for v in values if v)}" if values != {want[role]} else want[role])

    print("\nrepository")
    tracked = [".config/ghostty/themes", ".config/nvim/colors",
               ".config/nvim/lua/lualine/themes", ".config/bat/themes",
               ".claude/themes", ".claude/statusline-command.py",
               ".config/fish/functions/umber.fish", ".config/umber"]
    home = os.path.expanduser("~")
    r = subprocess.run(["git", "--git-dir", os.path.join(home, ".dotfiles"),
                        "--work-tree", home, "status", "--short", "--"]
                       + [os.path.join(home, p) for p in tracked],
                       capture_output=True, text=True, cwd=home, env=GIT_ENV)
    check("git status is readable", r.returncode == 0, r.stderr.strip()[:80])
    dirty = [l for l in r.stdout.splitlines() if l.strip()]
    check("no tracked file drifted", not dirty, "; ".join(dirty) if dirty else "")

    if notes:
        print("\nnotes")
        for n in notes:
            print(f"  - {n}")
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all checks passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main("--slow" in sys.argv))
