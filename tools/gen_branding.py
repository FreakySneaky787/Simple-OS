#!/usr/bin/env python3
"""Generates the Simple OS branding graphics (Catppuccin Mocha).

Brand: "SOS" (Simple Operating System), the "O" is a lifebuoy – a rescue from Big Tech – with the slogan
"Keep it Simple". A white ring with four stripes in Catppuccin Red (red and white, recognizable as a lifebuoy
even at 16 px), the two "S" in the Simple OS gradient blue -> pink. The logo (logo.png, icon.png) is the ring alone.

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
RED = (0xF3, 0x8B, 0xA8)          # Catppuccin Mocha Red: stripes of the lifebuoy
RING = (0xF5, 0xF6, 0xFA)         # base color of the ring (almost white)
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


def gradient_text(canvas, xy, text, font, start=BLUE, end=PINK, anchor="mm"):
    """Draws text with a horizontal blue->pink gradient."""
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    x0, _, x1, _ = mask.getbbox()
    grad = Image.new("RGB", canvas.size, start)
    grad.paste(gradient((x1 - x0, canvas.size[1]), start, end), (x0, 0))
    canvas.paste(grad, (0, 0), mask)


def make_lifebuoy(size):
    """Lifebuoy: white ring, four red stripes diagonally (45°, 135°, 225°, 315°), transparent hole.
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
    img.paste(gradient((w, h), BLUE, PINK).convert("RGBA"), (0, 0), mask)
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
    img.paste(gradient((w, bar), BLUE, PINK), (0, 0))
    img.paste(gradient((w, bar), BLUE, PINK), (0, h - bar))

    mark = make_wordmark(title_px * SS)
    img.alpha_composite(mark, ((w - mark.width) // 2, round(h * 0.40) - mark.height // 2))

    slogan_font = ImageFont.truetype(FONT_BOLD, round(title_px * 0.42) * SS)
    draw.text((w / 2, h * 0.70), SLOGAN, font=slogan_font, fill=TEXT, anchor="mm")
    sub_font = ImageFont.truetype(FONT, round(title_px * 0.26) * SS)
    draw.text((w / 2, h * 0.82), subtitle, font=sub_font, fill=SUBTEXT, anchor="mm")

    return img.convert("RGB").resize(size, Image.LANCZOS)


def make_wallpaper(size, day=False):
    """Minimal motif: layered dunes under a calm sky, a fine edge of light.
    No logo, no text, no color blobs – the wallpaper should disappear behind windows.
    Night (default): Catppuccin Mocha, edge of light in lavender. Day (day=True): the same dunes in Catppuccin
    Latte – a light sky with a hint of blue, a white edge of light (simpleos-wallpaper-schedule switches).
    Deterministic (fixed random seed), so every build delivers the same picture and day/night show the same
    landscape."""
    import math
    import random

    rnd = random.Random(1984)
    ss = 2  # supersampling for smooth edges
    w, h = size[0] * ss, size[1] * ss

    if day:
        # Sky: a light blue shimmer at the top, Latte Base towards the horizon
        sky = gradient((w, h), lerp(LATTE_BASE, LATTE_BLUE, 0.16), lerp(LATTE_BASE, LATTE_LAVENDER, 0.04),
                       horizontal=False)
        layers = [
            (0.58, lerp(LATTE_BASE, LATTE_SURFACE0, 0.45), 0.050, 0.55),
            (0.66, lerp(LATTE_SURFACE0, LATTE_BASE, 0.15), 0.060, 0.45),
            (0.75, LATTE_SURFACE1, 0.070, 0.35),
            (0.86, lerp(LATTE_SURFACE1, LATTE_SURFACE2, 0.6), 0.060, 0.25),
        ]
        rim_color = WHITE
    else:
        # Sky: Crust at the top, Base with a hint of lavender towards the horizon
        sky = gradient((w, h), CRUST, lerp(BASE, LAVENDER, 0.06), horizontal=False)
        # Dunes from back to front: lighter at the back (haze), darker at the front
        layers = [
            (0.58, lerp(BASE, SURFACE, 0.55), 0.050, 0.22),
            (0.66, lerp(BASE, SURFACE, 0.30), 0.060, 0.18),
            (0.75, BASE, 0.070, 0.14),
            (0.86, lerp(MANTLE, CRUST, 0.5), 0.060, 0.10),
        ]
        rim_color = LAVENDER
    img = sky.convert("RGBA")

    for base_y, color, amp, rim in layers:
        waves = [(rnd.uniform(0.6, 1.6), rnd.uniform(0, math.tau), rnd.uniform(0.35, 1.0)) for _ in range(3)]
        norm = sum(a for _f, _p, a in waves)
        pts = []
        for i in range(0, w + 8, 8):
            x = i / w
            y = sum(a * math.sin(math.tau * f * x + p) for f, p, a in waves) / norm
            pts.append((i, (base_y + amp * y) * h))
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.polygon(pts + [(w, h), (0, h)], fill=color + (255,))
        # Edge of light: a thin line on the ridge, fading softly upwards
        edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(edge).line(pts, fill=rim_color + (round(255 * rim),), width=2 * ss)
        edge = edge.filter(ImageFilter.GaussianBlur(ss))
        img = Image.alpha_composite(img, layer)
        img = Image.alpha_composite(img, edge)

    img = img.convert("RGB").resize(size, Image.LANCZOS)
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
        make_banner((1280, 420), 110, "Simple Operating System · Debian 12 · Openbox").save(
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
