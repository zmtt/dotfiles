"""Locating the Android Studio install.

Both intellij.py and jetbrains-ui.py write into the same config directory and
must agree on which one. They used to resolve it separately — a numeric-version
max in one, a lexicographic sort in the other — which disagree as soon as a
second install exists. The jar would then land beside a different .icls than the
one it embeds, and the packaging step silently shipped a jar whose themes
referenced an editor scheme that was not in it.

One rule now serves both: skip qualified builds (Preview, Beta), newest first.
"""
import glob
import os
import re

CONFIG_GLOB = "~/Library/Application Support/Google/AndroidStudio*"
APP_GLOB = "/Applications/Android Studio*.app"
PLATFORM_JAR = "lib/intellij.platform.ide.impl.jar"

# Digits directly after the product name mean a plain versioned install;
# anything else in that position is a qualifier such as Preview or Beta.
CONFIG_NAME = re.compile(r"^AndroidStudio(\d[\d.]*)$")
APP_NAME = re.compile(r"^Android Studio(?: (\d[\d.]*))?\.app$")

NEWEST = (float("inf"),)


def _stable(pattern, name_re):
    """Unqualified installs matching the glob, newest version first.

    An unversioned name ("Android Studio.app") sorts newest: it is the current
    install, while a version-suffixed sibling is an archived older one.
    """
    found = []
    for path in glob.glob(os.path.expanduser(pattern)):
        m = name_re.match(os.path.basename(path))
        if not m:
            continue
        try:
            v = tuple(int(x) for x in m.group(1).split(".")) if m.group(1) else NEWEST
        except ValueError:
            continue          # a trailing or doubled dot is not a version
        found.append((v, path))
    return [p for _, p in sorted(found, reverse=True)]


def config_dir():
    dirs = _stable(CONFIG_GLOB, CONFIG_NAME)
    if not dirs:
        raise SystemExit(f"no Android Studio config directory matching {CONFIG_GLOB}")
    return dirs[0]


def platform_jar():
    """The app bundle's platform jar, which carries the stock UI themes."""
    for app in _stable(APP_GLOB, APP_NAME):
        jar = os.path.join(app, "Contents", PLATFORM_JAR)
        if os.path.exists(jar):
            return jar
    raise SystemExit(f"Android Studio not found under {APP_GLOB}; "
                     "jetbrains-ui.py reads its theme structure from the app bundle")
