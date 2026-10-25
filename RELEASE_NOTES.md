# Simple OS 1.0.7

**SOS – Simple Operating System. Keep it Simple.**

Simple OS is a fast, quiet desktop built on Debian 12 "bookworm". It boots straight into a calm dark desktop
(Openbox, Catppuccin colors), sets itself up with a short wizard and keeps itself up to date. You don't
need a terminal.

## What's new in 1.0.7

A bugfix update. If you run Simple OS 1.0 to 1.0.6, you get it through **Software Updates** – no need to reinstall.
The first time you sign in afterwards, a short **"What's new"** window shows the highlights.

### Fixed

- **Power button on the lock screen** (issue #97). Pressing it while the screen was locked switched the computer off
  at once, and open windows and unsaved work were lost – on laptops with the button next to the keys one accidental
  press was enough. Now it puts the computer to sleep. On the desktop it still opens the power menu, and at the login
  screen with nobody signed in it shuts down as before. Works right after the update, without a restart.
- **Sleep locks the screen once** (issue #96). Closing the lid or choosing Sleep locked the screen two or three times,
  and every extra lock restarted the login screen – the same pattern that made unlocking fail in 1.0.5 (#88).
- **Dates in your language's order** (issue #81). The taskbar clock, its tooltip, the calendar and the clock of the
  login and lock screen used the US order with translated names ("Oktober 20, 2026"). They now follow the language:
  "Di, 20. Okt" and "20. Oktober 2026" in German, "20 October 2026" in British English, 2026年10月20日 in Japanese. US
  English stays as it was.
- **Keyboards plugged in later** (issue #98) – a USB keyboard, or a Bluetooth keyboard reconnecting after sleep – typed
  with the system's layout instead of the one chosen for your account (for example y and z swapped on a Swiss or
  German keyboard).
- **Software Updates checks the free disk space before installing** (issue #91). Before, "not enough free disk space"
  only came after the installation had failed halfway. Now nothing is changed when there isn't enough, the message says
  how much is needed, and a button opens the Storage Cleaner.
- **Refresh rates** (issue #78). Screens that offer 60 Hz and 59.95 Hz showed both; they show a single "60 Hz" now.
- About 450 KB of leftover build files are removed from the system (issue #99).

## Download

| File | What it is |
|---|---|
| `Simple-OS.iso` | The live and installer image (about 1.5 GB) |
| `Simple-OS.iso.sha256` | Checksum to make sure the download is complete and unchanged |
| `Simple-OS.packages.txt` | Every Debian package with its exact version (for source code requests) |

### Check the download

- **Linux:** `sha256sum -c Simple-OS.iso.sha256` (in the download folder) should print `Simple-OS.iso: OK`
- **Windows (PowerShell):** `Get-FileHash Simple-OS.iso` and compare the hash with the one in `Simple-OS.iso.sha256`

### Make a USB stick (4 GB or larger, everything on it is erased)

- **Windows / macOS / Linux:** [balenaEtcher](https://etcher.balena.io) – pick the ISO, pick the stick, Flash.
- **Windows:** [Rufus](https://rufus.ie) also works. If it asks, choose **"Write in DD Image mode"**.
- **Linux:** open *Disks* (gnome-disks), select the stick, choose *Restore Disk Image…* and pick the ISO.

Start the computer from the stick. Usually that's F12, F9, F2 or Esc right after power-on, depending on the brand.
The live system needs no password – not for the installer either. Only if something unexpected asks: the user is
`simple` and the password is `live`.
To install, use **Install Simple OS** on the desktop.

The other files attached here (`simpleos_1.0.7_all.deb`, `Packages`, `InRelease` …) are the signed update repository that
installed systems use. You don't need to download them yourself.

## System requirements

- 64-bit PC (x86-64) with UEFI or legacy BIOS. **Secure Boot is supported**, so you can leave it on.
- 2 GB RAM (1 GB minimum for the installer, 4 GB or more is recommended for browsing and gaming)
- 20 GB disk space (the installer accepts 10 GB)
- Internet for the setup wizard (browser, office suite, games) and for updates

## What's inside

- **Setup wizard** on first login: Wi-Fi, browser (Firefox, Chromium or Mullvad Browser), light/dark,
  accent color, office suite (LibreOffice or ONLYOFFICE) and an optional gaming setup (Steam, Lutris, MangoHud)
- **Control Center** (Super+I) for Wi-Fi, Bluetooth, sound, display and brightness, appearance, notifications, mouse &
  touchpad, keyboard, printers, power and screen lock, default and startup apps, date & time, storage and backups,
  password and firewall, updates and drivers
- **Software Store** (Flathub) and **Software Updates** with a single password prompt. Firmware and BIOS updates
  from the LVFS are included, and so are **new versions of Simple OS itself**: you don't need to reinstall to get
  the next Simple OS. Settings you changed yourself are kept.
- **Hardware & Drivers**: detects NVIDIA graphics, Wi-Fi chips and CPU microcode and installs what is missing
- **Backups**: restore points with Timeshift, optionally created before every update
- **Firewall** on by default: other devices can't connect to you, while browsing, printing and updates keep working
- **Battery care** (charge to 80 %) on laptops that support it, **power modes**, and protection against freezing
  when memory runs out (earlyoom)
- **Printers & scanners** are found automatically on the network and over USB
- **Report a Problem** (Menu → Help) saves the details of your computer to a file you can attach to a bug report.
  Your name, user name, network names and addresses are removed.
- Kernel 6.12 and current firmware from Debian backports, for recent laptops

## Known issues

- **English only.** The installer lets you choose your language and keyboard, but the Simple OS tools
  (Control Center, wizard, messages) are in English. The keyboard layout can be changed at any time in
  Control Center → Keyboard.
- **Firewall and LAN games:** hosting a game for others on your local network, and Steam Remote Play as the host,
  are blocked by the firewall. Turn it off for that time in Control Center → Password & Security.
- **Lenovo laptops:** the first start after installing may show "Self-Healing BIOS ESP" once. That's
  Lenovo's firmware restoring its backup on the new disk layout and is harmless. It does not come back.
- **NVIDIA with Secure Boot:** the NVIDIA driver (Control Center → System & Updates → Hardware & Drivers) only works
  with Secure Boot turned off in the firmware settings, because the firmware doesn't know the key it is signed with.
  Simple OS itself starts with Secure Boot on. Install the NVIDIA driver only after turning Secure Boot off.
- **BIOS/firmware updates** only install while the laptop is plugged in. Whether your model gets them depends on
  the manufacturer (LVFS).
- **Battery care** is only shown if the laptop supports a charge limit (most Lenovo, ASUS, Dell, HP and
  Framework models do).
- **Debian 12 base:** security updates come from Debian until June 2028 (Debian LTS). A version based on
  Debian 13 is planned.

## Found a bug?

Open **Menu → Help → Report a Problem**. It saves a report file to your Desktop and opens the
[issue page](https://github.com/FreakySneaky787/Simple-OS/issues). Drag the file into the issue and describe
what happened.

## License and source code

Simple OS's own scripts and settings are licensed under the GNU GPL, version 3 or later (see `LICENSE`).
Simple OS is built from Debian packages. Each keeps its own license in `/usr/share/doc/<package>/copyright`. The
source code of every package (versions in `Simple-OS.packages.txt` of this release; Debian's own updates since then
come straight from Debian) is available from
[snapshot.debian.org](https://snapshot.debian.org) and [sources.debian.org](https://sources.debian.org).
