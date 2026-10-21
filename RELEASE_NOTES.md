# Simple OS 1.0.6

**SOS – Simple Operating System. Keep it Simple.**

Simple OS is a fast, quiet desktop built on Debian 12 "bookworm". It boots straight into a calm dark desktop
(Openbox, Catppuccin colors), sets itself up with a short wizard and keeps itself up to date. You don't
need a terminal.

## What's new in 1.0.6

A bugfix update with a **new ISO** (the installer changed). If you run Simple OS 1.0 to 1.0.5, you get it through
**Software Updates** – no need to reinstall. The first time you sign in afterwards, a short **"What's new"** window
shows the highlights.

### New

- **Choose the app for office files** (issue #75). Control Center → Apps now also has **Documents**, **Spreadsheets**
  and **Presentations**: which app opens .docx/.odt, .xlsx/.ods/.csv and .pptx/.odp files – useful when both
  LibreOffice and ONLYOFFICE are installed. "More browsers" moved right below the web browser.

### Fixed

- **Control Center → Wi-Fi lists the networks again** (issue #76, broken since 1.0.4). Connect, switch to another
  network or disconnect there again – also when you're offline. The network menu in the taskbar was not affected.
- **Closing the Software Center during an installation** (issue #83) no longer stops Steam, LibreOffice or a Flathub
  app halfway: the window closes, the installation finishes in the background, and a message tells you when it's
  done. Opening the Software Center again shows the progress. Installing a browser with "More browsers" shows the usual
  progress window instead of a terminal, which had the same problem.
- **Refresh rates** (issue #78). Screens that offer 60, 59.97 and 59.96 Hz showed "60 Hz" three times in Control
  Center → Display and in the display menu (Super+P). Rates that would look the same now show their decimals.
- **Search and dates** (issue #82). A date like `2026-10-20` (or a phone number like `079-123-45-67`) in the search now
  finds your files – today's screenshots, for example – instead of calculating 2026 − 10 − 20.
- **"What's new" after updates** (issue #79) also appears on accounts from before 1.0.5 whose Setup Wizard was closed
  with the window's X.
- **Installing next to Windows without internet** (issue #73). Afterwards the computer's clock was off by your time
  zone's difference to UTC, in Windows and in Simple OS. The installer now keeps the time Windows set.
- Small text fixes (issue #80).

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

The other files attached here (`simpleos_1.0.6_all.deb`, `Packages`, `InRelease` …) are the signed update repository that
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
