#!/usr/bin/env bash
# Simple OS – Debian's rofi with Simple OS's patches (tools/rofi/*.patch, #144).
# Runs in the build container in build/ from tools/lb_config.sh (like fastfetch), as root.
#
# Why our own build: with hover-select (1.1.2, #137) Rofi made the row under a resting mouse pointer the selection as
# soon as a menu opened, and typing kept that row instead of the best match – "display settings" + Enter opened Control
# Center when the pointer happened to rest where its row appeared. Rofi has no option for either (also not 1.7.8 in
# Debian 13), so the two small patches go into Debian's own source package:
#   0001  opening a menu does not select the row under the pointer (the first real motion still does)
#   0002  every change of the typed text selects the first row (the best match) again
# The package keeps Debian's version plus "+simpleos1" (1.7.3-0.1+simpleos1 > Debian's 1.7.3-0.1+b1), so apt prefers
# it: live-build installs it from config/packages.chroot, installed systems get it from the Simple OS repository
# (output/repo, tools/build_deb.sh) with the next update. A new patch -> raise SUFFIX.
# Cached in build/downloads/rofi/<hash of this script + patches>: only a change rebuilds it (a few minutes).
# Output: config/packages.chroot/rofi_1.7.3-0.1-simpleos1_amd64.deb
set -euo pipefail
TOOLS=$(cd "$(dirname "$0")" && pwd)
DEBIAN_VERSION=1.7.3-0.1          # Debian bookworm's source package (apt-cache showsrc rofi)
SUFFIX=+simpleos1
VERSION=$DEBIAN_VERSION$SUFFIX
PATCHES=("$TOOLS"/rofi/*.patch)

hash=$(cat "$0" "${PATCHES[@]}" | sha256sum | cut -c1-16)
CACHE=downloads/rofi/$hash
# The file name without "+": GitHub renames release assets with a "+" (apt would not find the file) – the version in
# the package stays 1.7.3-0.1+simpleos1
DEB=$CACHE/rofi_${DEBIAN_VERSION}-${SUFFIX#+}_amd64.deb
mkdir -p config/packages.chroot
rm -f config/packages.chroot/rofi_*.deb
if [ -s "$DEB" ]; then
    cp "$DEB" config/packages.chroot/
    echo "rofi $VERSION: from the cache ($CACHE)"
    exit 0
fi

echo "rofi $VERSION: building Debian's rofi $DEBIAN_VERSION with ${#PATCHES[@]} Simple OS patches …"
# Source packages: only for this build, the image's own sources stay as they are (live-build configures those)
SRC=/etc/apt/sources.list.d/simpleos-build-src.sources
cat > "$SRC" <<'EOF'
Types: deb-src
URIs: http://deb.debian.org/debian
Suites: bookworm
Components: main
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF
WORK=$(mktemp -d)
trap 'rm -rf "$WORK" "$SRC"' EXIT
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends dpkg-dev fakeroot >/dev/null
apt-get build-dep -y -qq "rofi=$DEBIAN_VERSION" >/dev/null
(cd "$WORK" && apt-get source -qq --download-only "rofi=$DEBIAN_VERSION" && dpkg-source -x --no-check --skip-patches rofi_*.dsc src >/dev/null)

S=$WORK/src
mkdir -p "$S/debian/patches"
touch "$S/debian/patches/series"
for p in "${PATCHES[@]}"; do
    cp "$p" "$S/debian/patches/simpleos-${p##*/}"
    echo "simpleos-${p##*/}" >> "$S/debian/patches/series"
done
{
    printf 'rofi (%s) bookworm; urgency=medium\n\n' "$VERSION"
    printf '  * Simple OS: opening a menu does not select the row under the mouse pointer,\n'
    printf '    and typing selects the best match again (#144).\n\n'
    printf ' -- Simple OS <noreply@simpleos.invalid>  %s\n\n' "$(date -R -u -d @"${SOURCE_DATE_EPOCH:-$(date +%s)}")"
    cat "$S/debian/changelog"
} > "$WORK/changelog" && mv "$WORK/changelog" "$S/debian/changelog"

# nocheck: Rofi's own unit tests need a display for some parts; the behaviour is checked by the verify hook instead
(cd "$S" && DEB_BUILD_OPTIONS="nocheck noddebs" dpkg-buildpackage -b -uc -us >"$WORK/build.log" 2>&1) || {
    tail -n 40 "$WORK/build.log" >&2
    echo "build_rofi: the build failed (log above)" >&2
    exit 1
}
# Every patch must really be in the build: unpacked with --skip-patches, dpkg-buildpackage applies the whole series
# before building ("applying …" in its log) and takes it out again afterwards
for p in "${PATCHES[@]}"; do
    grep -q "info: applying simpleos-${p##*/}" "$WORK/build.log" || {
        echo "build_rofi: patch ${p##*/} was not applied" >&2
        exit 1
    }
done
rm -rf downloads/rofi
mkdir -p "$CACHE"
cp "$WORK/rofi_${VERSION}_amd64.deb" "$DEB"
cp "$DEB" config/packages.chroot/
echo "rofi $VERSION: built ($DEB)"
