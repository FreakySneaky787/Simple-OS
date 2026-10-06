#!/usr/bin/env bash
# Simple OS – build the edition package "simpleos" and the (unsigned) APT repository files.
# Runs in the build container in build/ at the end of tools/lb_config.sh, after the branding graphics exist.
#
# The package carries Simple OS itself – everything from config/includes.chroot that an installed system keeps
# (tools, settings, /etc/skel, look, os-release) – so a newer Simple OS reaches installed systems as an ordinary
# update: /etc/apt/sources.list.d/simpleos.sources -> GitHub release "latest" -> Software Updates (simpleos-update).
# What a package cannot do by itself, the edition tool (/usr/local/lib/simpleos/edition) does from the postinst and
# at sign-in; its data lands in /usr/share/simpleos/edition:
#   version, packages         Simple OS version (os-release VERSION_ID), the package lists (new entries are
#                             installed once by "simpleos-system-setup --upgrade")
#   skel.history              every version of every /etc/skel file -> unchanged copies in the homes are updated
#   system/                   files that belong to Debian packages (dpkg would refuse them in our package)
#   system.history            every version of every /etc file (conffiles + system/): an unchanged older copy is
#                             replaced – also when dpkg kept it as "changed" (systems from before the package)
#   hooks/                    build hooks marked "Re-run on Simple OS updates" (derived system settings)
#   migrations/{system,user}  from config/includes.chroot (one-time steps of an edition, see README)
# Output: config/packages.chroot/simpleos_<version>_all.deb (installed into the image by live-build) and
# ../output/repo/ (debs + Packages + Release; tools/release.sh signs and publishes it).
set -euo pipefail
TOOLS=$(cd "$(dirname "$0")" && pwd)
PROJECT=$(dirname "$TOOLS")
INC=config/includes.chroot
REPO_OUT=../output/repo

VERSION=$(sed -n 's/^VERSION_ID="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "$INC/usr/lib/os-release")
[[ $VERSION =~ ^[0-9]+(\.[0-9]+)*$ ]] || { echo "build_deb: VERSION_ID in usr/lib/os-release missing or invalid: '$VERSION'" >&2; exit 1; }
KEYRING=$INC/usr/share/keyrings/simpleos-archive-keyring.asc
if ! grep -q 'BEGIN PGP PUBLIC KEY BLOCK' "$KEYRING" 2>/dev/null; then
    echo "build_deb: release key missing ($KEYRING)." >&2
    echo "  Installed systems could not check updates without it. Create it once: ./tools/release.sh key" >&2
    exit 1
fi

# Not in the package (relative to includes.chroot; a trailing / = the whole folder):
#   installer and live session only – removed by simpleos-post-install anyway
#   first defaults that the installer (Calamares) and the user own afterwards
EXCLUDE=(
    etc/calamares/
    usr/sbin/bootloader-config
    usr/local/sbin/simpleos-post-install
    usr/local/lib/simpleos/open-as-user
    usr/share/applications/simpleos-install.desktop
    etc/skel/.config/autostart/calamares-desktop-icon.desktop
    etc/lightdm/lightdm.conf.d/01_autologin.conf
    etc/sudoers.d/simple-nopasswd
    etc/default/grub
    etc/default/keyboard
    etc/default/locale
    etc/locale.gen
)
# Files of Debian packages (dpkg refuses to overwrite them) or created by their scripts (/etc/motd: base-files'
# postinst – as a conffile, dpkg would ask about it during the build): a copy in /usr/share/simpleos/edition/system,
# the edition tool replaces the real file if nobody changed it. /usr/lib/os-release (base-files) is diverted instead.
DEBIAN_OWNED=(
    etc/issue
    etc/motd
    etc/default/zramswap
    etc/lightdm/lightdm-gtk-greeter.conf
    etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml
)
MENU=etc/skel/.config/openbox/menu.xml
# Build hooks that derive system settings and may run again on every update (idempotent)
HOOK_MARK='Re-run on Simple OS updates'
# Package lists of the installer/bootloader stay out of the edition (Calamares is purged after the installation)
LIST_EXCLUDE='50-installer|55-bootloader'

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
ROOT=$STAGE/simpleos

rsync_ex=()
for p in "${EXCLUDE[@]}" "${DEBIAN_OWNED[@]}"; do rsync_ex+=(--exclude "/$p"); done
rsync -a --exclude __pycache__ --exclude '*.pyc' "${rsync_ex[@]}" "$INC/" "$ROOT/"
# Folders left empty by the exclusions (e.g. /etc/sudoers.d: the package would take it over with other permissions)
find "$ROOT" -mindepth 1 -type d -empty -delete
mkdir -p "$ROOT/DEBIAN"
# The installed system has no "Install Simple OS" entry (simpleos-post-install removes it from the image's copy);
# the live image gets the full menu from includes.chroot, which live-build copies over the package's files.
sed -i '/simpleos-installer-begin/,/simpleos-installer-end/d' "$ROOT/$MENU"

ED=$ROOT/usr/share/simpleos/edition
mkdir -p "$ED/system" "$ED/hooks"
echo "$VERSION" > "$ED/version"
for p in "${DEBIAN_OWNED[@]}"; do
    [ -f "$INC/$p" ] || { echo "build_deb: $INC/$p missing" >&2; exit 1; }
    install -D -m 0644 "$INC/$p" "$ED/system/$p"
done
for f in config/package-lists/*.list.chroot; do
    [[ ${f##*/} =~ ^($LIST_EXCLUDE) ]] && continue
    sed -e 's/#.*//' -e 's/[[:space:]]//g' "$f"
done | grep . | sort -u > "$ED/packages"
for h in config/hooks/live/*.hook.chroot; do
    grep -q "$HOOK_MARK" "$h" && install -m 0755 "$h" "$ED/hooks/${h##*/}"
done

skel_ex=()
for p in "${EXCLUDE[@]}"; do [[ $p == etc/skel/* ]] && skel_ex+=(--exclude "${p#etc/skel/}"); done
python3 "$TOOLS/managed_history.py" --repo "$PROJECT" --tree "$INC" --base etc/skel "${skel_ex[@]}" \
    --strip-installer "${MENU#etc/skel/}" > "$ED/skel.history"
sys_paths=()
for p in "${DEBIAN_OWNED[@]}"; do sys_paths+=(--path "$p"); done
while IFS= read -r p; do sys_paths+=(--path "$p"); done < <(cd "$ROOT" && find etc -type f | sort)
python3 "$TOOLS/managed_history.py" --repo "$PROJECT" --tree "$INC" --base . "${sys_paths[@]}" \
    --strip-installer "$MENU" > "$ED/system.history"

# Package scripts. os-release belongs to base-files: divert Debian's copy to os-release.debian (images up to
# 1.0 did this in hook 13 as a "local" diversion – taken over by the package).
cat > "$ROOT/DEBIAN/preinst" <<'SH'
#!/bin/sh
set -e
OSR=/usr/lib/os-release
case "$1" in
    install|upgrade)
        [ "$(dpkg-divert --listpackage "$OSR")" = LOCAL ] && dpkg-divert --local --no-rename --remove "$OSR" >/dev/null
        # Without --rename: base-files is Essential, the file must never be missing (our version is unpacked over
        # it; Debian's next version goes to os-release.debian)
        [ "$(dpkg-divert --listpackage "$OSR")" = simpleos ] ||
            dpkg-divert --package simpleos --no-rename --divert "$OSR.debian" --add "$OSR" >/dev/null ;;
esac
exit 0
SH
cat > "$ROOT/DEBIAN/postinst" <<'SH'
#!/bin/sh
set -e
if [ "$1" = configure ]; then
    ln -sfn ../usr/lib/os-release /etc/os-release
    [ -d /run/systemd/system ] && systemctl daemon-reload >/dev/null 2>&1 || true
    # Debian-owned files, derived settings, migrations – never makes the installation fail (log: /var/log/simpleos-edition.log)
    # $2 empty = first installation of the package (in the image, or a system from before the package existed)
    if [ -z "$2" ]; then first=--first-install; else first=; fi
    /usr/local/lib/simpleos/edition --system $first || true
fi
exit 0
SH
cat > "$ROOT/DEBIAN/postrm" <<'SH'
#!/bin/sh
set -e
case "$1" in
    remove|abort-install|disappear)
        OSR=/usr/lib/os-release
        if [ -e "$OSR.debian" ]; then rename=--rename; else rename=--no-rename; fi
        dpkg-divert --package simpleos $rename --divert "$OSR.debian" --remove "$OSR" >/dev/null ;;
esac
exit 0
SH
chmod 0755 "$ROOT/DEBIAN/preinst" "$ROOT/DEBIAN/postinst" "$ROOT/DEBIAN/postrm"

# Permissions as in the image: no group/world write bits (the build copy may have them from the umask)
find "$ROOT" -path "$ROOT/DEBIAN" -prune -o ! -type l -exec chmod go-w {} +
# Every regular file under /etc is a conffile: changed by the user/admin -> kept on updates (helper: --force-confold)
(cd "$ROOT" && find etc -type f | sed 's|^|/|' | sort) > "$ROOT/DEBIAN/conffiles"
HOME_URL=$(sed -n 's/^HOME_URL="\(.*\)"/\1/p' "$INC/usr/lib/os-release")
cat > "$ROOT/DEBIAN/control" <<CTRL
Package: simpleos
Version: $VERSION
Architecture: all
Maintainer: Simple OS <simpleos@users.noreply.github.com>
Installed-Size: $(du -sk --exclude=DEBIAN "$ROOT" | cut -f1)
Section: misc
Priority: optional
Homepage: $HOME_URL
Description: Simple OS – desktop, tools and settings
 Everything that makes a Debian system Simple OS: the Openbox desktop settings, the Simple OS tools
 (Control Center, Software Updates, Setup Wizard …), the look and the system settings.
 Updates of this package bring installed systems to the newest Simple OS edition.
CTRL

DEB=simpleos_${VERSION}_all.deb
mkdir -p config/packages.chroot
rm -f config/packages.chroot/simpleos_*.deb
dpkg-deb --root-owner-group -Zxz --build "$ROOT" "config/packages.chroot/$DEB" >/dev/null

# APT repository (flat): the edition package and the other own packages (fastfetch, not in Debian)
rm -rf "$REPO_OUT"
mkdir -p "$REPO_OUT"
cp config/packages.chroot/*.deb "$REPO_OUT/"
(
    cd "$REPO_OUT"
    apt-ftparchive packages . > Packages
    gzip -9nk Packages
    apt-ftparchive -o APT::FTPArchive::Release::Origin="Simple OS" -o APT::FTPArchive::Release::Label="Simple OS" \
        -o APT::FTPArchive::Release::Description="Simple OS $VERSION" release . > "$STAGE/Release"
    mv "$STAGE/Release" Release
)
echo "Edition package: config/packages.chroot/$DEB ($(du -h "config/packages.chroot/$DEB" | cut -f1)), repository: output/repo (unsigned)"
