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
    """2.0 "Rigi": a cog railway climbing the mountain at sunset, everything in peach fading into the dark.
    No logo, no text – the wallpaper should still disappear behind windows (calm, low contrast, empty sky).
    Night (default): the glow of the sun behind the Rigi in Catppuccin Peach, the sky and slopes fade to Crust.
    Day (day=True): the same scene in light peach (simpleos-wallpaper-schedule switches).
    Deterministic (no random numbers), so every build delivers the same picture and day/night show the same scene."""
    import math

    ss = 2  # supersampling for smooth edges
    w, h = size[0] * ss, size[1] * ss

    if day:
        top, glow = lerp(WHITE, PEACH, 0.22), lerp(WHITE, PEACH, 0.70)
        far, near = lerp(WHITE, PEACH, 0.55), lerp(PEACH, (0x5A, 0x34, 0x2C), 0.78)
        rim, light = WHITE, WHITE
        ink = (0x3E, 0x24, 0x22)
    else:
        top, glow = CRUST, lerp(CRUST, PEACH, 0.92)
        far, near = lerp(CRUST, PEACH, 0.42), lerp(CRUST, PEACH, 0.025)
        rim, light = PEACH, lerp(PEACH, WHITE, 0.25)
        ink = CRUST

    img = gradient((w, h), top, glow, horizontal=False).convert("RGBA")
    # Sun: a soft glow low over the horizon, right of the middle
    sun = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy, rad = round(w * 0.86), round(h * 0.50), round(h * 0.085)
    ImageDraw.Draw(sun).ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=lerp(glow, WHITE, 0.45) + (230,))
    img = Image.alpha_composite(img, sun.filter(ImageFilter.GaussianBlur(rad * 0.9)))
    img = Image.alpha_composite(img, sun.filter(ImageFilter.GaussianBlur(rad * 3.2)))

    def smooth(x, freq, phase):
        return math.sin(math.tau * freq * x + phase)

    def ridge(x, base, peak_x, peak_h, width, wob):
        """Mountain profile (y in pixels): a broad peak at peak_x plus calm waves."""
        bump = math.exp(-(((x - peak_x) / width) ** 2))
        waves = 0.55 * smooth(x, 1.3, 0.7) + 0.30 * smooth(x, 3.1, 2.0) + 0.15 * smooth(x, 6.7, 4.1)
        return (base - peak_h * bump + wob * waves) * h

    def draw_layer(img, fn, color, rim_alpha, rim_color):
        pts = [(i, fn(i / w)) for i in range(0, w + 6, 6)]
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(pts + [(w, h), (0, h)], fill=color + (255,))
        img = Image.alpha_composite(img, layer)
        if rim_alpha:
            edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(edge).line(pts, fill=rim_color + (round(255 * rim_alpha),), width=2 * ss)
            img = Image.alpha_composite(img, edge.filter(ImageFilter.GaussianBlur(ss * 0.8)))
        return img

    # Back to front: far range (hazy), the Rigi itself, a dark foreground hill
    img = draw_layer(img, lambda x: ridge(x, 0.70, 0.18, 0.20, 0.20, 0.030), far, 0.30, rim)
    rigi = lambda x: ridge(x, 0.80, 0.60, 0.40, 0.27, 0.014)
    img = draw_layer(img, rigi, lerp(far, near, 0.80), 0.75, rim)

    # Cog railway: climbs the left slope of the Rigi towards the summit (a path along the slope, a bit below the ridge)
    x0, x1 = 0.07, 0.575
    n = 400
    track = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        track.append((x * w, rigi(x) + h * (0.060 - 0.030 * t)))
    rail = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rail)
    for i in range(0, n, 3):  # sleepers
        (xa, ya), (xb, yb) = track[i], track[min(i + 1, n)]
        ang = math.atan2(yb - ya, xb - xa)
        nx, ny = -math.sin(ang), math.cos(ang)
        rd.line((xa - nx * 3 * ss, ya - ny * 3 * ss, xa + nx * 3 * ss, ya + ny * 3 * ss), fill=ink + (200,), width=ss)
    rd.line(track, fill=ink + (255,), width=2 * ss)
    rd.line([(x, y - 2 * ss) for x, y in track], fill=rim + (130,), width=ss)
    img = Image.alpha_composite(img, rail)

    # Train: locomotive + two cars, lights in the windows, placed on the track and turned along the slope
    car_w, car_h, gap = 62 * ss, 24 * ss, 3 * ss
    train = Image.new("RGBA", (3 * car_w + 2 * gap + 20 * ss, car_h + 24 * ss), (0, 0, 0, 0))
    td = ImageDraw.Draw(train)
    for k in range(3):
        left = 10 * ss + k * (car_w + gap)
        td.rounded_rectangle((left, 8 * ss, left + car_w, 8 * ss + car_h), radius=5 * ss, fill=ink + (255,))
        td.line((left + 6 * ss, 10 * ss, left + car_w - 6 * ss, 10 * ss), fill=rim + (170,), width=ss)
        for j in range(5):
            wx = left + 6 * ss + j * (car_w - 12 * ss) / 5
            td.rounded_rectangle((wx, 8 * ss + 6 * ss, wx + 7 * ss, 8 * ss + 13 * ss), radius=ss, fill=light + (255,))
    glow_layer = train.filter(ImageFilter.GaussianBlur(3 * ss))
    ti = round(n * 0.60)
    (xa, ya), (xb, yb) = track[ti], track[ti + 1]
    ang = math.degrees(math.atan2(yb - ya, xb - xa))
    for layer_img, fx in ((glow_layer, 0.55), (train, 1.0)):
        rot = layer_img.rotate(-ang, resample=Image.BICUBIC, expand=True)
        if fx < 1:
            rot.putalpha(rot.getchannel("A").point(lambda a: round(a * fx)))
        # the middle of the train sits on the rail, its underside touches the track
        px = round(xa - rot.width / 2 - math.sin(math.radians(ang)) * car_h * 0.45)
        py = round(ya - rot.height / 2 - math.cos(math.radians(ang)) * car_h * 0.45)
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(rot, (px, py), rot)
        img = Image.alpha_composite(img, canvas)

    # Foreground: a dark hill with a thin edge of light
    img = draw_layer(img, lambda x: ridge(x, 0.93, 0.15, 0.05, 0.40, 0.018), lerp(near, ink, 0.55), 0.18, rim)

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
