# Release tests

Tick these off before uploading a new edition (the boxes start empty for every release). Ideally record any bug you find right away with **Menu → Help → Report a
Problem** – that tests the tool at the same time.

## 0. Build

- [x] Once: `./tools/release.sh key` – creates the release signing key and puts the public key into the image.
      Back up `~/.local/share/simpleos-release/gnupg` (without it no further update can be signed). Done for 1.0.
- [ ] `./tools/release.sh version X.Y.Z` (1.0.1: done), changes committed **and pushed** – `publish` tags exactly this
      commit and refuses one that is not on GitHub.
- [ ] `./build_iso.sh` runs without errors. At the end the verify hook reports `Simple OS verify: OK` (in `build/build.log`).
- [ ] `output/` contains `Simple-OS.iso`, `Simple-OS.iso.sha256`, `Simple-OS.packages.txt` and `repo/`
      (`simpleos_<version>_all.deb`, `Packages`, `Release`). The version is the one in `usr/lib/os-release`
      (the build stops if os-release and the installer's branding name different versions).
- [ ] `cd output && sha256sum -c Simple-OS.iso.sha256` reports `Simple-OS.iso: OK`.

## 1. In the VM (no extra hardware)

`./test_vm.sh` boots the ISO, `./test_installed_vm.sh` then boots the installed system, each in the same mode.

| Mode | Command | What to check |
|---|---|---|
| BIOS | `./test_vm.sh` | the boot menu shows Simple OS (no Debian helmet), installation, restart from the disk |
| UEFI + Secure Boot | `./test_vm.sh --secureboot` | as above, **and** after the installation in a terminal: `mokutil --sb-state` → `SecureBoot enabled` |
| UEFI + encryption | `./test_vm.sh --uefi` | tick "Encrypt system" in the installer. After the restart the system asks for the password and then starts normally |

- [ ] The installer's welcome page and slideshow show the new version ("Simple OS 1.0.1").

Last results: 1.0 is installed and in daily use on the ThinkBook (UEFI).

## 2. On real hardware

- [ ] **ThinkBook (UEFI):** install, then:
  - The firewall in Control Center → System → Security is on.
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
- [ ] **NVIDIA computer:** Control Center → System → Hardware & Drivers suggests the driver. Install it with Secure Boot
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

## 6. What changed in 1.0.1

Before publishing, the edition package can be tested on a VM installed from the **1.0** ISO: copy
`output/repo/simpleos_1.0.1_all.deb` into the VM and install it with `sudo apt install ./simpleos_1.0.1_all.deb`
(after publishing: through Software Updates, see section 5).

- [ ] **Office menu after an update from 1.0:** in the 1.0 VM run the Setup Wizard and pick LibreOffice first.
      After the update: `sudo dpkg --verify simpleos` does **not** list `/etc/skel/.config/openbox/menu.xml`,
      `/var/log/simpleos-edition.log` says `migration 010-skel-office-menu done`. Sign out and in: Menu → Apps shows
      LibreOffice Writer, Calc, Impress and Draw once each, with icons.
- [ ] **Office menu follows the Software Center:** install ONLYOFFICE in the Software Center → Menu → Apps shows
      "ONLYOFFICE" right away. Remove it again → the entry is gone.
- [ ] **New account:** create a second user (`sudo adduser test`), sign in as test: the Apps menu shows the installed
      office apps as well.
- [ ] **Regular update checks:** after signing in, `pgrep -af 'simpleos-update --watch'` shows exactly one process;
      sign out and back in → still exactly one. Put the laptop to sleep for a night: in the morning a pending
      update shows up as a notification about 2 minutes after waking up.
- [ ] **App updates:** when `flatpak remote-ls --updates --system` lists an app, Software Updates lists it as
      "<name> (app)" – also if there is no Debian update – and Install now updates it.
- [ ] **NVIDIA Kepler** (only if such a computer is available): driver 470 from Hardware & Drivers, then the Setup
      Wizard with Ultimate Gaming installs without errors, `dpkg -l nvidia-tesla-470-driver-libs:i386` shows it
      installed, Steam starts.
