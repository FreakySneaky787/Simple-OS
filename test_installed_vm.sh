#!/usr/bin/env bash
# Boots the installed Simple OS directly from the virtual disk (without the ISO).
#   ./test_installed_vm.sh [--uefi | --secureboot]   – short form of ./test_vm.sh --installed …
exec "$(dirname "$0")/test_vm.sh" --installed "$@"
