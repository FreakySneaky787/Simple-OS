#!/usr/bin/env bash
# Simple OS – configure live-build.
# Runs in the build container in the working directory build/, into which build_iso.sh has copied the
# source configuration (../config) beforehand. Only adds what is not stored as a file in the repo:
# the lb config basics, the branding graphics and the fastfetch package.
set -euo pipefail
TOOLS=$(cd "$(dirname "$0")" && pwd)

# contrib, non-free and non-free-firmware stay enabled (image + sources of the live system): the Setup Wizard
# installs steam-installer ("Ultimate Gaming", contrib) or NVIDIA libraries (non-free) from them at runtime.
# On the installed system Calamares (sources-final) overwrites the sources with "main non-free-firmware";
# simpleos-post-install adds them back afterwards (simpleos-system-setup --repos).
# Only amd64 in the image – the wizard enables i386 only when needed (dpkg --add-architecture), so apt
# does not download 32-bit package lists otherwise.
# Firmware: a fixed list in config/package-lists/40-hardware.list.chroot instead of the automatic selection (--firmware-chroot),
# which took every Bookworm package with /lib/firmware files (Raspberry Pi boot firmware, astronomy cameras …) and
# conflicts with the firmware from backports (firmware-realtek-rtl8723cs-bt). --firmware-binary only puts firmware
# into the ISO for the Debian installer – Simple OS installs with Calamares from the live system.
# --apt-options: never ask during the build. A conffile that already exists in the image (created by another package's
# scripts) would otherwise stop the build at dpkg's question; the edition tool takes the Simple OS version on the
# first installation of the package simpleos.
# Kernel/firmware/microcode from bookworm-backports: config/archives/backports.pref.chroot (kernel 6.12 knows e.g.
# Intel Raptor Lake 0xA7AA; with 6.1 the screen stayed at 800x600).
lb config \
    --distribution bookworm \
    --architectures amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --backports true \
    --apt-recommends false \
    --firmware-chroot false \
    --firmware-binary false \
    --apt-options "--yes -o Acquire::Retries=5 -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold" \
    --bootappend-live "boot=live components locales=en_US.UTF-8 keyboard-layouts=us quiet splash hostname=simple-os username=simple" \
    --bootappend-live-failsafe "boot=live components memtest noapic noapm nodma nomce nolapic nosmp nosplash vga=788 locales=en_US.UTF-8 keyboard-layouts=us hostname=simple-os username=simple"

# Generate the branding graphics (Calamares, wallpaper, wizard logo, Plymouth, ISO boot menu) in the Catppuccin look
python3 "$TOOLS/gen_branding.py" config/includes.chroot config/bootloaders/isolinux

# fastfetch: not in bookworm/-backports -> the official upstream .deb (version + SHA256 fixed).
# Cached in build/downloads so not every build downloads it again.
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

# Edition package "simpleos" (installed into the image, updates installed systems) + repository files in output/repo
"$TOOLS/build_deb.sh"
