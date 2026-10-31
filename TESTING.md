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
- [ ] **EFI partition (UEFI VM and ThinkPad E16):** after the installation `ls /boot/efi/EFI/BOOT` shows `BOOTX64.EFI`,
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
- [ ] **Audio:** `alsamixer` opens; `ls /usr/share/alsa/ucm2` is not empty; on the ThinkPad E16 speakers *and* the microphone
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
- [ ] **Date & Time (Control Center → Date & Time):** switch "Set the time automatically" off and on (password prompt); change the
      time zone → the taskbar clock follows; "Password → Change…" opens a terminal with `passwd`.
- [ ] **Logs:** `journalctl --disk-usage` stays below ~200 MB.
- [ ] **Wi-Fi band (Control Center → Wi-Fi):** while connected a row "Wi-Fi band" shows; choose 2.4 GHz only → the connection
      restarts, `iw dev <wlan> link` shows freq 24xx; back to Automatic. (`nmcli -g 802-11-wireless.band connection show <name>`)
- [ ] **Night light (real hardware):** Control Center → Display → Night light on → the screen turns warm at once (before, nothing
      happened and `~/.cache/simpleos-nightlight.log` said "Could not connect to wayland display"); off → normal again.
- [ ] **Microphone (ThinkPad E16 Gen 3):** Sound page lists a microphone input; `pactl info` no longer shows the speaker
      monitor as the default source ("stereo-fallback" profile gone after alsa-ucm-conf).
- [ ] **VPN:** the network menu → Edit Connections → Add offers OpenVPN.


## 9. What changed in 1.0.4

Screen blanking, power button, Wi-Fi country, brightness, git. Test on the ThinkPad E16 **updated from 1.0.3
through Software Updates** (or `sudo apt install ./simpleos_1.0.4_all.deb`, then sign out and in – the new autostart
lines only run at the next login) and on a PC without a battery (or a VM: there the PC path is used).

- [ ] **Turn off the screen (laptop, issue #25):** Control Center → Power → "Turn off the screen after" 1 minute (pick an
      odd value first: `simpleos-power --screen-off 1`). Do nothing: the screen goes dark after ~1 minute **on battery and
      after plugging in the charger** (before, xfce4-power-manager put its own 15/10 minutes back at every plug/unplug).
      `xfconf-query -c xfce4-power-manager -lv | grep -E 'blank|dpms'` shows the value.
- [ ] **Lock when the screen turns off:** the switch below it is on. After the time above the login screen is in front
      (password needed), and ~2 minutes later the login screen itself goes dark (any key wakes it). Switch it off →
      the screen only goes dark, no password. Super+L and the lock before sleep still work.
- [ ] **A video keeps the screen on:** set the time to 1 minute, play a video in Firefox/Chromium fullscreen for 2 minutes →
      stays on, no lock. Stop the video → it goes dark after the time. Laptop *and* a PC without a battery
      (`gdbus introspect --session -d org.freedesktop.ScreenSaver -o /org/freedesktop/ScreenSaver` answers on both).
- [x] **Power button (issue #35):** a press opens the power menu (Lock, Sleep, Restart, Shut down, Sign out); nothing
      shuts down by itself. `systemd-inhibit --list` shows "Simple OS … handle-power-key". At the login screen a press still
      shuts down as before. **If a press does nothing at all, X does not see the key – then tell me, do not publish.**
      ThinkPad E16 (2026-10-14): works when held ~1 s; a quick tap reaches neither logind nor X (`xinput test-xi2 --root`
      shows nothing, also with `intel_hid enable_5_button_array=1`) – firmware, not fixable in software.
- [ ] **Brightness slider (issue #34):** Control Center → Display → Brightness follows the slider at once and the Fn keys
      (the slider shows the new value after reopening); on a desktop PC the row is not there.
- [ ] **Wi-Fi country (issue #40):** `iw reg get` shows your country (from Date & Time → time zone) after a restart; after
      changing the time zone and a restart it follows. (Intel AX2xx chips may keep deciding themselves – note the result.)
- [ ] **git:** `git --version` works after the update (arrives with the first Software Updates).
- [ ] **Updating from 1.0.3:** Software Updates offers 1.0.4, the 1.0.3 setting "Turn off the screen after" is kept
      (e.g. 5 minutes stays 5 minutes in `xfconf-query`), nothing asks for a password besides the update.
- [ ] **Task Manager (sixth sweep):** the Memory column is fully visible (it was cut off), long names are shortened with "…".
- [ ] **Light mode:** Control Center → Appearance → Light: the Sound entry in the Control Center sidebar and other symbol icons are
      dark and readable (before: light gray on white); the Software Center list has no black frame.
- [ ] **A non-English installation (e.g. German):** `simpleos-wifi` (network menu) shows "Connected: …" and "Turn off Wi-Fi" while
      online – before, `nmcli` answered "verbunden"/"aktiviert" and the menu thought you were offline with Wi-Fi off. The Setup
      Wizard's Internet step says "Connected" too. Mute from the volume keys shows "Muted".
- [ ] **Setup Wizard, Internet step (issue #63):** `simpleos-welcome-wizard` with a cable or a known Wi-Fi → step 2 shows
      "Internet ✔" and Next goes from Welcome straight to Browser (Back as well). Without a connection (Wi-Fi off in the
      network menu first, then on again): the page shows "1. Click … 2. Type … 3. Click Connect", clicking a network with a
      password shows "Password for “name”:" with an eye button; typing the password and clicking **Next** (not Connect)
      connects and then moves on. Once online, the list is hidden behind "Use a different network".
- [ ] **Small screen (1366x768):** the Welcome window fits on the screen (it was taller than the screen).
- [ ] **App menu and search (issue #61):** text typed into the app menu (☰ / Super) and the search (Super+Space) is light
      and readable (before: dark teal on the dark field); in light mode it is dark.
- [ ] **Report a Problem:** a Bluetooth device name like `bluez_output.90_7A_…` is written as `XX:XX:XX:XX:XX:XX` in the saved file.
- [ ] **BIOS computer, GRUB updates:** on a computer or VM installed in BIOS mode (`./test_vm.sh` + `./test_installed_vm.sh`),
      after the update to 1.0.4: `sudo debconf-show grub-pc | grep install_devices` shows the disk (`/dev/disk/by-id/…` or
      `/dev/sda`), and `sudo dpkg-reconfigure -f noninteractive grub-pc` ends without "You must correct your GRUB install
      devices" and says "grub-install success". A fresh BIOS installation from a new ISO shows the same right away.
- [ ] **Installer (new ISO, issues #62/#64), in the live session:** double-click "Install Simple OS" quickly twice → one
      installer window, a notification "The installer is already open". `systemd-inhibit --list` shows "Simple OS installer"
      (shutdown, sleep, lid). Super+X → Shut down → the menu asks "The installer is still working" (Keep installing / Shut
      down anyway); "Keep installing" does nothing, "Shut down anyway" switches off within seconds. Open a partition of the
      computer's disk in the file manager, start the installer → it is closed first (with a terminal open in it: a message
      instead of the installer). Super+L in the live session: a message, no lock screen.
- [ ] **Remove the USB stick (new ISO):** at the end of an installation keep "Restart now" ticked and click Done → a window
      "Simple OS is installed – Remove the USB stick …". Pull the stick (VM: `eject -f ide1-cd0` in the QEMU monitor, or
      remove the ISO), click "Restart now" → the computer restarts within seconds and starts the new system. Once more
      **without** pulling the stick → a normal restart.
- [ ] **Install alongside on an older PC (BIOS/MBR, partition inside an extended partition):** on the Dell or in a VM
      (SeaBIOS, SATA disk with MBR: a primary NTFS partition marked active, an extended partition with an ext4 system
      and swap) choose "Install alongside" and shrink the ext4 system → the installation finishes (1.0.3: "The installer
      failed to create a partition"). Afterwards `sudo sfdisk -d /dev/sda`: the new partition sits inside the extended one,
      the NTFS partition is still "bootable"; the old system passes `sudo e2fsck -fn` and is in the GRUB menu.
- [ ] **Language (German installation):** `locale -a` lists `de_DE.utf8`, the clock in the taskbar says "Mi"/"Do",
      `sudo apt update` prints no perl locale warnings; with internet during the installation `hunspell-de-de` and
      `firefox-esr-l10n-de` are installed right away. **Updated from 1.0.3** (German): after the update `locale -a`
      lists `de_DE.utf8` (migration 040), sign out and in.
- [ ] **Keyring at the first login:** right after the installation (first session) open Chromium (or
      `secret-tool store --label=t a b` from `libsecret-tools`) → no "Choose password for new keyring" window;
      `ps -C gnome-keyring-daemon -o args=` shows `--daemonize --login`.
- [ ] **Other systems stay in the GRUB menu:** with Windows or another Linux on the disk, run
      `sudo dpkg-reconfigure -f noninteractive grub-pc` (UEFI: `grub-efi-amd64`) – what every GRUB update from Debian does –
      then `sudo grep menuentry /boot/grub/grub.cfg` still lists the other system and the output has no "os-prober will not
      be executed".
- [ ] **Date & Time:** Control Center → Date & Time → switch "Set the time automatically" off and on (password window each
      time; **Cancel** goes back without an error message), change the time zone → the taskbar clock follows at once.

## 10. What changed in 1.0.5

Menus, Control Center pages, default/startup apps, headphone battery, "What's new". Test on a machine **updated from
1.0.4 through Software Updates** (sign out and in once) and on a fresh VM install.

- [ ] **What's new (issue #65):** updated machine: about 8 s after the first sign-in after the update the window "What's
      new in Simple OS 1.0.5" opens once; the next sign-in it does not. Fresh install / new account: it never opens by
      itself. Menu → Help → What's New and Control Center → System & Updates open it any time; "Show this after updates"
      off is remembered (`~/.config/simpleos/whats-new`).
- [ ] **Right-click menu:** Apps / Settings / Tools / Help; every Settings entry opens the right Control Center page.
      Updated machine with LibreOffice/ONLYOFFICE: the office entries are still under Apps (the menu was merged, not
      kept old – `~/.cache/simpleos-edition.log` says "updated" or "merged", not "kept").
- [ ] **Control Center:** all 15 pages open; the sidebar fits or scrolls on a 1366×768 screen; the taskbar's
      Do Not Disturb icon (right-click) opens Notifications; `simpleos-drivers` without arguments opens System & Updates.
- [ ] **Default apps (issue #38):** Control Center → Apps → Pictures = another viewer (install one, e.g. gThumb from the
      Software Center) → double-click a .jpg/.png/.webp in Files opens it; Web browser = Chromium → Super+B and links from
      other apps open Chromium. Back to the old choice works.
- [ ] **Startup apps (issue #39):** install Discord/Steam and let it start at login → it is listed; switch it off → next
      sign-in it does not start; on again → it does. "Add…" Mousepad → it opens at the next sign-in **without** an error
      about a file named "%U"; "Remove" takes it out.
- [ ] **Headphone battery (issue #37):** after a restart, connected Bluetooth headphones show "Battery NN %" in Control
      Center → Bluetooth and in the Bluetooth flyout (headphones that report it: most Sony/Bose/Jabra). `systemctl cat
      bluetooth` shows `--experimental`; pairing a keyboard/mouse still works. Updated machine with Bluetooth: Software
      Updates asks for a restart after the update to 1.0.5 (migration 060-bluetooth-restart).
- [ ] **Keyboard layout in search/app menu (ThinkPad test):** installed with the Swiss (or German) layout, no own
      choice in Control Center → Keyboard: tap Super, type "zy" → the search shows "zy" (not "yz"); same in the app
      menu. `xkbcomp -i $(xinput list --id-only "Virtual core XTEST keyboard") $DISPLAY - | grep -A2 "<AD06>"` shows z.
- [ ] **Signing out and in (bug hunt):** sign out → at the login screen a short press of the power button shuts down
      as before (VM: `virsh shutdown`/ACPI button). Sign in again within a minute: `systemd-inhibit --list` shows
      **one** "Simple OS … handle-power-key", `pgrep -fa 'nightlight --daemon|wallpaper-schedule --daemon|update --watch'`
      shows one of each, and night light "Automatic" still turns warm at 20:00 (`SIMPLEOS_HOUR=21 simpleos-nightlight --apply`).
- [ ] **Calendar (issue #45):** click the clock → the month opens above it (taskbar at the top: below it); today marked;
      click the clock again or Esc → closed; "Date & Time settings" opens the Control Center page.
- [ ] **Dual boot with Windows (issue #46):** install next to Windows (VM with a Windows/fake "Windows" GRUB entry, or
      Pax's Dell): `timedatectl` shows "RTC in local TZ: yes"; boot Windows and back → the time is right in both.
      Control Center → Date & Time shows "Windows on this computer" with the switch and the fast-startup hint; without
      Windows in the boot menu that part is not there.

## 11. What changed in 1.0.6

Control Center Wi-Fi, office default apps, Software Center closing, refresh rates, date search, release tools. Test on a
machine **updated from 1.0.5 through Software Updates** and on a fresh install from the new ISO.

- [ ] **Wi-Fi (issue #76):** laptop with Wi-Fi. Control Center → Wi-Fi lists the networks **online and offline**
      (Turn Wi-Fi off and on with the switch, or disconnect); the connected one says "Connected" with **Disconnect**,
      the others **Connect**; switching to another network asks for its password if it is not saved; no "Click Next".
- [ ] **Office default apps (issue #75):** LibreOffice and ONLYOFFICE installed. Control Center → Apps → Documents =
      ONLYOFFICE → double-click a .docx and an .odt in Files → ONLYOFFICE; back to LibreOffice Writer → Writer. Same for
      Spreadsheets (.xlsx/.ods/.csv) and Presentations (.pptx/.odp). Without any office suite: "Get one…".
- [ ] **Software Center closed while installing (issue #83):** install VLC (or Steam), close the window at once → a
      notification "Installing … continues in the background", later "… is installed", and the app works (Steam:
      `dpkg -l steam-installer`). Start the Software Center again during the installation → the same window with its
      progress, not a second one. Browser: Control Center → Apps → More browsers → Chromium (not installed) → a
      progress window, no terminal; Esc on it does not stop the installation.
- [ ] **Refresh rates (issue #78):** a laptop panel with several rates near 60 (`xrandr` shows e.g. 60.00 59.97 59.96):
      Control Center → Display and Super+P → Refresh rate show "60 Hz", "59.97 Hz", "59.96 Hz", and picking one sets
      exactly that rate (`xrandr` marks it with `*`).
- [ ] **Search (issue #82):** take a screenshot (Print), tap Super, type today's date (`2026-10-24`) + Enter → the
      screenshot is listed. `12-4` + Enter still calculates `8`.
- [ ] **What's new (issue #79):** account from before 1.0.5 that never finished the Setup Wizard (closed with X) and
      was not signed in under 1.0.5: after the update to 1.0.6 the window appears once.
- [ ] **Dual boot, installed offline (issue #73):** install next to Windows **without network** (VM: no NIC; Windows
      clock = local time): after the first start of Simple OS the time is right, `timedatectl` shows "RTC in local TZ:
      yes"; boot Windows → its time is right too. (VM-tested 2026-10-21: QEMU `-rtc base=localtime`, network
      restricted, fake Windows ESP + NTFS, install alongside – right time; with the 1.0.5 script 2 h off.)
- [ ] **Lock screen after idle (issue #88):** sign in (after the update: sign out and in once), touch nothing until
      the screen locks itself (default 10 minutes), then wait **another 10+ minutes** at the lock screen. Type the
      password → the desktop comes back with its windows. `grep -c "Seat seat0: Locking" /var/log/lightdm/lightdm.log`
      (sudo) counts one per lock, not two or more. (VM-tested 2026-10-22 with `xset s 20 20`: 1.0.6 without the fix =
      black screen, with it = desktop.)
- [ ] **Release tools (issues #71, #72, #77):** `sudo ./build_iso.sh` (or without sudo) → `output/` and `output/repo`
      belong to you afterwards and `./tools/release.sh sign` works without a chown; a README/ROADMAP commit during the
      build keeps `dirty=0` in `output/repo/.build-state`; the build log says "changes since v1.0.5"; after `publish`,
      `git describe --tags --abbrev=0` shows `v1.0.6`.

## 12. What changed in 1.0.7

Power button, sleep locking, date order, hotplugged keyboards, disk space before updates. Test on a machine **updated
from 1.0.6 through Software Updates** (VM-tested 2026-10-25 with the files copied in, fake suspend) and on real hardware.

- [ ] **Power button (issue #97):** lock the screen (Super+L), press the power button briefly → the laptop goes to sleep
      (not off); wake it → lock screen, unlock → windows still there. Twice in a row works too. On the desktop the
      button opens the power menu. Sign out, press it at the login screen → it shuts down. Right after the update,
      without a restart: `systemctl status 'simpleos-power-key@*'` shows it running.
- [ ] **Sleep locks once (issue #96):** power menu → Sleep, closing the lid, and closing the lid while already locked:
      after each wake-up `sudo grep -c "Seat seat0: Locking" /var/log/lightdm/lightdm.log` grew by 1 (by 0 when it was
      already locked), and unlocking always works. (VM, fake suspend: 1/1, 1/1, 0 – before 3/4, 2/3, 1.)
- [ ] **Refresh rates (issue #78, ThinkPad E16):** Control Center → Display and Super+P show one "60 Hz", not "60 Hz"
      and "59.95 Hz".
- [ ] **Date order (issue #81):** with a German/Swiss system language: taskbar "So, 25. Okt", its tooltip "Sonntag,
      25. Oktober 2026", the calendar (click on the clock) "25. Oktober 2026", the login and lock screen "So, 25. Okt".
      English (US) unchanged: "Sun, Oct 25".
- [ ] **Keyboard plugged in later (issue #98):** account layout differs from the system's (Control Center → Keyboard,
      password dialog cancelled): plug in a USB keyboard after signing in → it types with the account's layout (y/z).
- [ ] **Disk space before updates (issue #91):** fill the disk until less than ~500 MB are free
      (`fallocate -l …G ~/big`), open Software Updates with updates pending → message "Not enough free disk space …
      Nothing was changed", the button opens the Storage Cleaner; `apt` shows nothing half installed. Delete the file →
      the update installs.
- [ ] **Leftovers (issue #99):** `ls /usr/local/bin/__pycache__` → does not exist (fresh install and after the update).

## 13. What changed in 1.1 (work in progress)

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
- [ ] **Language & Region (issue #42):** Control Center → Language & Region shows the language the installer set.
      Change it to another language (e.g. German → Switzerland): password dialog, progress window "Changing the
      language", then "Sign out now?". After signing out and back in: Firefox, Thunar and the menus are in the new
      language, the taskbar clock and the login screen clock use its date order, `locale` shows `LANG=de_CH.UTF-8`, and
      online the spell checking/Firefox language packs are installed (`dpkg -l 'hunspell-*' 'firefox-esr-l10n-*'`).
      Formats → another region (e.g. English language, formats Germany): the example line on the page shows
      "Donnerstag, 29. Oktober 2026 · 1.234,56 · 1.234,50 €" after the change, apps stay English. Cancel the password
      dialog: nothing changes. Without internet: the language changes, the packs come with the next Software Update.
- [ ] **Camera (issue #44):** Menu → Apps → Camera on the ThinkPad E16: the webcam picture appears within a few
      seconds, moves smoothly (not 5 frames a second), mirrored like a mirror (raise your right hand – it is on the
      right). Take Photo (or Space): white flash, "Saved to Pictures/Camera: Photo …"; the photo opens in the image
      viewer, is sharp and NOT mirrored (text readable). Open Folder shows Pictures/Camera. Camera switch/F-key off or
      lens covered by the privacy slider: what does it show? (No camera found / black picture.) Open the camera in
      Firefox (e.g. a video call test page) and then the Camera app: "The camera is in use", close the tab, Try Again
      → picture. A USB webcam plugged in while the window is open appears in the title bar choice. VM 2026-10-29
      with the virtual test camera (vivid): all of this except the hardware switch and unplugging.
- [ ] **Display scaling (issue #41):** on the ThinkPad E16 (16" 1920x1200, ~141 dpi) Control Center → Display → Scale
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
      Wi-Fi/Sound/Power flyouts still just above it; "Full" again looks as before.
