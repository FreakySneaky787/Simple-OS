#!/usr/bin/env bash
# Test Simple OS in QEMU.
#   ./test_vm.sh [--uefi | --secureboot] [--installed]
#     (none)         classic BIOS (SeaBIOS)                              disk output/disk.qcow2
#     --uefi         UEFI without Secure Boot (OVMF)                     disk output/disk-uefi.qcow2
#     --secureboot   UEFI with Secure Boot and the Microsoft keys like on a laptop you buy
#                                                                        disk output/disk-secureboot.qcow2
#     --installed    boot the installed system from the disk (without the ISO)
# UEFI: the NVRAM (boot entries, Secure Boot keys) is stored per mode in output/ovmf-vars-<mode>.fd and is kept
# between installation and restart – like on real hardware. To start over: delete the disk and the vars file.
# UEFI needs the package edk2-ovmf (Fedora).
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
        *) echo "Usage: $0 [--uefi | --secureboot] [--installed]" >&2; exit 2 ;;
    esac
done

case "$mode" in
    bios) DISK=./output/disk.qcow2 ;;
    *)    DISK=./output/disk-$mode.qcow2 ;;
esac

if [[ $installed == 1 ]]; then
    if [[ ! -f "$DISK" ]]; then
        flag=; [[ $mode != bios ]] && flag=" --$mode"
        echo "No disk for this mode – install first: $0$flag" >&2
        exit 1
    fi
    BOOT=()
else
    if [[ ! -f "$ISO" ]]; then
        echo "No ISO found – run ./build_iso.sh first." >&2
        exit 1
    fi
    # Create the virtual target disk for the installer
    if [[ ! -f "$DISK" ]]; then
        echo "Creating $DISK (20G) ..."
        qemu-img create -f qcow2 "$DISK" 20G
    fi
    BOOT=(-boot d -cdrom "$ISO")
fi

# Firmware: BIOS = QEMU default; UEFI = OVMF with its own writable NVRAM copy per mode.
# Secure Boot needs the q35 chipset with SMM, otherwise the system could bypass the keys (OVMF then refuses).
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
        echo "UEFI firmware missing ($CODE) – install it with: sudo dnf install edk2-ovmf" >&2
        exit 1
    fi
    VARS=./output/ovmf-vars-$mode.fd
    [[ -f "$VARS" ]] || cp "$VARS_TEMPLATE" "$VARS"
    FIRMWARE+=(-drive if=pflash,format=raw,unit=0,readonly=on,file="$CODE"
               -drive if=pflash,format=raw,unit=1,file="$VARS")
fi

# Absolute pointing device: the guest cursor follows the host cursor without offset/lag (instead of a relative PS/2 mouse)
INPUT=(-device qemu-xhci -device usb-tablet)

# Sound card (via the host's PipeWire), otherwise the volume keys have nothing to control
AUDIO=(-audiodev pipewire,id=snd0 -device intel-hda -device hda-duplex,audiodev=snd0)

# SPICE agent channel (QEMU internal): shared clipboard. Mouse deliberately off -> pointer only via the USB tablet
VDAGENT=(-device virtio-serial-pci
    -chardev qemu-vdagent,id=vdagent,name=vdagent,clipboard=on,mouse=off
    -device virtserialport,chardev=vdagent,name=com.redhat.spice.0)

echo "Mode: $mode$([[ $installed == 1 ]] && echo ' (installed system)') – disk $DISK"
qemu-system-x86_64 -m 4096 -smp 4 -enable-kvm -cpu host -vga virtio \
    "${FIRMWARE[@]}" \
    -display gtk,grab-on-hover=on \
    "${INPUT[@]}" \
    "${AUDIO[@]}" \
    "${VDAGENT[@]}" \
    "${BOOT[@]}" \
    -drive file="$DISK",format=qcow2
