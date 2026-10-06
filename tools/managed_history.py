#!/usr/bin/env python3
"""Simple OS – version history of the files the edition tool keeps up to date (called by tools/build_deb.sh).

Prints one line "<sha256>  <path>" for every version a file ever had in git and for its current version in the
build tree. The edition tool (/usr/local/lib/simpleos/edition) only replaces a file whose content is one of these
versions – nobody changed it, so it is safe to bring it to the new edition. Anything else was changed by the user
or a Simple OS tool (theme, taskbar …) and stays as it is.

    managed_history.py --repo /project --tree config/includes.chroot --base etc/skel [--exclude PATH] [--strip-installer PATH]
    managed_history.py --repo /project --tree config/includes.chroot --base . --path etc/issue --path …

Paths in the output are relative to --base. --strip-installer additionally lists each version without the
"Install Simple OS" block, as simpleos-post-install leaves it on the installed system (same sed command).
Without git (e.g. a source tarball) only the current versions are listed.
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path, PurePosixPath

REPO_PREFIX = "config/includes.chroot"
STRIP_SED = "/simpleos-installer-begin/,/simpleos-installer-end/d"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strip_installer(data):
    return subprocess.run(["sed", STRIP_SED], input=data, capture_output=True, check=True).stdout


def git(repo, *args):
    return subprocess.run(["git", "-c", "safe.directory=*", "-C", repo, *args],
                          capture_output=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tree", required=True, help="includes.chroot of the build (current versions)")
    ap.add_argument("--base", required=True, help="directory inside includes.chroot the paths are relative to")
    ap.add_argument("--path", action="append", default=[], help="only these files (relative to --base)")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--strip-installer", action="append", default=[])
    a = ap.parse_args()

    base = PurePosixPath(a.base)
    tree = Path(a.tree) / base

    def wanted(rel):
        if rel in a.exclude:
            return False
        return rel in a.path if a.path else True

    versions = set()

    def add(rel, data):
        versions.add((sha(data), rel))
        if rel in a.strip_installer:
            versions.add((sha(strip_installer(data)), rel))

    # Current versions (build tree)
    files = [tree / p for p in a.path] if a.path else sorted(tree.rglob("*"))
    for f in files:
        if f.is_file() and not f.is_symlink():
            rel = f.relative_to(tree).as_posix()
            if wanted(rel):
                add(rel, f.read_bytes())

    # Every version in git
    repo_base = PurePosixPath(REPO_PREFIX) / base
    specs = [str(repo_base / p) for p in a.path] if a.path else [str(repo_base) + "/"]
    try:
        commits = git(a.repo, "rev-list", "HEAD", "--", *specs).decode().split()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"managed_history: no git history ({e}) – current versions only", file=sys.stderr)
        commits = []
    blobs = {}
    for c in commits:
        for entry in git(a.repo, "ls-tree", "-r", "-z", c, "--", *specs).split(b"\0"):
            if not entry:
                continue
            meta, path = entry.split(b"\t", 1)
            mode, kind, obj = meta.decode().split()
            if kind != "blob" or mode == "120000":  # no symlinks
                continue
            rel = PurePosixPath(path.decode()).relative_to(repo_base).as_posix()
            if not wanted(rel):
                continue
            if obj not in blobs:
                blobs[obj] = git(a.repo, "cat-file", "blob", obj)
            add(rel, blobs[obj])

    for h, rel in sorted(versions, key=lambda v: (v[1], v[0])):
        print(f"{h}  {rel}")


if __name__ == "__main__":
    main()
