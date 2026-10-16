# Simple OS 1.0.5

**SOS – Simple Operating System. Keep it Simple.**

Simple OS is a fast, quiet desktop built on Debian 12 "bookworm". It boots straight into a calm dark desktop
(Openbox, Catppuccin colors), sets itself up with a short wizard and keeps itself up to date. You don't
need a terminal.

## What's new in 1.0.5

A bugfix update with a few small new features and a **new ISO**. If you run Simple OS 1.0 to 1.0.4, you get it
through **Software Updates** – no need to reinstall. Restart once after the update (Software Updates asks for it on
computers with Bluetooth). The first time you sign in afterwards, a short **"What's new"** window shows the highlights.

### Easier to find your way

- **Clearer menus.** The right-click menu is sorted into **Apps, Settings, Tools and Help**. Every entry under
  Settings opens the matching page of the Control Center. Menus you changed yourself keep your changes.
- **The Control Center has more, smaller pages.** Keyboard, Date & Time, Notifications, Printers & Scanners,
  Storage & Backups, Password & Security and System & Updates each have their own page now, instead of one long
  "System" page. Duplicate launchers for the same settings are hidden from the app menu.

### New

- **Choose your default apps** (issue #38). Control Center → Apps: which app opens web links, emails, PDFs, pictures,
  music, videos and text files.
- **Startup apps** (issue #39). On the same page: switch off apps that start by themselves when you sign in (Steam,
  Discord …), or add one.
- **Battery level of Bluetooth headphones** (issue #37) in Control Center → Bluetooth and in the Bluetooth menu of the
  taskbar, for headphones that report it.
- **A calendar** (issue #45). Click the clock in the taskbar to see the month; click it again (or press Esc) to close
  it. "Date & Time settings" opens the Control Center page.
- **Windows and Simple OS on one computer** (issue #46). Windows keeps the computer's clock in local time, Linux in
  UTC, so the time was off by an hour or more after using Windows. New installations next to Windows now keep the clock
  the way Windows does. Already installed? Control Center → Date & Time → "Keep the clock like Windows does". The same
  page explains what to do when you can't change files on your Windows drive (Windows "fast startup").
- **"What's new" window** (issue #65) after updates, once per new version. Find it again under Menu → Help → What's New.

### Fixed

- **Signing out and in again.** Afterwards the power button works on the login screen again, and automatic night
  light, the day/night wallpaper and update messages keep working without a restart.
- **Search and app menu with a Swiss, German or French keyboard.** Y and Z (or A and Q) were swapped there when you
  opened them by tapping the Super key.
- **Updates reach your menu.** On systems where an earlier update had to keep the old right-click menu, the new menu
  now arrives too.
- **Wi-Fi country** follows the time zone you set in Control Center → Date & Time (before, only the one from the
  installation).
- **Startup apps added by hand** no longer try to open a file named "%U".
- **No "USB drive is ready" messages during the installation** for the partitions the installer works on – the
  "Safely remove" button there could have unplugged the disk in the middle of the installation.

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

The other files attached here (`simpleos_1.0.5_all.deb`, `Packages`, `InRelease` …) are the signed update repository that
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
