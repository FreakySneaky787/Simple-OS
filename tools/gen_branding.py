#!/usr/bin/env python3
"""Erzeugt die Simple-OS-Branding-Grafiken (Catppuccin Mocha).

Aufruf: gen_branding.py <includes.chroot-Ordner>
Erzeugt darin:
  etc/calamares/branding/simpleos/{logo,icon,welcome,slide1}.png
  usr/share/simpleos/logo.png
  usr/share/backgrounds/simpleos/wallpaper.png (2560x1440)
  usr/share/plymouth/themes/spinner/watermark.png
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
# Catppuccin Latte (helles Gegenstück zu Mocha) für das Tag-Wallpaper
LATTE_CRUST = (0xDC, 0xE0, 0xE8)
LATTE_BASE = (0xEF, 0xF1, 0xF5)
LATTE_SURFACE0 = (0xCC, 0xD0, 0xDA)
LATTE_SURFACE1 = (0xBC, 0xC0, 0xCC)
LATTE_SURFACE2 = (0xAC, 0xB0, 0xBE)
LATTE_BLUE = (0x1E, 0x66, 0xF5)
LATTE_LAVENDER = (0x72, 0x87, 0xFD)
WHITE = (0xFF, 0xFF, 0xFF)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SS = 4  # Supersampling-Faktor für glatte Kanten


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
    """Zeichnet Text mit horizontalem Blau->Pink-Verlauf."""
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    x0, _, x1, _ = mask.getbbox()
    grad = Image.new("RGB", canvas.size, start)
    grad.paste(gradient((x1 - x0, canvas.size[1]), start, end), (x0, 0))
    canvas.paste(grad, (0, 0), mask)


def make_logo(size):
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    # Verlaufsring (blau -> pink) als äußerer Kreis
    ring = gradient((s, s), BLUE, PINK).convert("RGBA")
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, s - 1, s - 1], fill=255)
    img.paste(ring, (0, 0), mask)

    # Dunkle Innenscheibe
    border = round(s * 0.045)
    ImageDraw.Draw(img).ellipse([border, border, s - 1 - border, s - 1 - border], fill=BASE)

    # Blaues "S"
    font = ImageFont.truetype(FONT_BOLD, round(s * 0.62))
    ImageDraw.Draw(img).text((s / 2, s / 2 + s * 0.02), "S", font=font, fill=BLUE, anchor="mm")

    return img.resize((size, size), Image.LANCZOS)


def make_banner(size, title_px, subtitle, logo_px):
    w, h = size[0] * SS, size[1] * SS
    img = gradient((w, h), BASE, MANTLE, horizontal=False)
    draw = ImageDraw.Draw(img)

    # Dezente Akzentlinien oben/unten im Verlauf
    bar = round(h * 0.012)
    img.paste(gradient((w, bar), BLUE, PINK), (0, 0))
    img.paste(gradient((w, bar), BLUE, PINK), (0, h - bar))

    # Logo
    logo = make_logo(logo_px * SS)
    cy_logo = round(h * 0.34)
    img.paste(logo, ((w - logo.width) // 2, cy_logo - logo.height // 2), logo)

    # Schriftzug mit Verlauf
    title_font = ImageFont.truetype(FONT_BOLD, title_px * SS)
    gradient_text(img, (w / 2, h * 0.68), "SIMPLE OS", title_font)

    # Untertitel
    sub_font = ImageFont.truetype(FONT, round(title_px * 0.32) * SS)
    draw.text((w / 2, h * 0.83), subtitle, font=sub_font, fill=SUBTEXT, anchor="mm")

    return img.resize(size, Image.LANCZOS)


def make_wallpaper(size, day=False):
    """Minimal-Motiv: geschichtete Dünen unter einem ruhigen Himmel, feine Lichtkante.
    Kein Logo, kein Text, keine Farbflecken – das Wallpaper soll hinter Fenstern verschwinden.
    Nacht (Vorgabe): Catppuccin Mocha, Lichtkante in Lavender. Tag (day=True): dieselben Dünen in Catppuccin
    Latte – heller Himmel mit einem Hauch Blau, weiße Lichtkante (simpleos-wallpaper-schedule wechselt).
    Deterministisch (fester Zufallswert), damit jeder Build dasselbe Bild liefert und Tag/Nacht dieselbe
    Landschaft zeigen."""
    import math
    import random

    rnd = random.Random(1984)
    ss = 2  # Supersampling für glatte Kanten
    w, h = size[0] * ss, size[1] * ss

    if day:
        # Himmel: oben ein heller Blauschimmer, zum Horizont hin Latte-Base
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
        # Himmel: oben Crust, zum Horizont hin Base mit einem Hauch Lavender
        sky = gradient((w, h), CRUST, lerp(BASE, LAVENDER, 0.06), horizontal=False)
        # Dünen von hinten nach vorn: hinten heller (Dunst), vorne dunkler
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
        # Lichtkante: dünne Linie auf dem Kamm, nach oben weich auslaufend
        edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(edge).line(pts, fill=rim_color + (round(255 * rim),), width=2 * ss)
        edge = edge.filter(ImageFilter.GaussianBlur(ss))
        img = Image.alpha_composite(img, layer)
        img = Image.alpha_composite(img, edge)

    img = img.convert("RGB").resize(size, Image.LANCZOS)
    # Feine Körnung gegen Farbstufen (Banding) in den dunklen Verläufen
    noise = Image.effect_noise(size, 18).convert("RGB")
    return Image.blend(img, noise, 0.018)


def make_watermark(scale=1.0):
    """Logo + Schriftzug (Plymouth-Spinner, Wallpaper) mit transparentem Hintergrund."""
    w, h = round(360 * scale) * SS, round(72 * scale) * SS
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    logo = make_logo(round(64 * scale) * SS)
    img.paste(logo, (0, (h - logo.height) // 2), logo)
    font = ImageFont.truetype(FONT_BOLD, round(34 * scale) * SS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((round(80 * scale) * SS, h / 2), "SIMPLE OS", font=font, fill=255, anchor="lm")
    x0, _, x1, _ = mask.getbbox()
    grad = Image.new("RGBA", (w, h), BLUE + (255,))
    grad.paste(gradient((x1 - x0, h), BLUE, PINK).convert("RGBA"), (x0, 0))
    img.paste(grad, (0, 0), mask)
    img = img.crop(img.getbbox())
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    cala = root / "etc/calamares/branding/simpleos"
    cala.mkdir(parents=True, exist_ok=True)
    make_logo(256).save(cala / "logo.png")
    make_logo(64).save(cala / "icon.png")
    make_banner((600, 350), 56, "Minimal. Fast. Yours.", 120).save(cala / "welcome.png")
    make_banner((800, 480), 72, "Version 1.0", 160).save(cala / "slide1.png")

    # Logo für den Setup-Wizard (Calamares-Branding wird nach der Installation entfernt)
    share = root / "usr/share/simpleos"
    share.mkdir(parents=True, exist_ok=True)
    make_logo(256).save(share / "logo.png")

    bg = root / "usr/share/backgrounds/simpleos"
    bg.mkdir(parents=True, exist_ok=True)
    make_wallpaper((2560, 1440)).save(bg / "wallpaper.png", optimize=True)
    # Tag-Variante für simpleos-wallpaper-schedule (Dynamic Wallpaper: Tag hell, abends/Nachtmodus dunkel)
    make_wallpaper((2560, 1440), day=True).save(bg / "wallpaper-day.png", optimize=True)

    ply = root / "usr/share/plymouth/themes/spinner"
    ply.mkdir(parents=True, exist_ok=True)
    make_watermark().save(ply / "watermark.png")


if __name__ == "__main__":
    main()
