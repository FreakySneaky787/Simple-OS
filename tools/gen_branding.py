#!/usr/bin/env python3
"""Generates the Simple OS branding graphics (Catppuccin Mocha).

Brand: "SOS" (Simple Operating System), the "O" is a lifebuoy – a rescue from Big Tech – with the slogan
"Keep it Simple". A white ring with four stripes in Catppuccin Red (red and white, recognizable as a lifebuoy
even at 16 px), the two "S" in the Simple OS gradient peach -> pink. The logo (logo.png, icon.png) is the ring alone.

Usage: gen_branding.py <includes.chroot folder> [<bootloaders/isolinux folder>]
        gen_branding.py --readme docs     (only the README banner docs/sos-banner.png)
Generates in it:
  etc/calamares/branding/simpleos/{logo,icon,welcome,slide1}.png
  usr/share/simpleos/logo.png
  usr/share/backgrounds/simpleos/wallpaper.png (2560x1440)
  usr/share/plymouth/themes/spinner/watermark.png
and in the second folder the ISO's boot menu image (instead of live-build's Debian helmet with "Debian GNU/Linux"):
  splash.png (640x480, isolinux/BIOS) and splash800x600.png (GRUB/UEFI uses it as long as it has no own image)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = (0x1E, 0x1E, 0x2E)
MANTLE = (0x18, 0x18, 0x25)
SURFACE = (0x31, 0x32, 0x44)
BLUE = (0x89, 0xB4, 0xFA)
PINK = (0xF5, 0xC2, 0xE7)
SUBTEXT = (0xA6, 0xAD, 0xC8)
CRUST = (0x11, 0x11, 0x1B)
MAUVE = (0xCB, 0xA6, 0xF7)
PEACH = (0xFA, 0xB3, 0x87)        # Catppuccin Mocha Peach: accent of 2.0 "Rigi", wallpaper
LAVENDER = (0xB4, 0xBE, 0xFE)
# Catppuccin Latte (light counterpart of Mocha) for the day wallpaper
LATTE_CRUST = (0xDC, 0xE0, 0xE8)
LATTE_BASE = (0xEF, 0xF1, 0xF5)
LATTE_SURFACE0 = (0xCC, 0xD0, 0xDA)
LATTE_SURFACE1 = (0xBC, 0xC0, 0xCC)
LATTE_SURFACE2 = (0xAC, 0xB0, 0xBE)
LATTE_BLUE = (0x1E, 0x66, 0xF5)
LATTE_LAVENDER = (0x72, 0x87, 0xFD)
WHITE = (0xFF, 0xFF, 0xFF)
RED = (0xFE, 0x64, 0x0B)          # Catppuccin Latte Peach: stripes of the lifebuoy (2.0 "Rigi")
CREAM = (0xF5, 0xE0, 0xDC)        # Catppuccin Mocha Rosewater: end of the S gradient and the ring
RING = CREAM                      # base color of the ring (warm cream)
TEXT = (0xCD, 0xD6, 0xF4)
SLOGAN = "Keep it Simple"
VERSION = ""  # from usr/lib/os-release (main)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SS = 4  # supersampling factor for smooth edges


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def gradient(size, start, end, horizontal=True):
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    steps = w if horizontal else h
    for i in range(steps):
        c = lerp(start, end, i / max(steps - 1, 1))
        if horizontal:
            draw.line([(i, 0), (i, h)], fill=c)
        else:
            draw.line([(0, i), (w, i)], fill=c)
    return img


def gradient_text(canvas, xy, text, font, start=PEACH, end=CREAM, anchor="mm"):
    """Draws text with a horizontal peach->cream gradient."""
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    x0, _, x1, _ = mask.getbbox()
    grad = Image.new("RGB", canvas.size, start)
    grad.paste(gradient((x1 - x0, canvas.size[1]), start, end), (x0, 0))
    canvas.paste(grad, (0, 0), mask)


def make_lifebuoy(size):
    """Lifebuoy: cream ring, four orange stripes diagonally (45°, 135°, 225°, 315°), transparent hole.
    From 40 px and smaller the ring is thicker so the stripes stay visible (taskbar, icons)."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    c = s / 2
    hole = c * (0.50 if size > 40 else 0.40)
    ring = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(ring)
    d.ellipse([0, 0, s - 1, s - 1], fill=255)
    d.ellipse([c - hole, c - hole, c + hole, c + hole], fill=0)
    img.paste(Image.new("RGBA", (s, s), RING + (255,)), (0, 0), ring)
    stripes = Image.new("L", (s, s), 0)
    sd = ImageDraw.Draw(stripes)
    for mid in (45, 135, 225, 315):
        sd.pieslice([0, 0, s - 1, s - 1], mid - 25, mid + 25, fill=255)
    stripes = Image.composite(stripes, Image.new("L", (s, s), 0), ring)
    img.paste(Image.new("RGBA", (s, s), RED + (255,)), (0, 0), stripes)
    return img.resize((size, size), Image.LANCZOS)


def make_logo(size):
    """Logo = lifebuoy (Calamares, Setup Wizard, Welcome page)."""
    return make_lifebuoy(size)


def make_wordmark(cap_px):
    """Wordmark "S [ring] S", transparent, cropped to its content. cap_px = height of the capital letters;
    the ring is 10 % larger (overshoot like a real "O")."""
    font = ImageFont.truetype(FONT_BOLD, 100 * SS)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    l0, t0, r0, b0 = probe.textbbox((0, 0), "S", font=font, anchor="ls")
    fsize = round(100 * SS * cap_px * SS / (b0 - t0))          # font size for the desired height
    font = ImageFont.truetype(FONT_BOLD, fsize)
    l, t, r, b = probe.textbbox((0, 0), "S", font=font, anchor="ls")
    cap, sw = b - t, r - l
    ring_d = round(cap * 1.10)
    gap = round(fsize * 0.06)
    w, h = sw * 2 + ring_d + gap * 2 + 4 * SS, ring_d + 4 * SS
    base_y = (h + cap) // 2
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.text((2 * SS - l, base_y), "S", font=font, fill=255, anchor="ls")
    x_ring = 2 * SS + sw + gap
    md.text((x_ring + ring_d + gap - l, base_y), "S", font=font, fill=255, anchor="ls")
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(gradient((w, h), PEACH, CREAM).convert("RGBA"), (0, 0), mask)
    buoy = make_lifebuoy(ring_d // SS).resize((ring_d, ring_d), Image.LANCZOS)
    img.alpha_composite(buoy, (x_ring, base_y - cap // 2 - ring_d // 2))
    img = img.crop(img.getbbox())
    return img.resize((max(1, img.width // SS), max(1, img.height // SS)), Image.LANCZOS)


def make_banner(size, title_px, subtitle):
    """Calamares welcome image/slide: SOS wordmark, below it "Keep it Simple" and a quiet line."""
    w, h = size[0] * SS, size[1] * SS
    img = gradient((w, h), BASE, MANTLE, horizontal=False).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Subtle accent lines at the top/bottom in the gradient
    bar = round(h * 0.012)
    img.paste(gradient((w, bar), PEACH, CREAM), (0, 0))
    img.paste(gradient((w, bar), PEACH, CREAM), (0, h - bar))

    mark = make_wordmark(title_px * SS)
    img.alpha_composite(mark, ((w - mark.width) // 2, round(h * 0.40) - mark.height // 2))

    slogan_font = ImageFont.truetype(FONT_BOLD, round(title_px * 0.42) * SS)
    draw.text((w / 2, h * 0.70), SLOGAN, font=slogan_font, fill=TEXT, anchor="mm")
    sub_font = ImageFont.truetype(FONT, round(title_px * 0.26) * SS)
    draw.text((w / 2, h * 0.82), subtitle, font=sub_font, fill=SUBTEXT, anchor="mm")

    return img.convert("RGB").resize(size, Image.LANCZOS)


def make_wallpaper(size, day=False):
    """2.0 "Rigi": the evening view from a station on the Rigi. The sun sinks into the long chain of the Alps next to a
    massif with a jagged crown, the lake lies far below with the sun's path on the water, a meadow with firs comes down
    to the station, and a cog railway train comes in under its overhead line on its trackbed. Flat shapes, everything in
    Catppuccin Peach fading into the dark. No logo, no text; the upper left (desktop icons) stays calm sky.
    Night (default): peach into Crust. Day (day=True): the same scene in light peach (simpleos-wallpaper-schedule
    switches). Deterministic (fixed seeds): every build gives the same picture."""
    import math
    import random

    ss = 2  # supersampling for smooth edges
    W, H = size[0] * ss, size[1] * ss

    def X(x):
        return x * W

    def Y(y):
        return y * H

    if day:
        top, mid, glow, ink = lerp(WHITE, PEACH, 0.18), lerp(WHITE, PEACH, 0.42), lerp(WHITE, PEACH, 0.68), (0x5E, 0x38, 0x30)
        sun_c, ray_a, lamp = WHITE, 34, lerp(WHITE, PEACH, 0.15)
        ray_c = halo = WHITE
    else:
        top, mid, glow, ink = CRUST, lerp(CRUST, PEACH, 0.40), lerp(PEACH, WHITE, 0.10), CRUST
        sun_c, ray_a, lamp = lerp(PEACH, WHITE, 0.85), 18, lerp(PEACH, WHITE, 0.75)
        ray_c = lerp(glow, WHITE, 0.4)
        halo = lerp(glow, WHITE, 0.35)

    def shade(t):
        return lerp(glow, ink, t)

    # ---- Sky: dark at the top, glowing peach towards the horizon ----
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    stops = [(0.0, top), (0.30, mid), (0.50, glow), (1.0, glow)]
    for y in range(H):
        f = y / H
        for (fa, ca), (fb, cb) in zip(stops, stops[1:]):
            if fa <= f <= fb:
                d.line([(0, y), (W, y)], fill=lerp(ca, cb, (f - fa) / (fb - fa)))
                break

    def soft(draw_fn, blur, tint):
        """Soft light (glow, rays, haze): drawn at a quarter of the size, blurred, scaled up. The transparent pixels
        carry the light's own color, so blurring does not mix black into the edges (grey streaks in the day sky)."""
        k = 0.25
        small = Image.new("RGBA", (round(W * k), round(H * k)), tint + (0,))
        draw_fn(ImageDraw.Draw(small), k)
        small = small.filter(ImageFilter.GaussianBlur(blur * k * size[0] / 1280))  # blur grows with the picture
        return small.resize((W, H), Image.BILINEAR)

    def paste_soft(img, layer):
        return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    # ---- Sun with rays, sinking behind the shoulder of the big peak ----
    sx, sy = 0.425, 0.49

    def rays(dd, k):
        for i in range(16):
            ang = math.radians(-180 + i * 360 / 16 + 6)
            half = math.radians(1.6)
            p = [(X(sx) * k, Y(sy) * k)]
            for a2 in (ang - half, ang + half):
                p.append(((X(sx) + math.cos(a2) * W) * k, (Y(sy) + math.sin(a2) * W) * k))
            dd.polygon(p, fill=ray_c + (ray_a,))

    def sun_glow(dd, k):
        for r, a_ in ((0.42, 70), (0.20, 110), (0.08, 190)):
            rr = Y(r) * k
            dd.ellipse((X(sx) * k - rr, Y(sy) * k - rr, X(sx) * k + rr, Y(sy) * k + rr), fill=halo + (a_,))

    img = paste_soft(img, soft(rays, 10 * ss, ray_c))
    img = paste_soft(img, soft(sun_glow, 60 * ss, halo))
    d = ImageDraw.Draw(img, "RGBA")
    r = Y(0.03)
    d.ellipse((X(sx) - r, Y(sy) - r, X(sx) + r, Y(sy) + r), fill=sun_c)

    # ---- Mountains: jagged alpine ridges, lighter (more haze) the further away ----
    def ridge(seed, base, rough, peaks=(), levels=8):
        rnd = random.Random(seed)
        n = 2 ** levels
        pts = [0.0] * (n + 1)
        pts[0], pts[n] = rnd.uniform(-1, 1) * rough, rnd.uniform(-1, 1) * rough
        step, amp = n, rough
        while step > 1:
            half = step // 2
            for i in range(half, n, step):
                pts[i] = (pts[i - half] + pts[i + half]) / 2 + rnd.uniform(-1, 1) * amp
            step, amp = half, amp * 0.55

        def y_at(x):
            f = min(max(x, 0.0), 1.0) * n
            i = min(int(f), n - 1)
            t = f - i
            y = pts[i] * (1 - t) + pts[i + 1] * t
            # triangular peaks look alpine; the highest one wins where they overlap (a crown, not a spike)
            y -= max([ph * max(0.0, 1 - abs(x - px) / pw) for px, ph, pw in peaks] or [0.0])
            return base + y
        return y_at

    def mountain(img, fn, color, rim=0.0):
        pts = [(x, Y(fn(x / W))) for x in range(0, W + 4, 4)]
        d = ImageDraw.Draw(img, "RGBA")
        d.polygon(pts + [(W, H), (0, H)], fill=color)
        if rim:
            # edge of light, strongest close to the sun
            light = lerp(glow, WHITE, 0.45)
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                a_ = rim * max(0.0, 1 - abs(x0 / W - sx) / 0.45)
                if a_ > 0.02:
                    d.line([(x0, y0), (x1, y1)], fill=light + (round(255 * a_),), width=2 * ss)
        return img

    # The view from the Rigi: the Alps as a long serrated chain on the horizon, their edges lit like snow
    rnd = random.Random(5)
    alps = [(0.02 + i * 0.062 + rnd.uniform(-0.015, 0.015), rnd.uniform(0.018, 0.042), rnd.uniform(0.02, 0.035))
            for i in range(17)]
    img = mountain(img, ridge(3, 0.505, 0.014, alps, levels=9), shade(0.14), 0.55)
    # a massif next to the sun with a jagged crown of rock teeth (like the Pilatus seen from the Rigi)
    img = mountain(img, ridge(7, 0.60, 0.008, [(0.385, 0.07, 0.09), (0.51, 0.11, 0.17), (0.465, 0.125, 0.07),
                                                (0.505, 0.140, 0.06), (0.54, 0.132, 0.055), (0.575, 0.125, 0.07)],
                              levels=9), shade(0.30), 0.85)
    # low hills on the far shore
    img = mountain(img, ridge(11, 0.585, 0.012, [(0.08, 0.04, 0.12), (0.25, 0.025, 0.08), (0.80, 0.035, 0.12),
                                                  (0.95, 0.03, 0.08)]), shade(0.42), 0.30)

    # The lake far below (Lake Lucerne lies right under the Rigi): water reflecting the evening sky
    lake_y = 0.588
    d = ImageDraw.Draw(img)
    water_top, water_low = lerp(glow, WHITE, 0.10), lerp(glow, ink, 0.40)
    y0, y1 = round(Y(lake_y)), round(Y(0.80))
    for y in range(y0, y1):
        d.line([(0, y), (W, y)], fill=lerp(water_top, water_low, (y - y0) / (y1 - y0)))

    def sun_path(dd, k):  # the sun's path on the water
        dd.ellipse((X(sx - 0.018) * k, Y(lake_y) * k, X(sx + 0.018) * k, Y(0.78) * k), fill=sun_c + (150,))
    img = paste_soft(img, soft(sun_path, 10 * ss, sun_c))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(9):  # glitter
        gy = lake_y + 0.006 + 0.0035 * i ** 1.5
        gw = 0.010 + 0.004 * i
        d.line([(X(sx - gw), Y(gy)), (X(sx + gw), Y(gy))], fill=sun_c + (110,), width=ss)

    def fog(dd, k):  # evening haze lying on the water
        dd.rectangle((0, Y(lake_y - 0.012) * k, W * k, Y(lake_y + 0.018) * k), fill=lerp(glow, WHITE, 0.3) + (90,))
    img = paste_soft(img, soft(fog, 30 * ss, lerp(glow, WHITE, 0.3)))

    # near shore: a tongue of land from the left and hills on the right, framing the lake
    def shore(x):
        if x <= 0.36:
            return 0.615 + 0.12 * (x / 0.36) ** 2
        if x < 0.40:
            return 0.735 + (x - 0.36) / 0.04 * 0.30
        if x < 0.66:
            return 1.05
        if x < 0.72:
            return 1.05 - (x - 0.66) / 0.06 * 0.39
        return 0.66 - 0.02 * (x - 0.72) / 0.28
    img = mountain(img, shore, shade(0.58), 0.25)

    # Foreground: the Rigi itself – a meadow coming down from the left to the plateau of the station
    hill_noise = ridge(23, 0.0, 0.006)

    def ground(x):
        if x <= 0.45:
            return 0.665 + 0.12 * (x / 0.45) ** 1.6 + hill_noise(x) * (1 - x / 0.45)
        return 0.785 - 0.010 * (x - 0.45) / 0.55
    img = mountain(img, ground, shade(0.84), 0.30)
    d = ImageDraw.Draw(img, "RGBA")
    tree = shade(0.92)
    for tx, th in ((0.05, 0.030), (0.075, 0.042), (0.10, 0.026), (0.19, 0.034), (0.215, 0.046), (0.24, 0.028),
                   (0.33, 0.032), (0.355, 0.040)):
        base = Y(ground(tx)) + 2 * ss
        for k_, (wf, hf) in enumerate(((0.55, 1.0), (0.45, 0.72), (0.34, 0.45))):  # three tiers of a fir
            half = Y(th) * wf * 0.5
            top = base - Y(th) * hf
            bottom = base - Y(th) * (hf - 0.45) if k_ else base
            d.polygon([(X(tx) - half, bottom), (X(tx), top), (X(tx) + half, bottom)], fill=tree)

    # ---- The cog railway: front facing the viewer, the body going away to the right ----
    fx0, fx1, fy0, fy1 = 0.615, 0.695, 0.585, 0.790
    fw, fh = fx1 - fx0, fy1 - fy0
    vp = (1.22, 0.665)  # vanishing point of the train body

    def toward(p, t):
        return (p[0] + (vp[0] - p[0]) * t, p[1] + (vp[1] - p[1]) * t)
    tf = (1.03 - fx1) / (vp[0] - fx1)

    def side(u, v):
        t = tf * u ** 0.8  # near windows wider than far ones
        a_, b_ = toward((fx1, fy0), t), toward((fx1, fy1), t)
        return (X(a_[0] + (b_[0] - a_[0]) * v), Y(a_[1] + (b_[1] - a_[1]) * v))

    # track: ballast, sleepers, two rails and the rack in the middle, catching the light towards the viewer
    l0, l1 = (fx0 + 0.10 * fw, fy1), (0.42, 1.01)
    r0, r1 = (fx1 - 0.10 * fw, fy1), (0.85, 1.01)
    c0, c1 = ((l0[0] + r0[0]) / 2, fy1), ((l1[0] + r1[0]) / 2, 1.01)

    def P(p0, p1, t):
        return (X(p0[0] + (p1[0] - p0[0]) * t), Y(p0[1] + (p1[1] - p0[1]) * t))
    d.polygon([P(l0, l1, 0), P(r0, r1, 0), (X(r1[0] + 0.06), H), (X(l1[0] - 0.06), H)], fill=shade(0.92))
    for i in range(1, 15):
        t = (i / 14) ** 1.7
        d.line([P(l0, l1, t), P(r0, r1, t)], fill=lerp(shade(0.92), glow, 0.12), width=max(1, round((1 + 9 * t) * ss)))
    rail = lerp(glow, WHITE, 0.25)
    for a_, b_, w_ in ((l0, l1, 1.0), (r0, r1, 1.0), (c0, c1, 0.7)):
        for i in range(24):
            t0, t1 = i / 24, (i + 1) / 24
            d.line([P(a_, b_, t0), P(a_, b_, t1)], fill=rail + (round(120 + 120 * t1),),
                   width=max(1, round((1 + 5 * t1) * w_ * ss)))

    # along the body: trackbed with rails, the platform in front of it, everything in perspective
    d.polygon([side(0, 1.0), side(1, 1.0), side(1, 1.13), side(0, 1.13)], fill=shade(0.92))
    for v_ in (1.035, 1.10):
        d.line([side(0, v_), side(1, v_)], fill=rail + (150,), width=ss)
    d.polygon([side(0, 1.13), side(1, 1.13), (W, H), (X(0.90), H)], fill=shade(0.78))
    d.line([side(0, 1.13), side(1, 1.13)], fill=lerp(glow, WHITE, 0.2) + (150,), width=2 * ss)
    d.line([side(0, 1.13), (X(0.90), H)], fill=lerp(glow, WHITE, 0.2) + (130,), width=3 * ss)

    # far mast behind the train
    mast = shade(0.95)
    d.line([(X(0.865), Y(0.70)), (X(0.865), Y(0.505))], fill=mast, width=4 * ss)
    d.line([(X(0.865), Y(0.525)), (X(0.80), Y(0.525))], fill=mast, width=3 * ss)

    # body side (away from the sun: darker), with a band of windows reflecting the sky
    body_hi, body_lo = lerp(PEACH, ink, 0.52), lerp(ink, glow, 0.07)
    d.polygon([side(0, 0), side(1, 0), side(1, 0.55), side(0, 0.55)], fill=body_hi)
    d.polygon([side(0, 0.55), side(1, 0.55), side(1, 1), side(0, 1)], fill=body_lo)
    win = lerp(glow, ink, 0.30)
    for k_ in range(7):
        a_, b_ = 0.04 + k_ * 0.137, 0.04 + k_ * 0.137 + 0.105
        d.polygon([side(a_, 0.14), side(b_, 0.14), side(b_, 0.44), side(a_, 0.44)], fill=win + (230,))
    d.line([side(0.60, 0), side(0.60, 1)], fill=lerp(body_lo, ink, 0.6), width=2 * ss)  # gap between the cars
    under = lerp(ink, glow, 0.03)
    d.polygon([side(0, 0.94), side(1, 0.94), side(1, 1.0), side(0, 1.0)], fill=under)
    for a_, b_ in ((0.05, 0.20), (0.42, 0.55), (0.66, 0.78), (0.90, 0.98)):  # bogies with their wheels
        d.polygon([side(a_, 0.93), side(b_, 0.93), side(b_, 1.045), side(a_, 1.045)], fill=under)
    d.line([side(0, 0), side(1, 0)], fill=lerp(glow, WHITE, 0.2) + (140,), width=2 * ss)  # roof edge

    # front: peach livery on top fading into the dark, two windscreens, three lamps
    front_hi, front_lo = lerp(PEACH, ink, 0.28), lerp(ink, glow, 0.12)
    rad = round(X(0.010))
    d.rounded_rectangle((X(fx0), Y(fy0), X(fx1), Y(fy1)), radius=rad, fill=front_hi)
    steps = 60
    for i in range(steps):  # soft fade from the livery into the dark lower half
        t = i / (steps - 1)
        y0 = Y(fy0 + fh * (0.45 + 0.30 * t))
        d.rectangle((X(fx0), y0, X(fx1), Y(fy1)), fill=lerp(front_hi, front_lo, t) + (40,))
    d.rectangle((X(fx0), Y(fy0 + fh * 0.75), X(fx1), Y(fy1)), fill=front_lo)
    for wx0, wx1 in ((0.08, 0.47), (0.53, 0.92)):
        d.rounded_rectangle((X(fx0 + fw * wx0), Y(fy0 + fh * 0.10), X(fx0 + fw * wx1), Y(fy0 + fh * 0.40)),
                            radius=round(X(0.003)), fill=lerp(glow, ink, 0.18))
        # reflection of the sunset
        d.polygon([(X(fx0 + fw * wx0), Y(fy0 + fh * 0.30)), (X(fx0 + fw * (wx0 + 0.16)), Y(fy0 + fh * 0.10)),
                   (X(fx0 + fw * (wx0 + 0.24)), Y(fy0 + fh * 0.10)), (X(fx0 + fw * wx0), Y(fy0 + fh * 0.37))],
                  fill=lerp(glow, WHITE, 0.4) + (110,))
    d.line([(X(fx0) + rad, Y(fy0)), (X(fx1) - rad, Y(fy0))], fill=lerp(glow, WHITE, 0.3) + (200,), width=2 * ss)
    d.line([(X(fx0), Y(fy0) + rad), (X(fx0), Y(fy1))], fill=lerp(glow, WHITE, 0.3) + (170,), width=2 * ss)
    d.rectangle((X(fx0 - 0.004), Y(fy1 - fh * 0.06), X(fx1 + 0.004), Y(fy1)), fill=lerp(ink, glow, 0.04))
    d.rectangle((X(fx0 + 0.12 * fw), Y(fy1), X(fx1 - 0.12 * fw), Y(fy1 + 0.012)), fill=lerp(ink, glow, 0.03))
    lamps = [(fx0 + fw * 0.20, fy0 + fh * 0.80, 0.045), (fx1 - fw * 0.20, fy0 + fh * 0.80, 0.045),
             (fx0 + fw * 0.50, fy0 + fh * 0.05, 0.030)]
    for lx, ly, lr in lamps:
        rr = X(fw * lr)
        d.ellipse((X(lx) - rr, Y(ly) - rr, X(lx) + rr, Y(ly) + rr), fill=lamp)

    def lamp_glow(dd, k):
        for lx, ly, lr in lamps:
            rr = X(fw * lr) * 4 * k
            dd.ellipse((X(lx) * k - rr, Y(ly) * k - rr, X(lx) * k + rr, Y(ly) * k + rr), fill=lamp + (80,))
    if not day:  # in daylight the lamps do not glow
        img = paste_soft(img, soft(lamp_glow, 10 * ss, lamp))
    d = ImageDraw.Draw(img, "RGBA")

    # pantograph and overhead line
    wire = shade(0.97) + (210,)

    def wire_y(x, y_left, y_mast, y_right):
        return y_left + (y_mast - y_left) * x / 0.70 if x <= 0.70 else y_mast + (y_right - y_mast) * (x - 0.70) / 0.30
    px_, py_ = side(0.10, 0)
    top_y = Y(wire_y(px_ / W, 0.255, 0.546, 0.600))
    d.line([(px_, py_), (px_ - X(0.010), (py_ + top_y) / 2), (px_, top_y)], fill=wire, width=2 * ss)
    d.line([(px_ - X(0.012), top_y), (px_ + X(0.012), top_y)], fill=wire, width=2 * ss)
    d.line([(0, Y(0.255)), (X(0.70), Y(0.546)), (X(1.0), Y(0.600))], fill=wire, width=2 * ss)
    d.line([(0, Y(0.200)), (X(0.70), Y(0.505)), (X(1.0), Y(0.575))], fill=shade(0.97) + (150,), width=ss)

    # near mast on the left of the track, lit from the sun side
    d.line([(X(0.578), Y(0.86)), (X(0.578), Y(0.47))], fill=mast, width=6 * ss)
    d.line([(X(0.578) - 2 * ss, Y(0.86)), (X(0.578) - 2 * ss, Y(0.47))], fill=lerp(glow, WHITE, 0.3) + (90,),
           width=ss)
    d.line([(X(0.578), Y(0.500)), (X(0.712), Y(0.500))], fill=mast, width=4 * ss)
    d.line([(X(0.578), Y(0.475)), (X(0.712), Y(0.500))], fill=mast, width=2 * ss)

    img = img.resize(size, Image.LANCZOS)
    # Fine grain against color banding in the dark gradients
    noise = Image.effect_noise(size, 18).convert("RGB")
    return Image.blend(img, noise, 0.018)


def make_watermark(scale=1.0):
    """SOS wordmark (Plymouth spinner, boot menu) with a transparent background."""
    return make_wordmark(round(58 * scale))


def make_boot_splash(size, logo_y):
    """Background of the boot menus: dark gradient, logo + wordmark at the top (center at logo_y, share of the height).
    Everything below stays free – GRUB draws its menu from 52 % of the height, isolinux from about 40 %."""
    w, h = size
    img = gradient(size, CRUST, BASE, horizontal=False)
    mark = make_watermark(scale=w / 800)
    img.paste(mark, ((w - mark.width) // 2, round(h * logo_y) - mark.height // 2), mark)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, max(11, round(14 * w / 800)))
    draw.text((w / 2, round(h * logo_y) + mark.height // 2 + round(18 * w / 800)), f"{SLOGAN} · Version {VERSION}",
              font=font, fill=SUBTEXT, anchor="mt")
    # vesamenu (isolinux) and GRUB only read simple PNGs: RGB, 8 bit, without interlacing
    return img.convert("RGB")


def main():
    # README banner for the repository (docs/sos-banner.png): gen_branding.py --readme docs
    if len(sys.argv) > 2 and sys.argv[1] == "--readme":
        out = Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        make_banner((1280, 420), 110, "Simple Operating System · Debian 13 · Openbox").save(
            out / "sos-banner.png", optimize=True)
        return

    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    # The version is set in ONE place: usr/lib/os-release (VERSION_ID, also the version of the package "simpleos")
    global VERSION
    for line in (root / "usr/lib/os-release").read_text().splitlines():
        if line.startswith("VERSION_ID="):
            VERSION = line.split("=", 1)[1].strip('"')

    cala = root / "etc/calamares/branding/simpleos"
    cala.mkdir(parents=True, exist_ok=True)
    make_logo(256).save(cala / "logo.png")
    make_logo(64).save(cala / "icon.png")
    make_banner((600, 350), 72, "Simple Operating System").save(cala / "welcome.png")
    make_banner((800, 480), 96, f"Simple Operating System · Version {VERSION}").save(cala / "slide1.png")

    # Logo for the Setup Wizard (the Calamares branding is removed after the installation)
    share = root / "usr/share/simpleos"
    share.mkdir(parents=True, exist_ok=True)
    make_logo(256).save(share / "logo.png")

    bg = root / "usr/share/backgrounds/simpleos"
    bg.mkdir(parents=True, exist_ok=True)
    make_wallpaper((2560, 1440)).save(bg / "wallpaper.png", optimize=True)
    # Day variant for simpleos-wallpaper-schedule (dynamic wallpaper: light during the day, dark in the evening/night light)
    make_wallpaper((2560, 1440), day=True).save(bg / "wallpaper-day.png", optimize=True)

    ply = root / "usr/share/plymouth/themes/spinner"
    ply.mkdir(parents=True, exist_ok=True)
    make_watermark().save(ply / "watermark.png")

    if len(sys.argv) > 2:
        boot = Path(sys.argv[2])
        boot.mkdir(parents=True, exist_ok=True)
        make_boot_splash((640, 480), 0.20).save(boot / "splash.png")
        make_boot_splash((800, 600), 0.27).save(boot / "splash800x600.png")


if __name__ == "__main__":
    main()
