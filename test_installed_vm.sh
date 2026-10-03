#!/usr/bin/env bash
# Startet das installierte Simple OS direkt von der virtuellen Festplatte (ohne ISO).
#   ./test_installed_vm.sh [--uefi | --secureboot]   – Kurzform für ./test_vm.sh --installed …
exec "$(dirname "$0")/test_vm.sh" --installed "$@"
