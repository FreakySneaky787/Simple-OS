#!/usr/bin/env bash
# Simple OS – automatic boot test of the ISO in QEMU (#124). Run after ./build_iso.sh, before sign/publish:
#   ./tools/qemu-test.sh [ISO] [--bios | --uefi]     default: output/Simple-OS.iso, BIOS and UEFI one after the other
# Each run starts the ISO headless (no window), presses Enter in the boot menu like a person would (the menus wait
# without a countdown) and waits for the live session's report on the serial port (simpleos-boot-test.service, only
# active in QEMU/KVM): the desktop runs (Openbox, taskbar, desktop icons) and no system service failed.
# Pass = "desktop" within the time limit and "done failed=0". A screenshot of the desktop is kept either way.
# Output: output/qemu-test/<mode>.{serial,png,log} and output/.qemu-test (ISO checksum, commit, result per mode);
# tools/release.sh publish refuses an ISO without a passed test of both modes.
# Not a replacement for TESTING.md: real hardware, installing, dual boot, languages and sleep stay manual.
# Needs: qemu-system-x86_64 (KVM if /dev/kvm can be used), python3; for UEFI the OVMF firmware (edk2-ovmf / ovmf);
# python3-pil (Pillow) only for PNG screenshots (otherwise PPM).
# Environment: QEMU_TEST_TIMEOUT (seconds per mode, default 420), QEMU_TEST_MEM (MiB, default 4096).
set -euo pipefail
cd "$(dirname "$0")/.."

ISO=output/Simple-OS.iso
MODES=(bios uefi)
for a in "$@"; do
    case "$a" in
        --bios) MODES=(bios) ;;
        --uefi) MODES=(uefi) ;;
        -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
        -*) echo "qemu-test: unknown option $a" >&2; exit 2 ;;
        *) ISO=$a ;;
    esac
done
TIMEOUT=${QEMU_TEST_TIMEOUT:-420}
MEM=${QEMU_TEST_MEM:-4096}
OUT=output/qemu-test
[ -f "$ISO" ] || { echo "qemu-test: $ISO missing – ./build_iso.sh first" >&2; exit 2; }
command -v qemu-system-x86_64 >/dev/null || { echo "qemu-test: qemu-system-x86_64 missing (package qemu-system-x86)" >&2; exit 2; }
mkdir -p "$OUT"
ACCEL=(-machine q35)
if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then ACCEL=(-machine q35,accel=kvm -cpu host); else
    echo "qemu-test: no KVM – this will be very slow" >&2; TIMEOUT=$((TIMEOUT * 4)); fi

ovmf() {   # first existing OVMF code + vars pair (Fedora, Debian/Ubuntu, Arch)
    local c v
    for c in /usr/share/edk2/ovmf/OVMF_CODE.fd /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd \
             /usr/share/edk2/x64/OVMF_CODE.4m.fd /usr/share/edk2-ovmf/x64/OVMF_CODE.fd; do
        [ -f "$c" ] || continue
        v=${c/CODE/VARS}
        [ -f "$v" ] && { echo "$c $v"; return 0; }
    done
    return 1
}

# HMP monitor: one command, its output
hmp() {
    python3 - "$1" "$2" <<'PY'
import socket, sys, time
s = socket.socket(socket.AF_UNIX)
s.connect(sys.argv[1]); s.settimeout(3)
time.sleep(0.1)
try:
    s.recv(65536)
except socket.timeout:
    pass
s.sendall((sys.argv[2] + "\n").encode())
time.sleep(0.4)
try:
    print(s.recv(65536).decode(errors="replace"))
except socket.timeout:
    pass
s.close()
PY
}
# Screenshot -> file (PNG with Pillow, else PPM); prints the file name
shot() {
    local mon=$1 base=$2
    rm -f "$base.ppm"
    hmp "$mon" "screendump $base.ppm" >/dev/null
    for _ in 1 2 3 4 5 6 7 8 9 10; do [ -s "$base.ppm" ] && break; sleep 0.3; done
    [ -s "$base.ppm" ] || return 1
    sleep 0.3
    if python3 -c "from PIL import Image; Image.open('$base.ppm').save('$base.png')" 2>/dev/null; then
        rm -f "$base.ppm"; echo "$base.png"
    else
        echo "$base.ppm"
    fi
}
# Fingerprint of the screen (to see whether it is still / no longer the boot menu)
screen_sum() {
    local f
    f=$(shot "$1" "$2") || { echo none; return; }
    sha256sum "$f" | cut -c1-16
}

run_mode() {
    local mode=$1 dir serial mon log vars pid start sum prev tries=0 result=fail
    dir=$(mktemp -d)
    serial=$OUT/$mode.serial; mon=$dir/mon; log=$OUT/$mode.log
    : > "$serial"; : > "$log"
    local args=(-name "simpleos-qemu-test-$mode" "${ACCEL[@]}" -smp 2 -m "$MEM" -display none -vga std
                -monitor "unix:$mon,server,nowait" -serial "file:$serial" -cdrom "$ISO" -boot d
                -netdev user,id=n0 -device e1000,netdev=n0 -no-reboot)
    if [ "$mode" = uefi ]; then
        local fw
        fw=$(ovmf) || { echo "qemu-test: OVMF firmware missing (package edk2-ovmf / ovmf) – UEFI not tested" | tee -a "$log" >&2; rm -rf "$dir"; return 1; }
        vars=$dir/vars.fd; cp "${fw#* }" "$vars"
        args+=(-drive "if=pflash,format=raw,readonly=on,file=${fw%% *}" -drive "if=pflash,format=raw,file=$vars")
    fi
    qemu-system-x86_64 "${args[@]}" >>"$log" 2>&1 &
    pid=$!
    start=$(date +%s)
    for _ in $(seq 50); do [ -S "$mon" ] && break; sleep 0.2; done

    # Boot menu: wait until the screen stands still (menu drawn), press Enter; again if nothing changed (max 3 times)
    prev=
    while [ $(( $(date +%s) - start )) -lt 60 ]; do
        sleep 2
        sum=$(screen_sum "$mon" "$dir/menu")
        if [ -n "$prev" ] && [ "$sum" = "$prev" ] && [ "$sum" != none ]; then
            hmp "$mon" "sendkey ret" >/dev/null; tries=$((tries + 1))
            echo "boot menu: Enter ($tries)" >> "$log"
            sleep 3
            [ "$(screen_sum "$mon" "$dir/menu")" != "$sum" ] && break
            [ "$tries" -ge 3 ] && break
        fi
        prev=$sum
    done

    # The live session's report
    while kill -0 "$pid" 2>/dev/null && [ $(( $(date +%s) - start )) -lt "$TIMEOUT" ]; do
        grep -qa 'SIMPLEOS-BOOT-TEST: done\|SIMPLEOS-BOOT-TEST: timeout' "$serial" && break
        sleep 3
    done
    shot "$mon" "$OUT/$mode" >/dev/null || true
    hmp "$mon" "quit" >/dev/null 2>&1 || true
    sleep 1; kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
    rm -rf "$dir"

    local secs=$(( $(date +%s) - start ))
    if grep -qa 'SIMPLEOS-BOOT-TEST: done failed=0' "$serial"; then
        result=pass
        echo "qemu-test $mode: PASS – $(grep -a 'SIMPLEOS-BOOT-TEST: desktop' "$serial" | tr -d '\r' | sed 's/.*desktop /desktop: Simple OS /;s/ \([0-9]*\)$/ after \1 s/'), $(grep -a 'SIMPLEOS-BOOT-TEST: state' "$serial" | tr -d '\r' | sed 's/.*: //') (${secs} s in total)"
    else
        echo "qemu-test $mode: FAIL after ${secs} s" >&2
        if grep -qa 'SIMPLEOS-BOOT-TEST' "$serial"; then
            grep -a 'SIMPLEOS-BOOT-TEST' "$serial" | tr -d '\r' | sed 's/^/    /' >&2
        else
            echo "    no report from the live session (boot menu, kernel, LightDM or the desktop did not start)" >&2
        fi
        echo "    screenshot: $(ls "$OUT/$mode".png "$OUT/$mode".ppm 2>/dev/null | head -n 1), log: $log" >&2
    fi
    RESULTS+=("$mode=$result")
    [ "$result" = pass ]
}

RESULTS=()
rc=0
for m in "${MODES[@]}"; do run_mode "$m" || rc=1; done

iso_sum=$(sha256sum "$ISO" | cut -d' ' -f1)
commit=$(sed -n 's/^commit=//p' output/repo/.build-state 2>/dev/null || true)
# The other mode's result of the same ISO stays: "--bios", then "--uefi" = both passed (release.sh needs both, #175)
kept=()
if [ "$(sed -n 's/^iso=//p' output/.qemu-test 2>/dev/null)" = "$iso_sum" ]; then
    for m in bios uefi; do
        case " ${MODES[*]} " in *" $m "*) continue ;; esac
        line=$(grep -x "$m=.*" output/.qemu-test 2>/dev/null || true)
        [ -n "$line" ] && kept+=("$line")
    done
fi
{
    echo "iso=$iso_sum"
    echo "commit=${commit:-unknown}"
    echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    for r in "${kept[@]}" "${RESULTS[@]}"; do echo "$r"; done
} > output/.qemu-test
[ "$rc" = 0 ] && echo "qemu-test: all passed (output/.qemu-test)" || echo "qemu-test: FAILED – see above" >&2
exit "$rc"
