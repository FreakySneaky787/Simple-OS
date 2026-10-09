#!/usr/bin/env bash
# Simple OS – release a new edition: sign the update repository and publish it on GitHub.
#   ./tools/release.sh key        once: create the release signing key (asks for a passphrase) and put the public key
#                                 into the image (config/includes.chroot/usr/share/keyrings/simpleos-archive-keyring.asc)
#   ./tools/release.sh version X.Y.Z
#                                 set the version of the next edition everywhere it is shown: VERSION_ID (what the build
#                                 and the package use), VERSION and PRETTY_NAME in usr/lib/os-release, the installer's
#                                 branding (etc/calamares/branding/simpleos/branding.desc). The build refuses a mismatch.
#   ./tools/release.sh sign       sign output/repo (after ./build_iso.sh): InRelease + Release.gpg
#   ./tools/release.sh publish [--no-iso]
#                                 GitHub release v<VERSION> with the ISO and the signed repository, then mark it as
#                                 "latest" – from that moment every installed Simple OS is offered the new edition
#
# Installed systems read the repository from https://github.com/<owner>/<repo>/releases/latest/download/
# (/etc/apt/sources.list.d/simpleos.sources). So EVERY release must carry the repository files – a "latest" release
# without them breaks "Check for updates" on all systems. publish therefore creates a draft first, uploads everything,
# checks the asset list and only then publishes it.
# New edition: ./tools/release.sh version X.Y.Z, commit and push, ./build_iso.sh, test (TESTING.md),
# ./tools/release.sh sign && ./tools/release.sh publish.
# The private key lives outside the repository ($SIMPLEOS_GNUPGHOME, default ~/.local/share/simpleos-release/gnupg).
# Back it up: without it no further update can be signed, and installed systems only trust this key.
set -euo pipefail
cd "$(dirname "$0")/.."

GNUPGHOME=${SIMPLEOS_GNUPGHOME:-$HOME/.local/share/simpleos-release/gnupg}
export GNUPGHOME
# pinentry in the terminal (passphrase of the key)
GPG_TTY=$(tty 2>/dev/null || true)
export GPG_TTY
PUBKEY=config/includes.chroot/usr/share/keyrings/simpleos-archive-keyring.asc
OSR=config/includes.chroot/usr/lib/os-release
BRANDING=config/includes.chroot/etc/calamares/branding/simpleos/branding.desc
SOURCES=config/includes.chroot/etc/apt/sources.list.d/simpleos.sources
REPO=output/repo
ISO=output/Simple-OS.iso
REPO_FILES=(Packages Packages.gz Release InRelease Release.gpg)

die() { echo "release: $*" >&2; exit 1; }
version() { sed -n 's/^VERSION_ID="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "$OSR"; }
# owner/repo from the APT source (the URL installed systems really use)
gh_repo() { sed -n 's|^URIs: *https://github.com/\([^/]*/[^/]*\)/releases/latest/download/$|\1|p' "$SOURCES"; }

cmd_key() {
    [ -e "$PUBKEY" ] && die "$PUBKEY exists already – installed systems trust that key. Delete it only if you really want a new one."
    command -v gpg >/dev/null || die "gpg missing"
    mkdir -p "$GNUPGHOME"
    chmod 0700 "$GNUPGHOME"
    if ! gpg --list-secret-keys 2>/dev/null | grep -q .; then
        echo "Creating the Simple OS release key (choose a passphrase – you need it for every release) …"
        gpg --quick-generate-key "Simple OS Release Signing Key" ed25519 sign never
    fi
    mkdir -p "${PUBKEY%/*}"
    gpg --armor --export > "$PUBKEY"
    grep -q 'BEGIN PGP PUBLIC KEY BLOCK' "$PUBKEY" || { rm -f "$PUBKEY"; die "export failed"; }
    echo "Public key: $PUBKEY (commit it)"
    echo "Private key: $GNUPGHOME – BACK IT UP (e.g. gpg --export-secret-keys --armor > a safe place)."
}

# The repository is signed with the key the image trusts (not just any key in the keyring)
check_signature() {
    local tmp
    tmp=$(mktemp -d)
    GNUPGHOME=$tmp gpg --quiet --import "$PUBKEY" 2>/dev/null
    GNUPGHOME=$tmp gpg --quiet --verify "$REPO/InRelease" 2>/dev/null &&
        GNUPGHOME=$tmp gpg --quiet --verify "$REPO/Release.gpg" "$REPO/Release" 2>/dev/null
    local rc=$?
    rm -rf "$tmp"
    return $rc
}

check_repo() {
    local v
    v=$(version)
    for f in "${REPO_FILES[@]}"; do [ -s "$REPO/$f" ] || die "$REPO/$f missing – ./build_iso.sh, then ./tools/release.sh sign"; done
    [ -f "$REPO/simpleos_${v}_all.deb" ] || die "$REPO/simpleos_${v}_all.deb missing – the repository is from another version (os-release says $v)"
    awk -v v="$v" '/^Package: simpleos$/ { p = 1 } p && /^Version:/ { if ($2 == v) found = 1; p = 0 } END { exit !found }' "$REPO/Packages" ||
        die "Packages does not list simpleos $v"
    check_signature || die "the signature does not match $PUBKEY"
    # GitHub renames asset names with other characters (+ ~ : …) – apt would then not find the file
    local f
    for f in "$REPO"/*; do
        [[ ${f##*/} =~ ^[A-Za-z0-9._-]+$ ]] || die "file name ${f##*/} is not allowed as a GitHub asset"
    done
}

cmd_version() {
    local v=${1:-} cur
    [[ $v =~ ^[0-9]+(\.[0-9]+)*$ ]] || die "usage: ./tools/release.sh version X.Y.Z (digits and dots, e.g. 1.0.1)"
    cur=$(version)
    if [ -n "$cur" ] && [ "$(printf '%s\n%s\n' "$cur" "$v" | sort -V | tail -n 1)" != "$v" ]; then
        die "$v is older than the current version $cur – installed systems never go back to an older edition"
    fi
    sed -i -e "s/^VERSION_ID=.*/VERSION_ID=\"$v\"/" -e "s/^VERSION=.*/VERSION=\"$v\"/" \
        -e "s/^PRETTY_NAME=.*/PRETTY_NAME=\"Simple OS v$v\"/" "$OSR"
    sed -i -E -e "s/^( *(version|shortVersion): *).*/\1\"$v\"/" \
        -e "s/^( *(versionedName|shortVersionedName): *).*/\1\"Simple OS $v\"/" "$BRANDING"
    [ "$(version)" = "$v" ] && [ "$(grep -cE "^ *(version|shortVersion): *\"$v\"\$|^ *(versionedName|shortVersionedName): *\"Simple OS $v\"\$" "$BRANDING")" = 4 ] ||
        die "could not set the version in $OSR / $BRANDING – check both files"
    echo "Version $v set in $OSR and $BRANDING."
    echo "Next: commit and push, ./build_iso.sh, test (TESTING.md), ./tools/release.sh sign, ./tools/release.sh publish"
}

cmd_sign() {
    [ -s "$REPO/Release" ] || die "$REPO/Release missing – build first (./build_iso.sh)"
    [ -s "$PUBKEY" ] || die "no release key – ./tools/release.sh key"
    rm -f "$REPO/InRelease" "$REPO/Release.gpg"
    # The passphrase comes from pinentry (no --batch – it would not ask)
    gpg --yes --digest-algo SHA512 --clearsign -o "$REPO/InRelease" "$REPO/Release"
    gpg --yes --digest-algo SHA512 --armor --detach-sign -o "$REPO/Release.gpg" "$REPO/Release"
    check_repo
    echo "Signed: $REPO (Simple OS $(version))"
}

cmd_publish() {
    local with_iso=1
    [ "${1:-}" = --no-iso ] && with_iso=0
    command -v gh >/dev/null || die "GitHub CLI (gh) missing"
    local v repo tag latest
    v=$(version)
    repo=$(gh_repo)
    [ -n "$repo" ] || die "no GitHub URL in $SOURCES"
    tag="v$v"
    check_repo
    # The next edition recognizes unchanged files by their versions in git – an edition from uncommitted files
    # would not be in it (its files would count as "changed by the user" forever)
    [ -z "$(git status --porcelain -- config tools)" ] || die "uncommitted changes in config/ or tools/ – commit, rebuild, then publish"
    # The tag must point to the commit that was built: without --target, "gh release create" tags the newest commit of
    # GitHub's default branch – another one as soon as something is not pushed yet (the release's source code would
    # then not be the ISO's). So: this commit, and it must be on GitHub already.
    local head tagged
    head=$(git rev-parse HEAD)
    git fetch --quiet --tags origin || die "git fetch origin failed (network? a local tag that differs from GitHub's?)"
    [ -n "$(git branch -r --contains "$head")" ] || die "commit ${head:0:7} is not on GitHub yet – git push first, then publish"
    tagged=$(git rev-parse -q --verify "refs/tags/$tag^{commit}" || true)
    [ -z "$tagged" ] || [ "$tagged" = "$head" ] || die "tag $tag exists already and points to ${tagged:0:7}, not to ${head:0:7}"
    # The ISO and the update package must come from this commit: build_iso.sh records the commit and whether config/ and
    # tools/ were clean (output/repo/.build-state). A commit made after the build would be in the release's source code
    # but not in what installed systems download.
    local bcommit bdirty
    bcommit=$(sed -n 's/^commit=//p' "$REPO/.build-state" 2>/dev/null)
    bdirty=$(sed -n 's/^dirty=//p' "$REPO/.build-state" 2>/dev/null)
    [ -n "$bcommit" ] || die "output/repo/.build-state missing – run ./build_iso.sh again (it records the commit the build is made from)"
    [ "$bdirty" = 0 ] || die "the build was made from uncommitted changes in config/ or tools/ – commit, run ./build_iso.sh again, then sign and publish"
    git cat-file -e "$bcommit^{commit}" 2>/dev/null || die "the build commit ${bcommit:0:7} is unknown here – run ./build_iso.sh again"
    git diff --quiet "$bcommit" "$head" -- config tools ||
        die "config/ or tools/ changed since the build (${bcommit:0:7} → ${head:0:7}): the ISO and the update package do not contain it – run ./build_iso.sh again, then sign and publish"
    local assets=()
    for f in "$REPO"/*; do assets+=("$f"); done
    if [ "$with_iso" = 1 ]; then
        [ -f "$ISO" ] || die "$ISO missing (or --no-iso for an update without a new ISO)"
        # Same build: the ISO must contain this repository's simpleos package (a later --config-only rebuilds output/repo
        # without the marker build_iso.sh writes; file times do not help – live-build dates the ISO to the build start)
        (cd "$REPO" && sha256sum --quiet -c .in-iso >/dev/null 2>&1) ||
            die "output/repo is not from the ISO build – run ./build_iso.sh again, then sign and publish"
        assets+=("$ISO" "$ISO.sha256" output/Simple-OS.packages.txt)
    fi
    # Installed systems download without a GitHub login: release files of a private repository are not reachable
    local vis
    vis=$(gh repo view "$repo" --json visibility -q .visibility 2>/dev/null || true)
    [ "$vis" = PUBLIC ] || die "github.com/$repo is ${vis:-not reachable} – make it public first (Settings → Danger Zone → Change visibility); installed systems cannot download updates from a private repository"
    gh release view "$tag" -R "$repo" >/dev/null 2>&1 && die "release $tag exists already – raise the version (./tools/release.sh version X.Y.Z)"
    # Never go backwards: apt would not install an older edition anyway
    latest=$(gh release view -R "$repo" --json tagName -q .tagName 2>/dev/null || true)
    latest=${latest#v}
    if [ -n "$latest" ]; then
        if [ "$latest" = "$v" ] || [ "$(printf '%s\n%s\n' "$latest" "$v" | sort -V | tail -n 1)" != "$v" ]; then
            die "version $v is not newer than the latest release $latest"
        fi
    fi
    echo "Creating draft release $tag on $repo (commit ${head:0:7}) …"
    gh release create "$tag" -R "$repo" --target "$head" --draft --title "Simple OS $v" --notes-file RELEASE_NOTES.md "${assets[@]}" ||
        die "upload failed – remove the draft (gh release delete $tag -R $repo --yes) and run publish again"
    local names
    names=$(gh release view "$tag" -R "$repo" --json assets -q '.assets[].name')
    for f in "${REPO_FILES[@]}" "simpleos_${v}_all.deb"; do
        grep -qx "$f" <<<"$names" || die "asset $f missing in the draft $tag – NOT published (fix it and run: gh release edit $tag -R $repo --draft=false --latest)"
    done
    gh release edit "$tag" -R "$repo" --draft=false --latest
    # As an installed system sees it: anonymous, through "latest"
    curl -fsSL -o /dev/null "https://github.com/$repo/releases/latest/download/InRelease" ||
        die "published, but https://github.com/$repo/releases/latest/download/InRelease cannot be downloaded – check the release on GitHub"
    echo "Published: Simple OS $v – installed systems are offered it at their next update check."
}

case "${1:-}" in
    key)     cmd_key ;;
    version) shift; cmd_version "$@" ;;
    sign)    cmd_sign ;;
    publish) shift; cmd_publish "$@" ;;
    *) sed -n '2,12p' "$0" >&2; exit 2 ;;
esac
