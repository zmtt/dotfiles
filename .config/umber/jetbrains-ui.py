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
Purple, Teal, Yellow, Orange — each running dark to light, and its ui block
references those by name with no raw hex. So retinting the ramps replaces the
theme completely: each step keeps its own lightness and its position within its
ramp, and takes Umber's hue and chroma for that family.
"""
import json, os, re, glob, zipfile
from perceptual import hex_lr, lch
from palette import lum

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "palette.json")))
EMBER = 48.0

APP = "/Applications/Android Studio.app/Contents"
PLATFORM_JAR = "lib/intellij.platform.ide.impl.jar"
TEMPLATES = {"dark": "themes/expUI/expUI_dark.theme.json",
             "light": "themes/expUI/expUI_light.theme.json"}

# Which Umber hue each platform ramp becomes, and the chroma that family is
# allowed at full strength. Orange maps to the ember, the palette's signature.
RAMPS = {
    "Gray":   ("neutral", 0.016),
    "Red":    ("1", 0.130),
    "Yellow": ("3", 0.128),
    "Green":  ("2", 0.090),
    "Teal":   ("6", 0.063),
    "Blue":   ("4", 0.059),
    "Purple": ("5", 0.070),
    "Orange": (None, 0.120),
}


def studio_root():
    roots = sorted(glob.glob(os.path.expanduser(
        "~/Library/Application Support/Google/AndroidStudio*")))
    if not roots:
        raise SystemExit("no Android Studio configuration directory found")
    return roots[-1]


def read_template(variant):
    with zipfile.ZipFile(os.path.join(APP, PLATFORM_JAR)) as z:
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
        slot, ceiling = RAMPS[family]
        hue = nh if slot == "neutral" else (EMBER if slot is None else lch(V[slot])[2])
        peak = max(lch(colors[n])[1] for n in names) or 1.0
        for name in names:
            lr, C, _ = lch(colors[name])          # lch returns Lr, not Oklab L
            # position within the ramp's own saturation curve, so its pale and
            # near-neutral ends stay pale instead of snapping to full chroma
            out[name] = hex_lr(lr, ceiling * (C / peak), hue)[0]

    for name, hx in colors.items():          # anything outside the eight ramps
        if name not in out:
            lr, C, _ = lch(hx)
            out[name] = hex_lr(lr, min(C, 0.020), nh)[0]
    return out


def build(variant, name):
    V = P[variant]
    theme = read_template("light" if variant == "light" else "dark")
    dark = lum(V["background"]) < 0.18
    nh = lch(V["foreground"])[2]
    bglr = lch(V["background"])[0]
    d = 1 if dark else -1
    surf = lambda off, C=0.017: hex_lr(bglr + d * off, C, nh)[0]

    theme["colors"] = retint_ramps(theme["colors"], V)
    theme["name"] = name
    theme["dark"] = dark
    theme["editorScheme"] = "/themes/%s.xml" % variant

    # These must agree exactly with the editor scheme or a seam shows where the
    # editor meets its own tab, so they are set rather than left to a ramp.
    theme.setdefault("ui", {}).setdefault("*", {}).update({
        "background": surf(0.045),
        "foreground": V["foreground"],
        "selectionBackground": V["selection"],
        "selectionForeground": V["foreground"],
        "borderColor": surf(0.075),
        "separatorColor": surf(0.075),
    })
    theme["ui"]["Editor"] = {"background": V["background"],
                             "shortcutForeground": V["cursor"]}
    theme["ui"]["EditorTabs"] = {"underlinedTabBackground": V["background"],
                                 "underlineColor": V["cursor"],
                                 "background": surf(0.045)}
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
    with zipfile.ZipFile(jar_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("META-INF/plugin.xml", plugin % providers)
        for variant, theme, icls in built:
            z.writestr("themes/%s.theme.json" % variant, json.dumps(theme, indent=2))
            src = os.path.join(colors_dir, icls)
            if os.path.exists(src):
                z.write(src, "themes/%s.xml" % variant)
    return jar_path


if __name__ == "__main__":
    root = studio_root()
    colors_dir = os.path.join(root, "colors")
    plugins_dir = os.path.join(root, "plugins")
    os.makedirs(plugins_dir, exist_ok=True)

    built = []
    for variant, name, icls in (("dark", "Umber", "Umber.icls"),
                                ("night", "Umber Night", "Umber Night.icls"),
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
