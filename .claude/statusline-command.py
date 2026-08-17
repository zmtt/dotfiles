#!/usr/bin/env python3
import json, subprocess, sys, os

try:
    data = json.load(sys.stdin)

    cwd = data.get("workspace", {}).get("current_dir", os.getcwd())
    ctx = data.get("context_window", {})
    used_pct = ctx.get("used_percentage")  # Can be null early in session

    model_obj = data.get("model", {})
    model_label = model_obj.get("display_name", "Claude")

    total_duration_ms = (data.get("cost") or {}).get("total_duration_ms", 0) or 0

    # ANSI helpers
    def rgb_fg(r, g, b): return f"\033[38;2;{r};{g};{b}m"

    def hexc(h):
        return rgb_fg(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    RST = "\033[0m"
    TEAL = hexc("71aeae")    # umber slot 6
    MAUVE = hexc("cf9fbe")   # slot 5
    DIM = hexc("8a7f75")     # slot 8

    # Slots 2, 3, 1: the palette's own success/warn/alarm ramp.
    RAMP = ((0x8e, 0xb7, 0x80), (0xd5, 0x96, 0x3e), (0xfb, 0x94, 0x7e))

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
        session_time = f"{h}h{m:02d}m" if h else f"{m}m"

    folder = os.path.basename(cwd)
    gap = "  "

    parts = [f"{TEAL}{model_label}{RST}", f"{DIM}\uf07b{RST} {folder}"]
    if git_branch:
        parts.append(f"{MAUVE}\ue725 {git_branch}{git_dirty}{RST}")
    if used_pct is not None:
        parts.append(rgb_fg(*pct_to_rgb(used_pct)) + f"{used_pct}%" + RST)
    if session_time:
        parts.append(f"{DIM}{session_time}{RST}")

    print(gap.join(parts))

except Exception as e:
    # Fallback to minimal output on error (prevents blank status line)
    print(f"Claude | Error: {type(e).__name__}")
