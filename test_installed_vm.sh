#!/usr/bin/env bash
# Startet das installierte Simple OS direkt von der virtuellen Festplatte (ohne ISO).
set -euo pipefail
cd "$(dirname "$0")"

DISK=./output/disk.qcow2

if [[ ! -f "$DISK" ]]; then
    echo "Keine Festplatte gefunden – zuerst mit ./test_vm.sh installieren." >&2
    exit 1
fi

# Absolutes Zeigegerät: Gast-Cursor folgt dem Host-Cursor ohne Versatz/Lag (statt relativer PS/2-Maus)
INPUT=(-device qemu-xhci -device usb-tablet)

# Soundkarte (über PipeWire des Hosts), sonst haben die Lautstärketasten nichts zu steuern
AUDIO=(-audiodev pipewire,id=snd0 -device intel-hda -device hda-duplex,audiodev=snd0)

# SPICE-Agent-Kanal (QEMU-intern): gemeinsame Zwischenablage. Maus bewusst aus -> Zeiger nur über das USB-Tablet
VDAGENT=(-device virtio-serial-pci
    -chardev qemu-vdagent,id=vdagent,name=vdagent,clipboard=on,mouse=off
    -device virtserialport,chardev=vdagent,name=com.redhat.spice.0)

qemu-system-x86_64 -m 4096 -smp 4 -enable-kvm -cpu host -vga virtio \
    -display gtk,grab-on-hover=on \
    "${INPUT[@]}" \
    "${AUDIO[@]}" \
    "${VDAGENT[@]}" \
    -drive file="$DISK",format=qcow2
