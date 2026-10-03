#!/usr/bin/env bash
# Simple OS – live-build konfigurieren.
# Läuft im Build-Container im Arbeitsverzeichnis build/, in das build_iso.sh vorher die
# Quell-Konfiguration (../config) kopiert hat. Ergänzt nur, was nicht als Datei im Repo liegt:
# die lb-config-Grundeinstellungen, die Branding-Grafiken und das fastfetch-Paket.
set -euo pipefail
TOOLS=$(cd "$(dirname "$0")" && pwd)

# contrib, non-free und non-free-firmware bleiben aktiv (Image + Quellen des Live-Systems): der Setup-Wizard
# installiert daraus zur Laufzeit steam-installer ("Ultimate Gaming", contrib) bzw. NVIDIA-Bibliotheken (non-free).
# Auf dem installierten System überschreibt Calamares (sources-final) die Quellen mit "main non-free-firmware";
# simpleos-post-install ergänzt sie danach wieder (simpleos-system-setup --repos).
# Nur amd64 im Image – i386 aktiviert der Wizard erst bei Bedarf (dpkg --add-architecture), damit apt
# sonst keine 32-Bit-Paketlisten lädt.
# Firmware: feste Liste in config/package-lists/40-hardware.list.chroot statt der Automatik (--firmware-chroot),
# die jedes Bookworm-Paket mit /lib/firmware-Dateien mitnahm (Raspberry-Pi-Bootfirmware, Astronomie-Kameras …) und
# mit der Firmware aus Backports kollidiert (firmware-realtek-rtl8723cs-bt). --firmware-binary legt Firmware nur
# für den Debian-Installer ins ISO – Simple OS installiert mit Calamares aus dem Live-System.
# Kernel/Firmware/Microcode aus bookworm-backports: config/archives/backports.pref.chroot (Kernel 6.12 kennt z.B.
# Intel Raptor Lake 0xA7AA; mit 6.1 blieb der Bildschirm bei 800x600).
lb config \
    --distribution bookworm \
    --architectures amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --backports true \
    --apt-recommends false \
    --firmware-chroot false \
    --firmware-binary false \
    --bootappend-live "boot=live components locales=en_US.UTF-8 keyboard-layouts=us quiet splash hostname=simple-os username=simple" \
    --bootappend-live-failsafe "boot=live components memtest noapic noapm nodma nomce nolapic nosmp nosplash vga=788 locales=en_US.UTF-8 keyboard-layouts=us hostname=simple-os username=simple"

# Branding-Grafiken (Calamares, Wallpaper, Wizard-Logo, Plymouth, Bootmenü der ISO) im Catppuccin-Look erzeugen
python3 "$TOOLS/gen_branding.py" config/includes.chroot config/bootloaders/isolinux

# fastfetch: nicht in bookworm/-backports -> offizielles Upstream-.deb (Version + SHA256 fest).
# Zwischengespeichert in build/downloads, damit nicht jeder Build neu lädt.
FASTFETCH_VERSION=2.69.0
FASTFETCH_SHA256=cd91bc80ba416e2089e4dd40ea087e9e02028aeeb65988f92e17ede8da1c1bda
FASTFETCH_DEB=downloads/fastfetch_${FASTFETCH_VERSION}_amd64.deb
mkdir -p downloads config/packages.chroot
if ! echo "$FASTFETCH_SHA256  $FASTFETCH_DEB" | sha256sum -c --quiet >/dev/null 2>&1; then
    curl -fsSL -o "$FASTFETCH_DEB" \
        "https://github.com/fastfetch-cli/fastfetch/releases/download/${FASTFETCH_VERSION}/fastfetch-linux-amd64.deb"
    echo "$FASTFETCH_SHA256  $FASTFETCH_DEB" | sha256sum -c --quiet
fi
cp "$FASTFETCH_DEB" config/packages.chroot/
