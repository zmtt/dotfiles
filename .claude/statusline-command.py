#!/usr/bin/env python3
import json, re, signal, subprocess, sys, os

try:
    # stdin is the one unbounded wait; everything downstream has a timeout.
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(5)
    data = json.load(sys.stdin)
    signal.alarm(0)

    # `or {}` throughout, not a get() default: these keys can be present-but-null.
    cwd = (data.get("workspace") or {}).get("current_dir") or os.getcwd()
    used_pct = (data.get("context_window") or {}).get("used_percentage")
    if not isinstance(used_pct, (int, float)) or isinstance(used_pct, bool) or abs(used_pct) > 1e6:
        used_pct = None

    model_label = (data.get("model") or {}).get("display_name") or "Claude"

    total_duration_ms = (data.get("cost") or {}).get("total_duration_ms") or 0
    if not isinstance(total_duration_ms, (int, float)) or isinstance(total_duration_ms, bool) \
            or not 0 <= total_duration_ms < 1e15:
        total_duration_ms = 0

    def clean(text):
        """A directory name may contain newlines and escapes; the status line is
        one line and must not be able to drive the terminal."""
        return "".join(c for c in str(text) if c.isprintable())

    # ANSI helpers
    def rgb_fg(r, g, b): return f"\033[38;2;{r};{g};{b}m"

    def hexc(h):
        return rgb_fg(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    RST = "\033[0m"

    # Read from the palette rather than hardcoding: copied constants went stale
    # the moment the ground changed, and five of six no longer matched.
    FALLBACK = {"1": "#e5806b", "2": "#92bc84", "3": "#e0a049",
                "5": "#c394b2", "6": "#88c5c5", "8": "#8a7f75"}
    try:
        with open(os.path.expanduser("~/.config/umber/palette.json")) as fh:
            slots = json.load(fh)["dark"]
    except Exception:
        slots = {}
    if not isinstance(slots, dict):
        slots = {}          # "dark" holding a scalar would raise inside slot()

    def slot(n):
        """Per-slot validation: a palette that parses can still hold a value
        that is not a 6-digit hex, and one bad slot must not take the line."""
        v = slots.get(n)
        return v if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) else FALLBACK[n]

    TEAL, MAUVE, DIM = hexc(slot("6")[1:]), hexc(slot("5")[1:]), hexc(slot("8")[1:])
    # success -> warn -> alarm, the palette's own semantic ramp
    RAMP = tuple(tuple(int(slot(n)[i:i + 2], 16) for i in (1, 3, 5)) for n in ("2", "3", "1"))

    def pct_to_rgb(pct):
        t = max(0.0, min(1.0, pct / 100)) * 2
        i = 0 if t <= 1 else 1
        t -= i
        a, b = RAMP[i], RAMP[i + 1]
        return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))

    # Git info
    git_branch = ""
    git_dirty = ""
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=2
        )
        if r.returncode == 0:
            git_branch = r.stdout.strip()
            d = subprocess.run(
                ["git", "-C", cwd, "--no-optional-locks", "diff-index", "--quiet", "HEAD", "--"],
                capture_output=True, timeout=2
            )
            if d.returncode != 0:
                git_dirty = "*"
    except Exception:
        pass

    # Session time from API
    session_time = ""
    elapsed = total_duration_ms // 1000
    if elapsed > 0:
        h, m = elapsed // 3600, (elapsed % 3600) // 60
        h, m = int(h), int(m)
        session_time = f"{h}h{m:02d}m" if h else f"{m}m"

    folder = clean(os.path.basename(cwd))
    gap = "  "

    parts = [f"{TEAL}{clean(model_label)}{RST}", f"{DIM}\uf07b{RST} {folder}"]
    if git_branch:
        parts.append(f"{MAUVE}\ue725 {clean(git_branch)}{git_dirty}{RST}")
    if used_pct is not None:
        parts.append(rgb_fg(*pct_to_rgb(used_pct)) + f"{used_pct}%" + RST)
    if session_time:
        parts.append(f"{DIM}{session_time}{RST}")

    print(gap.join(parts))

except Exception as e:
    # Fallback to minimal output on error (prevents blank status line)
    print(f"Claude | Error: {type(e).__name__}")
