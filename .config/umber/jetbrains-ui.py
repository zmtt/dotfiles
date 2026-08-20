"""Build the Android Studio UI theme plugin.

An .icls only themes the editor pane. The surrounding IDE — tool windows, tabs,
sidebar, status bar — comes from a UI theme, which JetBrains loads only from a
plugin. A theme plugin is pure resources, so this composes one directly: no
Gradle, no compilation.

The key structure is read out of the installed Android Studio at build time
rather than vendored here. That keeps the platform's file where it is licensed,
means only Umber's own colours land in this repo, and picks up new UI keys when
Studio updates.

The platform's New UI theme is built from eight ramps — Gray, Blue, Green, Red,
Purple, Teal, Yellow, Orange — each running dark to light. Retinting the ramps
recolours everything routed through a ramp name: each step keeps its own
lightness and its position within its ramp, and takes Umber's hue and chroma for
that family.

The ui block also carries raw hex literals that no ramp name covers. Opaque
chromatic ones (the git-log current-branch wash, the run widget's green, the
progress counter) are re-hued into the nearest Umber accent family, keeping
their own lightness and capping chroma at that family's ceiling — except the
identity palettes (RecentProject avatars, CodeWithMe users, Recap branding),
whose whole purpose is to differ per project or user. Translucent and
near-neutral literals pass through: they blend with the retinted surfaces
anyway. The surfaces that matter most are still overridden explicitly below.
"""
import io, json, os, re, zipfile
from editor import surfaces
from perceptual import hex_lr, lch
from palette import lum
from model import EMBER, chroma_for
from studio import config_dir, platform_jar
from perceptual import write_atomic

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "palette.json")))

TEMPLATES = {"dark": "themes/expUI/expUI_dark.theme.json",
             "light": "themes/expUI/expUI_light.theme.json"}

# Which Umber hue each platform ramp becomes, and the chroma that family is
# allowed at full strength. Orange maps to the ember, the palette's signature.
NEUTRAL, EMBER_HUE = "neutral", "ember"   # hue sources that are not a palette slot

# Below this chroma a colour reads as neutral: the retint caps unramped colours
# to it, and the literal pass leaves anything under it alone.
NEAR_NEUTRAL_C = 0.020

# Which palette slot each platform ramp borrows. Both hue and chroma come from
# that slot at build time — hardcoding the chroma made this the one surface a
# model.py change did not reach, and it silently drifted per variant because the
# literals were copied from the dark palette.
RAMPS = {
    "Gray":   NEUTRAL,
    "Red":    "1",
    "Yellow": "3",
    "Green":  "2",
    "Teal":   "6",
    "Blue":   "4",
    "Purple": "5",
    "Orange": EMBER_HUE,
}
NEUTRAL_CHROMA = 0.016


def _hue_and_chroma(source, V, neutral_hue):
    """Hue and chroma ceiling for a ramp, both taken from the live palette."""
    if source == NEUTRAL:
        return neutral_hue, NEUTRAL_CHROMA
    if source == EMBER_HUE:
        return EMBER, chroma_for(EMBER)
    L, C, H = lch(V[source])
    return H, C


def read_template(variant):
    with zipfile.ZipFile(platform_jar()) as z:
        return json.loads(z.read(TEMPLATES[variant]))


def retint_ramps(colors, V):
    """Map every ramp step into Umber, keeping its lightness and ramp position."""
    nh = lch(V["foreground"])[2]
    families = {}
    for name in colors:
        m = re.match(r"([A-Za-z]+)(\d+)$", name)
        if m and m.group(1) in RAMPS:
            families.setdefault(m.group(1), []).append(name)

    out = {}
    for family, names in families.items():
        source = RAMPS[family]
        hue, ceiling = _hue_and_chroma(source, V, nh)
        peak = max(lch(colors[n])[1] for n in names) or 1.0
        for name in names:
            lr, C, _ = lch(colors[name])          # lch returns Lr, not Oklab L
            # position within the ramp's own saturation curve, so its pale and
            # near-neutral ends stay pale instead of snapping to full chroma
            out[name] = hex_lr(lr, ceiling * (C / peak), hue)[0]

    for name, hx in colors.items():          # anything outside the eight ramps
        if name not in out:
            lr, C, _ = lch(hx)
            out[name] = hex_lr(lr, min(C, NEAR_NEUTRAL_C), nh)[0]
    return out


# Palettes whose whole purpose is to differ per project, user, or product.
IDENTITY = ("RecentProject.", "CodeWithMe.", "Recap.")


def retint_literals(ui, V):
    """Re-hue opaque chromatic hex literals into the nearest Umber family,
    in place."""
    slots = [lch(V[s]) for s in ("1", "2", "3", "4", "5", "6")]

    def snap(hx):
        lr, C, H = lch(hx)
        if C < NEAR_NEUTRAL_C:
            return hx                          # near-neutral: blends fine
        _, sc, sh = min(slots, key=lambda s: 180 - abs(abs(s[2] - H) - 180))
        return hex_lr(lr, min(C, sc), sh)[0]

    def walk(node, path=""):
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            if isinstance(v, dict):
                walk(v, p)
            elif (isinstance(v, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", v)
                  and not p.startswith(IDENTITY)):
                node[k] = snap(v)
    walk(ui)


def build(variant, name):
    V = P[variant]
    theme = read_template("light" if variant == "light" else "dark")
    dark = lum(V["background"]) < 0.18
    S = surfaces(V)

    theme["colors"] = retint_ramps(theme["colors"], V)
    retint_literals(theme.get("ui", {}), V)
    theme["name"] = name
    theme["dark"] = dark
    theme["editorScheme"] = "/themes/%s.xml" % variant

    # These must agree exactly with the editor scheme or a seam shows where the
    # editor meets its own tab, so they come from the same surfaces() ramp the
    # scheme uses rather than being re-derived here: intellij.py solves the
    # tree's file-status colours against S["line"] on the promise that this is
    # the tree's ground.
    theme.setdefault("ui", {}).setdefault("*", {}).update({
        "background": S["line"],
        "foreground": V["foreground"],
        "selectionBackground": V["selection"],
        "selectionForeground": V["foreground"],
        "borderColor": S["panel"],
        "separatorColor": S["panel"],
    })
    # Merge, never assign: the platform sets more here than we override, and
    # most of it already points at ramp names we retint (tooltip error/success
    # backgrounds, the under-tabs border). Replacing the section drops those to
    # the base theme's cool greys and loses the tab underline geometry.
    theme["ui"].setdefault("Editor", {}).update({
        "background": V["background"], "shortcutForeground": V["cursor"]})
    theme["ui"].setdefault("EditorTabs", {}).update({
        "underlinedTabBackground": V["background"],
        "underlineColor": V["cursor"],
        "background": S["line"]})
    return theme


def package(jar_path, built, colors_dir):
    plugin = """<idea-plugin>
    <id>dev.umber.theme</id>
    <name>Umber</name>
    <version>1.0.0</version>
    <vendor>generated</vendor>
    <description><![CDATA[Umber UI theme and editor schemes, generated from
    ~/.config/umber so the IDE matches the terminal.]]></description>
    <idea-version since-build="222"/>
    <depends>com.intellij.modules.platform</depends>
    <extensions defaultExtensionNs="com.intellij">
%s
    </extensions>
</idea-plugin>
"""
    providers = "\n".join(
        '        <themeProvider id="dev.umber.theme.%s" path="/themes/%s.theme.json"/>' % (v, v)
        for v, _, _ in built)
    # Build in memory, then write atomically: ZipFile(path, "w") truncates the
    # installed jar before the first entry is added. Entry timestamps are fixed
    # so the same inputs give the same bytes.
    buf = io.BytesIO()
    stamp = (1980, 1, 1, 0, 0, 0)
    def add(z, name, data):
        info = zipfile.ZipInfo(name, date_time=stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, data)
    with zipfile.ZipFile(buf, "w") as z:
        add(z, "META-INF/plugin.xml", plugin % providers)
        for variant, theme, icls in built:
            add(z, "themes/%s.theme.json" % variant, json.dumps(theme, indent=2))
            src = os.path.join(colors_dir, icls)
            if not os.path.exists(src):
                raise SystemExit(f"{icls} missing from {colors_dir}; run intellij.py first "
                                 "(a jar without it declares an editorScheme it does not carry)")
            add(z, "themes/%s.xml" % variant, open(src, "rb").read())
    write_atomic(jar_path, buf.getvalue())
    return jar_path


if __name__ == "__main__":
    root = config_dir()
    colors_dir = os.path.join(root, "colors")
    plugins_dir = os.path.join(root, "plugins")
    os.makedirs(plugins_dir, exist_ok=True)

    built = []
    for variant, name, icls in (("dark", "Umber", "Umber.icls"),
                                ("light", "Umber Light", "Umber Light.icls")):
        if variant not in P:
            continue
        theme = build(variant, name)
        built.append((variant, theme, icls))
        print(f"  {name:<12} {len(theme['colors']):>3} ramp colours   "
              f"editor bg {theme['ui']['Editor']['background']}   "
              f"accent {P[variant]['cursor']}")

    jar = package(os.path.join(plugins_dir, "umber-theme.jar"), built, colors_dir)
    print(f"\nwrote {jar.replace(os.path.expanduser('~'), '~')}")
