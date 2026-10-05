#!/usr/bin/env bash
# Simple OS – build the ISO.
#   ./build_iso.sh                 build the ISO -> output/Simple-OS.iso (privileged container, needs sudo)
#   ./build_iso.sh --config-only   only generate the live-build configuration in build/config (without sudo, for checking)
#
# The source is config/ (never modified). The build happens in build/: the freshly copied
# configuration, all live-build intermediates and build.log end up there.
set -euo pipefail
cd "$(dirname "$0")"

IMAGE="simple-os-builder"
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
    trap 'sudo chown -R "$(id -u):$(id -g)" build output 2>/dev/null || true' EXIT
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

echo "Done: output/Simple-OS.iso (log: build/build.log)"
echo "  Checksum:     output/Simple-OS.iso.sha256  ($(cut -d' ' -f1 output/Simple-OS.iso.sha256))"
echo "  Package list: output/Simple-OS.packages.txt"
