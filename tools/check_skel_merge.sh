#!/usr/bin/env bash
# Simple OS – will the update reach the accounts? (called by tools/build_deb.sh)
#
# At sign-in the edition tool merges a changed /etc/skel file into the account's own copy with diff3 (base = the
# version the copy came from). If Simple OS changed lines right next to lines the account's copy changed, diff3
# gives up and the copy stays OLD ("kept … changed in the same places" in ~/.cache/simpleos-edition.log) – the update
# silently never arrives. 1.0.5 nearly shipped like that (menu.xml: diff3 lined up the removed installer block
# differently on both sides – the edition tool now merges without that block, see merge_file).
# Simulates the copies every installed account has, from the files of the last release tag:
#   menu.xml   without the "Install Simple OS" block (simpleos-post-install), with office entries (office-menu)
#              -> a conflict is an ERROR (every installed system looks like that)
#   any file   with an own line at the end (people add to autostart …) -> a conflict is a WARNING
# "The last release" = the newest tag v<version> in this branch's history that is older than the version being built.
# Release tags are made on GitHub (tools/release.sh publish) and only reach this clone with "git fetch --tags" (#77):
# a gap in the patch numbers (v1.0.4 found, 1.0.6 built) gives a warning.
# Without git or tags (source tarball, first release): nothing to compare, exit 0.
set -uo pipefail
PROJECT=${1:?project folder}
INC=${2:?includes.chroot of the build}
SKEL=etc/skel
command -v git >/dev/null && command -v diff3 >/dev/null || { echo "check_skel_merge: git/diff3 missing – skipped"; exit 0; }
cur=$(sed -n 's/^VERSION_ID="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "$INC/usr/lib/os-release" 2>/dev/null)
prev=
while IFS= read -r t; do
    v=${t#v}
    [[ $v =~ ^[0-9]+(\.[0-9]+)*$ ]] || continue
    # older than the version being built (without one: the newest tag)
    if [ -z "$cur" ] || { [ "$v" != "$cur" ] && [ "$(printf '%s\n%s\n' "$v" "$cur" | sort -V | head -n 1)" = "$v" ]; }; then
        prev=$t
        break
    fi
done < <(git -C "$PROJECT" tag --merged HEAD --list 'v*' --sort=-v:refname 2>/dev/null)
[ -n "$prev" ] || { echo "check_skel_merge: no release tag – skipped"; exit 0; }
# X.Y.Z built, X.Y.(Z-2 or older) found: the release in between is most likely only missing here
IFS=. read -r pa pb pc <<<"${prev#v}"
IFS=. read -r ca cb cc <<<"$cur"
if [ "${pa:-0}.${pb:-0}" = "${ca:-0}.${cb:-0}" ] && [ $(( ${cc:-0} - ${pc:-0} )) -gt 1 ]; then
    echo "check_skel_merge: warning – the newest release tag here is $prev, but $cur is being built: is a release in between" >&2
    echo "  missing in this clone? Run 'git fetch --tags origin' and build again (the check compares with $prev)." >&2
fi
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
strip() { sed '/simpleos-installer-begin/,/simpleos-installer-end/d' "$1"; }
errors=0

old() {  # PATH below etc/skel -> file of the last release (1 = did not exist)
    git -C "$PROJECT" show "$prev:config/includes.chroot/$SKEL/$1" > "$tmp/old" 2>/dev/null
}
merges() {  # USER BASE NEW -> 0 if diff3 merges without a conflict
    diff3 -m "$1" "$2" "$3" > "$tmp/merged" 2>/dev/null
}

menu=.config/openbox/menu.xml
if old "$menu" && ! cmp -s "$tmp/old" "$INC/$SKEL/$menu"; then
    strip "$tmp/old" > "$tmp/user"
    SIMPLEOS_OFFICE_APPS="writer calc impress onlyoffice" sh "$INC/usr/local/lib/simpleos/office-menu" "$tmp/user"
    strip "$tmp/old" > "$tmp/base-stripped"
    strip "$INC/$SKEL/$menu" > "$tmp/new-stripped"
    # as the edition tool merges it (merge_file): the account's copy has no installer block -> base and new without it
    if ! merges "$tmp/user" "$tmp/base-stripped" "$tmp/new-stripped"; then
        echo "check_skel_merge: ERROR – $menu of $prev does not merge into installed accounts (installer block removed," >&2
        echo "  office entries added). Keep the lines next to the office marker as they were." >&2
        errors=1
    fi
fi

while IFS= read -r f; do
    p=${f#"$INC/$SKEL/"}
    old "$p" || continue
    cmp -s "$tmp/old" "$f" && continue
    { cat "$tmp/old"; echo "# a line of your own"; } > "$tmp/user"
    merges "$tmp/user" "$tmp/old" "$f" ||
        echo "check_skel_merge: warning – $p: an account that added a line at the end keeps the old version (change the end of the file less)"
done < <(find "$INC/$SKEL" -type f ! -name '*.png' ! -name '*.svg')

[ "$errors" -eq 0 ] && echo "check_skel_merge: /etc/skel changes since $prev merge into existing accounts"
exit "$errors"
