#!/usr/bin/env bash
# Simple OS – ISO bauen.
#   ./build_iso.sh                 ISO bauen -> output/Simple-OS.iso (privilegierter Container, braucht sudo)
#   ./build_iso.sh --config-only   nur die live-build-Konfiguration in build/config erzeugen (ohne sudo, zum Prüfen)
#
# Quelle ist config/ (wird nie verändert). Gebaut wird in build/: dort landen die frisch kopierte
# Konfiguration, alle live-build-Zwischenstände und build.log.
set -euo pipefail
cd "$(dirname "$0")"

IMAGE="simple-os-builder"
case "${1:-}" in
    "")            CONFIG_ONLY=0; CONTAINER_CMD="${CONTAINER_CMD:-sudo podman}"; RUN_OPTS=(--privileged) ;;
    --config-only) CONFIG_ONLY=1; CONTAINER_CMD="${CONTAINER_CMD:-podman}";      RUN_OPTS=() ;;
    *) echo "Aufruf: $0 [--config-only]" >&2; exit 2 ;;
esac

$CONTAINER_CMD build -t "$IMAGE" -f Containerfile .
mkdir -p build output
# Der privilegierte Build schreibt als root in build/ und output/. Immer zurückgeben – auch wenn der Build
# scheitert (set -e): sonst gehören die Verzeichnisse root und der nächste Aufruf (auch --config-only, der
# rootless läuft) bricht mit "operation not permitted" ab.
if [[ $CONFIG_ONLY == 0 ]]; then
    trap 'sudo chown -R "$(id -u):$(id -g)" build output 2>/dev/null || true' EXIT
fi

# Frische Kopie der Quell-Konfiguration; lb clean --purge entfernt auch den Stage-Marker .build/config,
# daher muss lb config (tools/lb_config.sh) danach und direkt vor lb build laufen.
# Python-Bytecode (__pycache__, *.pyc von lokalen Syntaxprüfungen) gehört nicht ins Image – cp -a nähme ihn mit.
PREPARE='rm -rf config && cp -a ../config config && find config -name __pycache__ -prune -exec rm -rf {} + && find config -name "*.pyc" -delete'
if [[ $CONFIG_ONLY == 1 ]]; then
    STEPS="$PREPARE && ../tools/lb_config.sh"
else
    STEPS="$PREPARE && lb clean --purge && ../tools/lb_config.sh && { lb build 2>&1 | tee build.log; exit \${PIPESTATUS[0]}; }"
fi
$CONTAINER_CMD run --rm "${RUN_OPTS[@]}" -v "$PWD":/project:Z -w /project/build "$IMAGE" bash -euc "$STEPS"

if [[ $CONFIG_ONLY == 1 ]]; then
    echo "Konfiguration erstellt in $PWD/build/config"
    exit 0
fi

ISO=$(ls -t build/*.iso 2>/dev/null | head -n1 || true)
if [[ -z "$ISO" ]]; then
    echo "Fehler: Keine ISO gefunden – siehe build/build.log" >&2
    exit 1
fi
sudo mv "$ISO" output/Simple-OS.iso

# Für den Download: Prüfsumme (nur der Dateiname drin, damit "sha256sum -c" im Download-Ordner klappt) und die
# Paketliste mit genauen Versionen – darüber findet man den Quellcode jedes Pakets (snapshot.debian.org, GPL).
(cd output && sha256sum Simple-OS.iso) | sudo tee output/Simple-OS.iso.sha256 >/dev/null
sudo cp build/live-image-amd64.packages output/Simple-OS.packages.txt

echo "Fertig: output/Simple-OS.iso (Log: build/build.log)"
echo "  Prüfsumme:  output/Simple-OS.iso.sha256  ($(cut -d' ' -f1 output/Simple-OS.iso.sha256))"
echo "  Paketliste: output/Simple-OS.packages.txt"
