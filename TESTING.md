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

## 6. What changed in 1.1 (work in progress)

Faster start and installation, Language & Region, Camera, display scaling, USB notifications, package versions of test
builds.

**Update 1.0.7 → 1.1 (VM 2026-10-30, package from `next` f693877 through a local repository):** Software Updates'
helper rc 0 in 40 s; simpleos 1.1+…, the new packages (GStreamer for the camera, zstd) came along; `dpkg --audit` clean;
migration 100 rebuilt the initramfs (17 MB, `MODULES=dep`) and the system restarted with it; "What's new in Simple OS 1.1"
appeared; no failed units; tint2rc (scale line) and the Openbox menu (Camera) merged into the account; greeter-wrapper,
Xsession step and the Rofi wrapper in place; Language & Region and the camera app (no camera) open.

- [ ] **Small initramfs (issue #47):** fresh installation (BIOS and UEFI, once with LUKS):
      `cat /etc/initramfs-tools/conf.d/simpleos-modules.conf` ends with `MODULES=dep`, `ls -la /boot/initrd.img-*` is
      about 17–40 MB (was ~160 MB), `systemd-analyze` kernel time lower than before; with LUKS the password can be typed
      on the laptop keyboard and on a USB keyboard. In the live session before restarting,
      `sudo cat /root/.cache/calamares/session.log` (Calamares runs as root) has "initramfs-dep: test build with MODULES=dep: … MB". The live ISO still boots on other hardware (its initramfs
      keeps MODULES=most). Update from 1.0.7: migration 100 rebuilds it the same way (`sudo cat
      /var/log/simpleos-edition.log`). VM 2026-10-29: 160 → 17 MB, kernel phase 2.1 → 1.1 s; the disk moved from AHCI to
      NVMe still boots (with plain `dep` it stopped at the initramfs shell); Calamares-like chroot from the live ISO: test
      build OK, the initramfs job took 5 s. ISO from `next` 59c59f0 (2026-10-31), VM UEFI, Calamares "Erase disk":
      `MODULES=dep`, initramfs 15.6 MB, boot 1.1 s kernel + 1.7 s userspace, no failed units. Open: BIOS, LUKS, real
      hardware; the session.log in the live session had only its start line, so the "test build" line was not seen.
      VM BIOS + "Encrypt system" 2026-10-31: GRUB asks for the passphrase, the initramfs opens root and swap with the
      key file, initramfs 16 MB with dm-crypt and the USB keyboard drivers, `MODULES=dep`. Found (not from #47, older):
      every start waited ~30 s – the kernel line has `resume=` on the encrypted swap, but the initramfs is built in the
      installer's chroot where the swap is not open, so it was left out (a rebuild in the installed system, e.g. at the
      first kernel update, healed it). bootloader-config now gives the swap the crypttab option `initramfs`: chroot
      build in the VM → 9.6 s. ISO e4a665bd (2026-10-31), VM BIOS + "Encrypt system": first start 9.9 s (kernel),
      swap line with `initramfs` in /etc/crypttab, swap and zram active, no failed units.
- [x] **zstd squashfs (issue #19):** `build/build.log` says `zstd compressed`; the ISO stays below 2 GiB (`publish`
      refuses otherwise; expected ~1.71 GB); the live session starts and installs (time it against 1.0.7 on the same
      machine). Measured on the 1.0.7 squashfs: xz 1432 MB / 5.6 s to unpack, zstd-19 1514 MB / 2.8 s.
      ISO 2026-10-31: 1.66 GB, `unsquashfs -s` = zstd level 19, verify hook OK, live session up in 4.9 s, installed in a VM.
- [x] **zstd in the image:** `update-initramfs -u` no longer prints "No zstd … using gzip" (VM 2026-10-31).
- [ ] **USB notifications (issue #100):** a computer with a second internal disk that has its own EFI partition
      (Windows/another Linux): opening Software Updates or the Software Center shows no "USB drive is ready". A USB
      stick still shows it, and "Safely remove" still works.
- [ ] **Test builds (issue #102):** `dpkg-query -W simpleos` shows `1.1+<build time>`; Software Updates shows
      "Simple OS 1.1" (no number after it). A machine installed from an earlier test build is offered the published
      build.
- [x] **Language & Region (issue #42):** Control Center → Language & Region shows the language the installer set.
      Change it to another language (e.g. German → Switzerland): password dialog, progress window "Changing the
      language", then "Sign out now?". After signing out and back in: Firefox, Thunar and the menus are in the new
      language, the taskbar clock and the login screen clock use its date order, `locale` shows `LANG=de_CH.UTF-8`, and
      online the spell checking/Firefox language packs are installed (`dpkg -l 'hunspell-*' 'firefox-esr-l10n-*'`).
      Formats → another region (e.g. English language, formats Germany): the example line on the page shows
      "Donnerstag, 29. Oktober 2026 · 1.234,56 · 1.234,50 €" after the change, apps stay English. Cancel the password
      dialog: nothing changes. Without internet: the language changes, the packs come with the next Software Update.
      ThinkPad E16 2026-10-31 (live session, German → Switzerland): OK; Control Center itself stays English (#43, 1.2).
- [x] **Camera (issue #44):** Menu → Apps → Camera on the ThinkPad E16: the webcam picture appears within a few
      seconds, moves smoothly (not 5 frames a second), mirrored like a mirror (raise your right hand – it is on the
      right). Take Photo (or Space): white flash, "Saved to Pictures/Camera: Photo …"; the photo opens in the image
      viewer, is sharp and NOT mirrored (text readable). Open Folder shows Pictures/Camera. Camera switch/F-key off or
      lens covered by the privacy slider: what does it show? (No camera found / black picture.) Open the camera in
      Firefox (e.g. a video call test page) and then the Camera app: "The camera is in use", close the tab, Try Again
      → picture. A USB webcam plugged in while the window is open appears in the title bar choice. VM 2026-10-29
      with the virtual test camera (vivid): all of this except the hardware switch and unplugging. ThinkPad E16
      2026-10-31 (live session, ISO from `next` 59c59f0): OK.
- [x] **Display scaling (issue #41):** on the ThinkPad E16 (16" 1920x1200, ~141 dpi) Control Center → Display → Scale
      says "Automatic (100 %)" and everything looks exactly as in 1.0.7. Choose 150 %: at once the taskbar, the start
      menu (Super), flyouts (Wi-Fi, Sound, Power – still right above the taskbar), notifications, window titles, the
      right-click menu, the mouse pointer and the Control Center itself are bigger; Firefox and the Terminal after
      reopening them. Sign out and in: still 150 %. Back to 100 %: like before. 200 %: GTK windows (Control Center,
      Thunar, Firefox) twice as big and sharp, not blurry. With a 2.8K/4K laptop or a 4K monitor as the main screen:
      "Automatic" shows 150/200 % and is used from the first sign-in, the login and lock screen are bigger too.
      Lowered resolution on such a screen: Automatic follows the resolution in use. Live ISO on a HiDPI laptop: the
      installer is readable. VM 2026-10-29 (2880x1800): 200/150/100 % live and after signing in again, login/lock screen
      at 200 % (password field, icons) with a faked automatic value; the automatic value itself with mocked xrandr
      (2.8K 200 %, 16" 2560x1600 150 %, Full HD 100 %, 27" 4K 100 %, TV 160x90 mm 100 %, turned screen).
      Taskbar size "Large" (Control Center → Appearance → Taskbar → Layout): higher bar, bigger clock and texts, the
      Wi-Fi/Sound/Power flyouts still just above it; "Full" again looks as before. ThinkPad E16 2026-10-31 (live
      session): Automatic 100 %, 150 %, 200 % and Large taskbar OK. Still open: a real 2.8K/4K screen.
