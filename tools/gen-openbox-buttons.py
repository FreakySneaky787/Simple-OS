#!/usr/bin/python3
"""Simple OS – draw the Openbox window buttons (minimize, maximize, restore, close) as XBM masks (#121).

    ./tools/gen-openbox-buttons.py            write them into config/includes.chroot (run from the repository root)
    ./tools/gen-openbox-buttons.py --check    only compare: exit 1 if a file differs from what would be written
    ./tools/gen-openbox-buttons.py --show     print the shapes as text

Openbox draws the button images in the theme colors (window.*.button.*.image.color); without images of its own the
theme fell back to Openbox's built-in 6x6 bitmaps, which were tiny at every size. The images do not grow with the
display scale (#41) – Openbox only centers them in the button –, so there is one set per scale:
    100 %  config/includes.chroot/usr/share/themes/SimpleOS/openbox-3/          (the system theme itself)
    125/150/200 %  config/includes.chroot/usr/share/simpleos/openbox-buttons/<percent>/
simpleos-theme copies the matching set into the user's theme copy (~/.themes/SimpleOS/openbox-3).
Size: the glyph is 10 px at 100 % (the button is 18 px: title font height + the label's 2 px bevel margins − 2),
lines 2 px; both grow with the scale.
"""
import os
import sys

NAMES = ("iconify", "max", "max_toggled", "close")
SCALES = (100, 125, 150, 200)
BASE = 10        # glyph size at 100 %
LINE = 2         # line width at 100 %
ROOT = "config/includes.chroot"


def geometry(pct):
    return max(6, round(BASE * pct / 100)), max(1, round(LINE * pct / 100))


def draw(name, n, t):
    """n x n grid of 0/1."""
    g = [[0] * n for _ in range(n)]

    def rect(x0, y0, x1, y1):       # filled, inclusive
        for y in range(max(0, y0), min(n, y1 + 1)):
            for x in range(max(0, x0), min(n, x1 + 1)):
                g[y][x] = 1

    def frame(x0, y0, x1, y1, w):
        rect(x0, y0, x1, y0 + w - 1)
        rect(x0, y1 - w + 1, x1, y1)
        rect(x0, y0, x0 + w - 1, y1)
        rect(x1 - w + 1, y0, x1, y1)

    if name == "iconify":           # a line at the bottom
        rect(0, n - t, n - 1, n - 1)
    elif name == "max":             # a square
        frame(0, 0, n - 1, n - 1, t)
    elif name == "max_toggled":     # restore: two overlapping squares, the back one only where it shows
        off = max(2, round(n * 0.3))
        back = max(1, t - 1)            # the back square thinner, so it stays readable at 10 px
        frame(off, 0, n - 1, n - 1 - off, back)
        for y in range(off, n):     # clear what the front square covers
            for x in range(0, n - off):
                g[y][x] = 0
        frame(0, off, n - 1 - off, n - 1, t)
    elif name == "close":           # an x: both diagonals, t px wide
        for y in range(n):
            for x in range(n):
                if abs(x - y) * 2 < t + 0.5 or abs(x + y - (n - 1)) * 2 < t + 0.5:
                    g[y][x] = 1
    return g


def xbm(name, g):
    n = len(g)
    out = [f"#define {name}_width {n}", f"#define {name}_height {n}", f"static unsigned char {name}_bits[] = {{"]
    data = []
    for row in g:
        for i in range(0, n, 8):
            b = 0
            for bit, v in enumerate(row[i:i + 8]):
                b |= v << bit
            data.append(f"0x{b:02x}")
    lines = [", ".join(data[i:i + 12]) for i in range(0, len(data), 12)]
    out.append("   " + ",\n   ".join(lines) + " };")
    return "\n".join(out) + "\n"


def target(pct):
    if pct == 100:
        return os.path.join(ROOT, "usr/share/themes/SimpleOS/openbox-3")
    return os.path.join(ROOT, f"usr/share/simpleos/openbox-buttons/{pct}")


def main(argv):
    check, show = "--check" in argv, "--show" in argv
    if not os.path.isdir(ROOT):
        print("Run from the repository root.", file=sys.stderr)
        return 2
    differ = 0
    for pct in SCALES:
        n, t = geometry(pct)
        for name in NAMES:
            g = draw(name, n, t)
            if show:
                print(f"{name} {pct} % ({n} px, line {t})")
                print("\n".join("".join("#" if v else "." for v in row) for row in g) + "\n")
            path = os.path.join(target(pct), name + ".xbm")
            text = xbm(name, g)
            try:
                with open(path) as f:
                    same = f.read() == text
            except OSError:
                same = False
            if check:
                if not same:
                    print(f"differs: {path}", file=sys.stderr)
                    differ = 1
            elif not show and not same:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(text)
    return differ


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
