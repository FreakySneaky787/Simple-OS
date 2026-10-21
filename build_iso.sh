#!/usr/bin/env bash
# Simple OS – build the ISO.
#   ./build_iso.sh                 build the ISO -> output/Simple-OS.iso (privileged container, needs sudo)
#   ./build_iso.sh --config-only   only generate the live-build configuration in build/config (without sudo, for checking)
#                                  – also builds the edition package "simpleos" and output/repo (tools/build_deb.sh)
#
# The source is config/ (never modified). The build happens in build/: the freshly copied
# configuration, all live-build intermediates and build.log end up there.
set -euo pipefail
cd "$(dirname "$0")"

IMAGE="simple-os-builder"
# Which commit is this build made from, and were config/ and tools/ clean? tools/release.sh publish refuses an ISO that
# was built from uncommitted files or from another commit than the one it tags (recorded now, checked again after the
# build). Only config/ and tools/ count: a commit of README/ROADMAP during the build moved HEAD and marked the 1.0.5
# build dirty (#72). --no-optional-locks: as root (sudo ./build_iso.sh) git must not rewrite the user's .git/index.
uncommitted() { [[ -n "$(git --no-optional-locks status --porcelain -- config tools 2>/dev/null)" ]]; }
START_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo unknown)
START_DIRTY=0
uncommitted && START_DIRTY=1
# The build runs privileged as root and writes build/ and output/ as root: they go back to the person who started it
# – also with "sudo ./build_iso.sh" (id -u is 0 then; up to 1.0.5 output/repo stayed root's and
# "./tools/release.sh sign" failed, #71)
OWNER="${SUDO_UID:-$(id -u)}:${SUDO_GID:-$(id -g)}"
case "${1:-}" in
    "")            CONFIG_ONLY=0; CONTAINER_CMD="${CONTAINER_CMD:-sudo podman}"; RUN_OPTS=(--privileged) ;;
    --config-only) CONFIG_ONLY=1; CONTAINER_CMD="${CONTAINER_CMD:-podman}";      RUN_OPTS=() ;;
    *) echo "Usage: $0 [--config-only]" >&2; exit 2 ;;
esac

$CONTAINER_CMD build -t "$IMAGE" -f Containerfile .
mkdir -p build output
# The privileged build writes into build/ and output/ as root. Always give them back – also if the build
# fails (set -e): otherwise the directories belong to root and the next call (also --config-only, which
# runs rootless) aborts with "operation not permitted".
if [[ $CONFIG_ONLY == 0 ]]; then
    trap 'sudo chown -R "$OWNER" build output 2>/dev/null || true' EXIT
fi

# A fresh copy of the source configuration; lb clean --purge also removes the stage marker .build/config,
# so lb config (tools/lb_config.sh) must run after it and right before lb build.
# Python bytecode (__pycache__, *.pyc from local syntax checks) does not belong in the image – cp -a would take it along.
PREPARE='rm -rf config && cp -a ../config config && find config -name __pycache__ -prune -exec rm -rf {} + && find config -name "*.pyc" -delete'
if [[ $CONFIG_ONLY == 1 ]]; then
    STEPS="$PREPARE && ../tools/lb_config.sh"
else
    STEPS="$PREPARE && lb clean --purge && ../tools/lb_config.sh && { lb build 2>&1 | tee build.log; exit \${PIPESTATUS[0]}; }"
fi
$CONTAINER_CMD run --rm "${RUN_OPTS[@]}" -v "$PWD":/project:Z -w /project/build "$IMAGE" bash -euc "$STEPS"

if [[ $CONFIG_ONLY == 1 ]]; then
    echo "Configuration created in $PWD/build/config"
    exit 0
fi

ISO=$(ls -t build/*.iso 2>/dev/null | head -n1 || true)
if [[ -z "$ISO" ]]; then
    echo "Error: no ISO found – see build/build.log" >&2
    exit 1
fi
sudo mv "$ISO" output/Simple-OS.iso

# For the download: checksum (only the file name in it, so "sha256sum -c" works in the download folder) and the
# package list with exact versions – it leads to the source code of every package (snapshot.debian.org, GPL).
(cd output && sha256sum Simple-OS.iso) | sudo tee output/Simple-OS.iso.sha256 >/dev/null
sudo cp build/live-image-amd64.packages output/Simple-OS.packages.txt
# Marker for tools/release.sh: this repository's simpleos package is the one in this ISO (a later --config-only
# rebuilds output/repo without the marker). Dot file: not uploaded as a release asset.
(cd output/repo && sha256sum simpleos_*_all.deb) | sudo tee output/repo/.in-iso >/dev/null
# ... and the state of the sources it was built from: dirty if config/ or tools/ were not committed at the start, are
# not now, or changed in a commit made during the build (another HEAD with only docs changed stays clean)
dirty=$START_DIRTY
uncommitted && dirty=1
if [[ $START_COMMIT == unknown ]] || ! git diff --quiet "$START_COMMIT" HEAD -- config tools 2>/dev/null; then dirty=1; fi
printf 'commit=%s\ndirty=%s\n' "$START_COMMIT" "$dirty" | sudo tee output/repo/.build-state >/dev/null

echo "Done: output/Simple-OS.iso (log: build/build.log)"
echo "  Checksum:     output/Simple-OS.iso.sha256  ($(cut -d' ' -f1 output/Simple-OS.iso.sha256))"
echo "  Package list: output/Simple-OS.packages.txt"
echo "  Updates:      output/repo (edition package + repository; release: ./tools/release.sh sign && ./tools/release.sh publish)"
