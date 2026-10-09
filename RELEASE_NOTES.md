# Simple OS 1.0.2

**SOS – Simple Operating System. Keep it Simple.**

Simple OS is a fast, quiet desktop built on Debian 12 "bookworm". It boots straight into a calm dark desktop
(Openbox, Catppuccin colors), sets itself up with a short wizard and keeps itself up to date. You don't
need a terminal.

## What's new in 1.0.2

A maintenance update. If you run Simple OS 1.0 or 1.0.1, you get it through **Software Updates** – no need to
reinstall. The update adds a few small packages (about 40 MB) and removes nothing.

- **The clock is set over the internet now.** Before, nothing kept the time right; on a computer that also runs
  Windows it was often off by hours.
- **Apps that start with the computer work.** "Start Steam / Discord / … when I sign in" did nothing before.
- **Previews in the file manager** for pictures, PDFs and more.
- **No keyring password prompts.** Apps that store passwords (Chromium, Signal, Discord, VS Code …) used to ask
  for a new "keyring" password; the keyring now opens with your login password.
- **Smoother video:** hardware video decoding is available for Intel and AMD graphics (less heat and battery use).
- **Smoother under memory pressure:** memory settings now fit the compressed swap Simple OS uses.
- **Media keys** (play/pause, next, previous) and **Super+L** to lock the screen.
- **After an installation** about 175 MB of leftovers of the installer are removed.
- **Startup of the secure boot files:** updates of Debian's boot loader (shim, GRUB) now reach the EFI partition,
  and a fallback loader is added if there is none, so the computer still starts after a firmware reset.
- **Fixes:** the Hardware & Drivers assistant no longer offers an unsuitable NVIDIA driver to GeForce RTX 50 cards;
  Control Center shows all refresh rates of a monitor and refreshes a page that is opened again; sliders for volume
  no longer stutter; Bluetooth keyboards and phones can be paired (the window with the code opens); Wi-Fi passwords
  are no longer visible to other programs while connecting; chat messages and mails that mention "battery" or "power" are no
  longer hidden on desktop computers; removing Firefox no longer changes Simple OS's own default settings;
  the accent color no longer changes the "Install Simple OS" badge; night light stays on after waking up; the
  calculator in the search shows `2**3` correctly and understands `1,000`.

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

## System requirements

- 64-bit PC (x86-64) with UEFI or legacy BIOS. **Secure Boot is supported**, so you can leave it on.
- 2 GB RAM (1 GB minimum for the installer, 4 GB or more is recommended for browsing and gaming)
- 20 GB disk space (the installer accepts 10 GB)
- Internet for the setup wizard (browser, office suite, games) and for updates

## What's inside

- **Setup wizard** on first login: Wi-Fi, browser (Firefox, Chromium or Mullvad Browser), light/dark,
  accent color, office suite (LibreOffice or ONLYOFFICE) and an optional gaming setup (Steam, Lutris, MangoHud)
- **Control Center** (Super+I) for sound, display, Wi-Fi, Bluetooth, appearance, power and system settings
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
  Control Center → System.
- **Firewall and LAN games:** hosting a game for others on your local network, and Steam Remote Play as the host,
  are blocked by the firewall. Turn it off for that time in Control Center → System → Security.
- **Lenovo laptops:** the first start after installing may show "Self-Healing BIOS ESP" once. That's
  Lenovo's firmware restoring its backup on the new disk layout and is harmless. It does not come back.
- **NVIDIA with Secure Boot:** the NVIDIA driver (Control Center → System → Hardware & Drivers) only works
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
[issue page](https://github.com/FreakySneaky787/simple-os/issues). Drag the file into the issue and describe
what happened.

## License and source code

Simple OS's own scripts and settings are licensed under the GNU GPL, version 3 or later (see `LICENSE`).
Simple OS is built from Debian packages. Each keeps its own license in `/usr/share/doc/<package>/copyright`. The
source code of every package in this release (versions in `Simple-OS.packages.txt`) is available from
[snapshot.debian.org](https://snapshot.debian.org) and [sources.debian.org](https://sources.debian.org).
