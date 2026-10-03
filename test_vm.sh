#!/usr/bin/env bash
# Simple OS in QEMU testen.
#   ./test_vm.sh [--uefi | --secureboot] [--installed]
#     (ohne)         klassisches BIOS (SeaBIOS)                          Platte output/disk.qcow2
#     --uefi         UEFI ohne Secure Boot (OVMF)                        Platte output/disk-uefi.qcow2
#     --secureboot   UEFI mit Secure Boot und den Microsoft-Schlüsseln wie bei einem gekauften Laptop
#                                                                        Platte output/disk-secureboot.qcow2
#     --installed    das installierte System von der Platte starten (ohne ISO)
# UEFI: Der NVRAM (Booteinträge, Secure-Boot-Schlüssel) liegt je Modus in output/ovmf-vars-<modus>.fd und bleibt
# zwischen Installation und Neustart erhalten – wie auf echter Hardware. Neu anfangen: Platte und vars-Datei löschen.
# Braucht für UEFI das Paket edk2-ovmf (Fedora).
set -euo pipefail
cd "$(dirname "$0")"

ISO=./output/Simple-OS.iso
OVMF=/usr/share/edk2/ovmf
mode=bios installed=0
for a in "$@"; do
    case "$a" in
        --uefi) mode=uefi ;;
        --secureboot) mode=secureboot ;;
        --installed) installed=1 ;;
        *) echo "Aufruf: $0 [--uefi | --secureboot] [--installed]" >&2; exit 2 ;;
    esac
done

case "$mode" in
    bios) DISK=./output/disk.qcow2 ;;
    *)    DISK=./output/disk-$mode.qcow2 ;;
esac

if [[ $installed == 1 ]]; then
    if [[ ! -f "$DISK" ]]; then
        flag=; [[ $mode != bios ]] && flag=" --$mode"
        echo "Keine Festplatte für diesen Modus – zuerst installieren: $0$flag" >&2
        exit 1
    fi
    BOOT=()
else
    if [[ ! -f "$ISO" ]]; then
        echo "Keine ISO gefunden – zuerst ./build_iso.sh ausführen." >&2
        exit 1
    fi
    # Virtuelle Zielfestplatte für den Installer anlegen
    if [[ ! -f "$DISK" ]]; then
        echo "Lege $DISK (20G) an ..."
        qemu-img create -f qcow2 "$DISK" 20G
    fi
    BOOT=(-boot d -cdrom "$ISO")
fi

# Firmware: BIOS = QEMU-Standard; UEFI = OVMF mit eigener, beschreibbarer NVRAM-Kopie je Modus.
# Secure Boot braucht den q35-Chipsatz mit SMM, sonst könnte das System die Schlüssel umgehen (OVMF verweigert dann).
FIRMWARE=()
if [[ $mode != bios ]]; then
    if [[ $mode == secureboot ]]; then
        CODE=$OVMF/OVMF_CODE.secboot.fd VARS_TEMPLATE=$OVMF/OVMF_VARS.secboot.fd
        FIRMWARE=(-machine q35,smm=on -global driver=cfi.pflash01,property=secure,value=on)
    else
        CODE=$OVMF/OVMF_CODE.fd VARS_TEMPLATE=$OVMF/OVMF_VARS.fd
        FIRMWARE=(-machine q35)
    fi
    if [[ ! -f "$CODE" || ! -f "$VARS_TEMPLATE" ]]; then
        echo "UEFI-Firmware fehlt ($CODE) – installieren mit: sudo dnf install edk2-ovmf" >&2
        exit 1
    fi
    VARS=./output/ovmf-vars-$mode.fd
    [[ -f "$VARS" ]] || cp "$VARS_TEMPLATE" "$VARS"
    FIRMWARE+=(-drive if=pflash,format=raw,unit=0,readonly=on,file="$CODE"
               -drive if=pflash,format=raw,unit=1,file="$VARS")
fi

# Absolutes Zeigegerät: Gast-Cursor folgt dem Host-Cursor ohne Versatz/Lag (statt relativer PS/2-Maus)
INPUT=(-device qemu-xhci -device usb-tablet)

# Soundkarte (über PipeWire des Hosts), sonst haben die Lautstärketasten nichts zu steuern
AUDIO=(-audiodev pipewire,id=snd0 -device intel-hda -device hda-duplex,audiodev=snd0)

# SPICE-Agent-Kanal (QEMU-intern): gemeinsame Zwischenablage. Maus bewusst aus -> Zeiger nur über das USB-Tablet
VDAGENT=(-device virtio-serial-pci
    -chardev qemu-vdagent,id=vdagent,name=vdagent,clipboard=on,mouse=off
    -device virtserialport,chardev=vdagent,name=com.redhat.spice.0)

echo "Modus: $mode$([[ $installed == 1 ]] && echo ' (installiertes System)') – Platte $DISK"
qemu-system-x86_64 -m 4096 -smp 4 -enable-kvm -cpu host -vga virtio \
    "${FIRMWARE[@]}" \
    -display gtk,grab-on-hover=on \
    "${INPUT[@]}" \
    "${AUDIO[@]}" \
    "${VDAGENT[@]}" \
    "${BOOT[@]}" \
    -drive file="$DISK",format=qcow2
