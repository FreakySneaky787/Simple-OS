# Release tests

Tick these off before uploading a new edition (the boxes start empty for every release). Ideally record any bug you find right away with **Menu → Help → Report a
Problem** – that tests the tool at the same time.

## 0. Build

- [x] Once: `./tools/release.sh key` – creates the release signing key and puts the public key into the image.
      Back up `~/.local/share/simpleos-release/gnupg` (without it no further update can be signed). Done for 1.0.
- [ ] `./tools/release.sh version X.Y.Z` (1.0.3: done), changes committed **and pushed** – `publish` tags exactly this
      commit and refuses one that is not on GitHub.
- [ ] `./build_iso.sh` runs without errors. At the end the verify hook reports `Simple OS verify: OK` (in `build/build.log`).
- [ ] `output/` contains `Simple-OS.iso`, `Simple-OS.iso.sha256`, `Simple-OS.packages.txt` and `repo/`
      (`simpleos_<version>_all.deb`, `Packages`, `Release`). The version is the one in `usr/lib/os-release`
      (the build stops if os-release and the installer's branding name different versions).
- [ ] `cd output && sha256sum -c Simple-OS.iso.sha256` reports `Simple-OS.iso: OK`.

## 1. In the VM (no extra hardware)

> QEMU's standard graphics (`-vga std`, bochs-drm) loses part of the picture when the screen blanks (screen saver/DPMS
> with "Lock" off, e.g. in the live session): after waking up the upper half stays black until a window changes. Not a
> Simple OS bug – with `-vga virtio` (or virt-manager's default) it does not happen (checked 2026-10-15). Test screen
> blanking with virtio graphics or on real hardware.

`./test_vm.sh` boots the ISO, `./test_installed_vm.sh` then boots the installed system, each in the same mode.

| Mode | Command | What to check |
|---|---|---|
| BIOS | `./test_vm.sh` | the boot menu shows Simple OS (no Debian helmet), installation, restart from the disk |
| UEFI + Secure Boot | `./test_vm.sh --secureboot` | as above, **and** after the installation in a terminal: `mokutil --sb-state` → `SecureBoot enabled` |
| UEFI + encryption | `./test_vm.sh --uefi` | tick "Encrypt system" in the installer. After the restart the system asks for the password and then starts normally |

- [ ] The installer's welcome page and slideshow show the new version ("Simple OS 2.0").

Last results: 1.0 is installed and in daily use on the ThinkBook (UEFI).

## 2. On real hardware

- [ ] **ThinkBook (UEFI):** install, then:
  - The firewall in Control Center → Password & Security is on.
  - Power mode offers three profiles.
  - Software Updates shows a BIOS update, if there is one.
  - Install updates: clicking the "Updates installed" notification does **not** restart right away but asks
    first ("Restart now" / "Later"). After the restart Software Updates does not offer the same updates again.
    If a BIOS update was included and it shows up again anyway, a notification says it was not applied.
    If there are problems, keep `~/.cache/simpleos-update.log`.
  - Wi-Fi: run a large download (e.g. a Flatpak). The rate must not keep dropping to a few kB/s. If it does:
    Menu → Help → Report a Problem; the "Network" section lists the driver, link rate and power saving mode
    (`Power save: off` expected).
  - Report a Problem creates a file on the desktop.
- [ ] **Secure Boot on** (enable it in the BIOS): the installed system still starts.
- [ ] **Dual boot with Windows:** choose "Install alongside" in the installer. Afterwards the GRUB menu shows Simple OS
      **and** Windows, and Windows still starts. Make a Windows backup first or use a computer where nothing can be lost.
- [ ] **NVIDIA computer:** Control Center → System & Updates → Hardware & Drivers suggests the driver. Install it with Secure Boot
      **off**, restart, then check that `glxinfo -B` shows "NVIDIA" as the renderer.
- [ ] **AMD computer:** graphics, Wi-Fi and sound work. Hardware & Drivers reports nothing missing.

## 3. Report a Problem

- [ ] Menu → Help → Report a Problem → "Create report" → enter the password.
- [ ] Open the file on the desktop and check that it does **not** contain:
  - your name, your user name, your computer name
  - your Wi-Fi name
  - your IP addresses
- [ ] The GitHub page for a new bug report opens (only once the repo is public).

## 4. Publish

1. Once (done for 1.0): a public repo **`simple-os`** under `FreakySneaky787` on GitHub. The name must match,
   because the installer and Report a Problem link to `github.com/FreakySneaky787/simple-os`.
2. `git push` – the commit the ISO was built from must be on GitHub.
3. `./tools/release.sh sign && ./tools/release.sh publish` – creates the release `v<version>` with the text of
   `RELEASE_NOTES.md`, the three ISO files and the update repository, checks it as a draft and only then makes it
   "latest" (needs `gh auth login`). From then on installed systems are offered this edition.
   `publish` refuses while the repo is private – installed systems download updates without a GitHub login.
4. On an installed system (VM): `sudo apt-get update` shows the Simple OS source without errors
   (`…/releases/latest/download ./ InRelease`), and `/etc/apt/sources.list.d/simpleos.sources` has no `Enabled: no`.

## 5. Update to a new edition (from the second release on)

- [ ] Before publishing the new version: a VM installed from the **previous** ISO. Change something by hand in
      `~/.config/openbox/rc.xml` (e.g. a comment).
- [ ] After `publish`: Software Updates lists "Simple OS <new version>" at the top → Install now → the notification
      says "Simple OS … is installed". `cat /etc/os-release` shows the new version.
- [ ] Sign out and back in: files you did not change follow the new edition, your change in `rc.xml` is still there
      (`~/.cache/simpleos-edition.log` lists "updated …" / "kept …"). New packages of the edition are installed.

## 6. What changes in 2.0 "Rigi" (Debian 13)

Draft, grows with the port on the branch `trixie` (issues #50–#53). Everything in sections 0–3 again, on the new base,
plus:

- [ ] **Build:** `./build_iso.sh` on Debian 13 (`Containerfile` from `debian:trixie`); the verify hook reports
      `Simple OS verify: OK`; no package from `bookworm` or `bookworm-backports` in `Simple-OS.packages.txt`.
- [ ] **Boot and install** in all three modes (BIOS, UEFI, UEFI + Secure Boot) and next to Windows; GRUB shows both
      systems; `mokutil --sb-state` → `SecureBoot enabled`.
- [ ] **Desktop and tools:** taskbar, menus, Control Center (every page), Setup Wizard, night light, screenshots,
      clipboard, snapping, lock screen (#88 test from 1.0.6) – all Python/GTK tools start without warnings in
      `~/.xsession-errors`.
- [ ] **Hardware:** NVIDIA with Debian 13's driver (Hardware & Drivers suggests it, `glxinfo -B` shows NVIDIA), AMD
      and Intel graphics, Wi-Fi (also Broadcom), Bluetooth incl. headphone battery, sound over HDMI/USB, sleep.
- [ ] **Software Updates and Store:** updates from Debian 13 and the Simple OS 2.x channel; Flatpak apps install and
      update.
- [ ] **Update channel:** a 1.x system with the newest 1.x update is **not** offered 2.0 as a normal update.
- [ ] **Upgrade 1.x → 2.0** (issue #52): on a VM with the newest 1.2.x and one real machine – restore point first, then the
      upgrade; afterwards `/etc/os-release` says 2.0, no `bookworm` sources left, no backports pin file, files,
      Flatpak apps, Steam and settings are kept; `dpkg --audit` clean, no failed units.
