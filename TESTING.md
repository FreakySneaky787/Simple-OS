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
      (the build stops if os-release and the installer's branding name different versions); inside the package it
      carries the build time, `X.Y.Z+YYYYMMDDHHMMSS` (since 1.1, #102), so a system installed from an earlier test build
      of the same version is offered the published build.
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

- [ ] The installer's welcome page and slideshow show the new version ("Simple OS 1.0.3").

Last results: 1.0 is installed and in daily use on the ThinkPad E16 (UEFI).

## 2. On real hardware

- [ ] **ThinkPad E16 (UEFI):** install, then:
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

## 6. What changed in 1.1.1

Before publishing (Sunday 2026-11-08), with the new ISO (#114: every release has one):

- [ ] **Slow clicks (issue #104)** – the table of the issue, on the ThinkPad E16 with the **touchpad** (firm click) and
      a **mouse**: desktop right-click, window title bar right-click, held 0.1 / 0.3 / 0.6 / 1 s – the menu stays open
      every time; a quick click on an entry still runs it. VM (2026-11-03, `xdotool mousedown/sleep/mouseup`): desktop
      menu open at 0.1–1.3 s with `hideDelay` 1500, closed from 0.3 s with the old 200.
- [ ] **Speaker icon (#104)** – left of the network display: a click (short and held) opens the sound menu, a click
      never mutes; scroll up/down = louder/quieter with the on-screen display; middle click = mute, the icon turns grey;
      volume keys and the sound menu change the icon at once; Bluetooth headphones connected → the icon follows the new
      output. Only one speaker icon (no volumeicon in the tray). VM: sound menu open after 0.1–1.5 s holds.
- [ ] **Update 1.1 → 1.1.1** (VM installed from the 1.1 ISO, Software Updates): after signing out and in, one speaker
      icon, `grep hideDelay ~/.config/openbox/rc.xml` = 1500, no `volumeicon` in `~/.config/openbox/autostart`; an
      account with its own autostart line keeps it (migration 110). Taskbar settings (Large, top, network off) still
      apply and the right icon is in the right place.
- [ ] **Display scale 150/200 % (#115):** a notification with buttons (e.g. an update notification → right-click or
      the context key) shows its menu in the same size as the other menus.
- [ ] **Camera / Language & Region (#116):** a photo is saved as before; with `LANG=de_DE.utf8` written by hand in
      `/etc/default/locale`, changing only the formats works.
- [ ] **Window buttons (#121):** minimize/maximize/close are clear shapes (line, square, two squares when maximized,
      ×), noticeably bigger than in 1.1 and easy to hit with the touchpad; close turns red under the pointer, the others
      get a dark background. Control Center → Display → Scale 125/150/200 %: the buttons and their images grow with it
      (no tiny 6-pixel images in a big title bar). Another accent color (Appearance): images stay. Update from 1.1 with
      150 % or another accent: right after signing in the new buttons (migration 130). Container 2026-11-05 (Xvfb,
      Openbox 3.6.1): buttons 18/22/26/34 px with 10/12/15/20 px images at 100/125/150/200 %.
- [ ] **Updates in plain words (#120):** during the update 1.1 → 1.1.1 the window says "Downloading updates (n of
      m)", "Installing updates (n of m)", "Finishing up" – never a line with "Unpacking", "Setting up" or version
      numbers, and the bar does not jump back. `~/.cache/simpleos-update.log` has a section "apt/dpkg output".
      Pull the network cable during the download: the notification still names the reason (internet).
- [ ] **Restore point (#119):** Backup → "Restore point before updates" on, no restore point yet, then the update:
      while Timeshift prepares, the bar glides (no "0%", no "???"), the line below says "Copying system files · n
      files" and counts up, the hint says "This can take 10–20 minutes"; after 3 minutes "Still working, this is
      normal". Once Timeshift reports a percentage the normal bar with "… left" takes over.
- [ ] **Store icons (#117):** Menu/search (Super): Software Center (grid), Software Store (shop front), GNOME Software
      (bag) – three different icons, in dark and light mode. Open the Software Store once (Bazaar installed): the menu
      and the search show no separate "Bazaar" entry; `~/.local/share/applications/io.github.kolunmi.Bazaar.desktop`
      has `NoDisplay=true`. Update from 1.1 with Bazaar already installed: the "Bazaar" entry is gone after signing in
      (migration 120).
- [ ] **Fresh install from the 1.1.1 ISO** (BIOS + UEFI) – the usual checks of sections 0–3.
