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

`./test_vm.sh` boots the ISO, `./test_installed_vm.sh` then boots the installed system, each in the same mode.

| Mode | Command | What to check |
|---|---|---|
| BIOS | `./test_vm.sh` | the boot menu shows Simple OS (no Debian helmet), installation, restart from the disk |
| UEFI + Secure Boot | `./test_vm.sh --secureboot` | as above, **and** after the installation in a terminal: `mokutil --sb-state` → `SecureBoot enabled` |
| UEFI + encryption | `./test_vm.sh --uefi` | tick "Encrypt system" in the installer. After the restart the system asks for the password and then starts normally |

- [ ] The installer's welcome page and slideshow show the new version ("Simple OS 1.0.3").

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

## 7. What changed in 1.0.2

Test the edition package on a VM installed from the **1.0.1** ISO (`sudo apt install ./simpleos_1.0.2_all.deb`, or after
publishing through Software Updates), and a fresh installation from the new ISO. The packages added to the lists are
installed once by Software Updates ("Installing new Simple OS components").

- [ ] **Build:** `output/repo/.build-state` exists (`dirty=0`, the commit of the build); `publish` refuses after a later
      commit in `config/` or `tools/`, and after a build from uncommitted files.
- [ ] **Time:** `timedatectl` shows `System clock synchronized: yes` and `NTP service: active` (fresh install and update).
- [ ] **XDG autostart:** put a `.desktop` file with `Exec=kitty` in `~/.config/autostart`, sign out and in → a terminal opens.
      Nothing started twice (`pgrep -c nm-applet` = 1, no `xfce4-power-manager` without a battery); the folders in the
      home folder are unchanged (no `xdg-user-dirs-update`).
- [ ] **Keyring:** fresh install, start Chromium (Setup Wizard) → no "new keyring" window; `secret-tool` is not needed:
      `busctl --user list | grep org.freedesktop.secrets` shows the service.
- [ ] **Thumbnails:** a folder with pictures in Thunar shows previews.
- [ ] **EFI partition (UEFI VM and ThinkBook):** after the installation `ls /boot/efi/EFI/BOOT` shows `BOOTX64.EFI`,
      `fbx64.efi`, `mmx64.efi`, `grubx64.efi`. In the VM: `sudo apt install --reinstall shim-signed` or a newer shim/GRUB
      updates the files in `EFI/Simple_OS` (`/var/log/simpleos-edition.log` is not involved, watch the apt output); with
      Secure Boot on the system still starts. Delete the boot entry in the firmware (or `efibootmgr -B`) → the
      computer still starts via the fallback loader and the entry is recreated.
- [ ] **Browser defaults:** in a 1.0.1 VM remove Firefox with the wizard (Chromium), update → `/etc/xdg/mimeapps.list`
      names `firefox-esr.desktop` again (log: `020-browser-defaults`), your own default (`xdg-mime query default
      x-scheme-handler/https`) is still Chromium, Super+B opens Chromium; a new account's Super+B also opens Chromium.
- [ ] **Wi-Fi:** connect to a WPA2 network with the flyout (password via Rofi), then with the Setup Wizard; while it
      connects `ps aux | grep nmcli` does not show the password; wrong password → clear message; a saved network with a
      new password connects.
- [ ] **Bluetooth pairing:** a Bluetooth keyboard and a phone via Add device… (blueman's window with the code opens);
      headphones/mice as before.
- [ ] **RTX 50** (only with such a computer, or `SIMPLEOS_HW_ROOT` test): Hardware & Drivers recommends no NVIDIA driver.
- [ ] **Control Center:** a monitor with two lines for one resolution in `xrandr` offers all rates; opening the same
      page again (right-click the Do Not Disturb icon) shows the current state; dragging the volume slider is smooth.
- [ ] **Do Not Disturb icon:** appears and disappears at once; `top` shows no process waking up every second.
- [ ] **Super+L** locks the screen; media keys control a playing video in the browser.
- [ ] **Notifications on a desktop PC:** a chat/mail message that contains "battery" or "power" is shown.
- [ ] **Night light:** on, suspend and wake up → still warm within 5 minutes.
- [ ] **After the installation:** `apt-get -s autoremove` lists nothing from Qt/KDE; `df` shows ~175 MB more free space.
- [ ] **Memory:** `sysctl vm.swappiness vm.page-cluster` → 100 / 0.
- [ ] **Video:** `vainfo` (package vainfo, optional) lists profiles on Intel/AMD; mpv with `--hwdec=auto` uses vaapi.

## 8. What changed in 1.0.3

Beginner traps (what a first-time user hits in the first hour). Test on a VM installed from the **1.0.2** ISO (update
through Software Updates, or `sudo apt install ./simpleos_1.0.3_all.deb`) and on a fresh installation.

- [ ] **Tools:** `curl --version`, `wget --version`, `unzip -v`, `zip -v`, `ssh -V` work in a terminal.
- [ ] **Audio:** `alsamixer` opens; `ls /usr/share/alsa/ucm2` is not empty; on the ThinkBook speakers *and* the microphone
      still work (Sound page lists them).
- [ ] **Fonts:** open a page in Arabic/Thai/Hindi/Chinese (e.g. the Wikipedia main page in that language) → letters, no boxes.
- [ ] **Language:** install in German (or any other language) with internet → after the first login Firefox is German,
      the Setup Wizard's LibreOffice is German with a German dictionary (`dpkg -l 'hunspell-de*' 'firefox-esr-l10n-de'`).
      Without internet during the installation: the packages arrive with the first Software Updates. English: nothing added.
- [ ] **Second monitor / projector / TV:** plug in HDMI while logged in → it lights up to the right of the laptop screen
      with a notification; Super+P → Duplicate works; unplug → the laptop screen alone, no black desktop.
      Unplug while only the external screen was on → the laptop screen comes back.
- [ ] **Mouse & Touchpad (Control Center):** natural scrolling off → two-finger scrolling reverses at once; tap to click off;
      pointer speed; the values are still there after signing out; a Bluetooth/USB mouse plugged in later gets them too.
- [ ] **Date & Time (Control Center → System):** switch "Set the time automatically" off and on (password prompt); change the
      time zone → the taskbar clock follows; "Password → Change…" opens a terminal with `passwd`.
- [ ] **Logs:** `journalctl --disk-usage` stays below ~200 MB.
- [ ] **Wi-Fi band (Control Center → Wi-Fi):** while connected a row "Wi-Fi band" shows; choose 2.4 GHz only → the connection
      restarts, `iw dev <wlan> link` shows freq 24xx; back to Automatic. (`nmcli -g 802-11-wireless.band connection show <name>`)
- [ ] **Night light (real hardware):** Control Center → Display → Night light on → the screen turns warm at once (before, nothing
      happened and `~/.cache/simpleos-nightlight.log` said "Could not connect to wayland display"); off → normal again.
- [ ] **Microphone (ThinkPad E16 Gen 3):** Sound page lists a microphone input; `pactl info` no longer shows the speaker
      monitor as the default source ("stereo-fallback" profile gone after alsa-ucm-conf).
- [ ] **VPN:** the network menu → Edit Connections → Add offers OpenVPN.

