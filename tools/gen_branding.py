#!/usr/bin/env python3
"""Erzeugt die Simple-OS-Branding-Grafiken (Catppuccin Mocha).

Marke: "SOS" (Simple Operating System), das "O" ist ein Rettungsring – Rettung vor Big Tech – mit dem Spruch
"Keep it Simple". Ring weiß mit vier Streifen in Catppuccin Red (rot-weiß, auch in 16 px als Rettungsring
erkennbar), die beiden "S" im Simple-OS-Verlauf Blau -> Pink. Das Logo (logo.png, icon.png) ist der Ring allein.

Aufruf: gen_branding.py <includes.chroot-Ordner> [<bootloaders/isolinux-Ordner>]
        gen_branding.py --readme docs     (nur das README-Banner docs/sos-banner.png)
Erzeugt darin:
  etc/calamares/branding/simpleos/{logo,icon,welcome,slide1}.png
  usr/share/simpleos/logo.png
  usr/share/backgrounds/simpleos/wallpaper.png (2560x1440)
  usr/share/plymouth/themes/spinner/watermark.png
und im zweiten Ordner das Bootmenü-Bild der ISO (statt live-builds Debian-Helm mit "Debian GNU/Linux"):
  splash.png (640x480, isolinux/BIOS) und splash800x600.png (GRUB/UEFI nutzt es, solange es kein eigenes hat)
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
RED = (0xF3, 0x8B, 0xA8)          # Catppuccin Mocha Red: Streifen des Rettungsrings
RING = (0xF5, 0xF6, 0xFA)         # Grundfarbe des Rings (fast weiß)
TEXT = (0xCD, 0xD6, 0xF4)
SLOGAN = "Keep it Simple"

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


def make_lifebuoy(size):
    """Rettungsring: weißer Ring, vier rote Streifen diagonal (45°, 135°, 225°, 315°), Loch transparent.
    Ab 40 px und kleiner ist der Ring dicker, damit die Streifen sichtbar bleiben (Taskleiste, Symbole)."""
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
    """Logo = Rettungsring (Calamares, Setup-Wizard, Welcome-Seite)."""
    return make_lifebuoy(size)


def make_wordmark(cap_px):
    """Wortmarke "S [Ring] S", transparent, auf den Inhalt zugeschnitten. cap_px = Höhe der Großbuchstaben;
    der Ring ist 10 % größer (Überhang wie bei einem echten "O")."""
    font = ImageFont.truetype(FONT_BOLD, 100 * SS)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    l0, t0, r0, b0 = probe.textbbox((0, 0), "S", font=font, anchor="ls")
    fsize = round(100 * SS * cap_px * SS / (b0 - t0))          # Schriftgröße für die gewünschte Höhe
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
    """Calamares-Willkommensbild/-Folie: SOS-Wortmarke, darunter "Keep it Simple" und eine leise Zeile."""
    w, h = size[0] * SS, size[1] * SS
    img = gradient((w, h), BASE, MANTLE, horizontal=False).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Dezente Akzentlinien oben/unten im Verlauf
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
    """SOS-Wortmarke (Plymouth-Spinner, Bootmenü) mit transparentem Hintergrund."""
    return make_wordmark(round(58 * scale))


def make_boot_splash(size, logo_y):
    """Hintergrund der Bootmenüs: dunkler Verlauf, Logo + Schriftzug oben (Mitte bei logo_y, Anteil der Höhe).
    Darunter bleibt alles frei – GRUB zeichnet sein Menü ab 52 % der Höhe, isolinux ab etwa 40 %."""
    w, h = size
    img = gradient(size, CRUST, BASE, horizontal=False)
    mark = make_watermark(scale=w / 800)
    img.paste(mark, ((w - mark.width) // 2, round(h * logo_y) - mark.height // 2), mark)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, max(11, round(14 * w / 800)))
    draw.text((w / 2, round(h * logo_y) + mark.height // 2 + round(18 * w / 800)), f"{SLOGAN} · Version 1.0",
              font=font, fill=SUBTEXT, anchor="mt")
    # vesamenu (isolinux) und GRUB lesen nur einfache PNGs: RGB, 8 Bit, ohne Interlacing
    return img.convert("RGB")


def main():
    # README-Banner fürs Repository (docs/sos-banner.png): gen_branding.py --readme docs
    if len(sys.argv) > 2 and sys.argv[1] == "--readme":
        out = Path(sys.argv[2])
        out.mkdir(parents=True, exist_ok=True)
        make_banner((1280, 420), 110, "Simple Operating System · Debian 12 · Openbox").save(
            out / "sos-banner.png", optimize=True)
        return

    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    cala = root / "etc/calamares/branding/simpleos"
    cala.mkdir(parents=True, exist_ok=True)
    make_logo(256).save(cala / "logo.png")
    make_logo(64).save(cala / "icon.png")
    make_banner((600, 350), 72, "Simple Operating System").save(cala / "welcome.png")
    make_banner((800, 480), 96, "Simple Operating System · Version 1.0").save(cala / "slide1.png")

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

    if len(sys.argv) > 2:
        boot = Path(sys.argv[2])
        boot.mkdir(parents=True, exist_ok=True)
        make_boot_splash((640, 480), 0.20).save(boot / "splash.png")
        make_boot_splash((800, 600), 0.27).save(boot / "splash800x600.png")


if __name__ == "__main__":
    main()
