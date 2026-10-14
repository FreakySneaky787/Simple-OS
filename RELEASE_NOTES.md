# Simple OS 1.0.4

**SOS – Simple Operating System. Keep it Simple.**

Simple OS is a fast, quiet desktop built on Debian 12 "bookworm". It boots straight into a calm dark desktop
(Openbox, Catppuccin colors), sets itself up with a short wizard and keeps itself up to date. You don't
need a terminal.

## What's new in 1.0.4

A bugfix update with a **new ISO** (the installer changed). If you run Simple OS 1.0 to 1.0.3, you get it through
**Software Updates** – no need to reinstall.
It adds `git` and a small screen-lock helper (`xss-lock`) and removes nothing. Sign out and in once after the update
(or restart) so the new screen and power-button settings start.

- **The screen locks when you leave.** After the time set in Control Center → Power → "Turn off the screen after"
  (10 minutes by default) the screen goes dark and the login screen asks for your password. Don't want that? Switch
  off "Lock when the screen turns off" right below it. On laptops the time you set is now really used, also after
  plugging the charger in or out (before, the laptop's power manager put its own 15/10 minutes back).
- **Videos keep the screen on.** Browsers and video players can now stop the screen from turning off – also on desktop
  PCs, where that did not work before.
- **The power button asks first.** Pressing it opens the power menu (Lock, Sleep, Restart, Shut down, Sign out)
  instead of shutting down at once. On some laptops (e.g. Lenovo ThinkBook) the firmware ignores a quick tap while
  the computer runs – hold the button for about a second.
- **New: Brightness slider** in Control Center → Display (laptops), for keyboards without brightness keys.
- **Wi-Fi uses your country's rules.** The Wi-Fi country now follows your time zone (before, a chip could guess the
  wrong country and miss channels your router uses).
- **`git` is included**, the first tool many tutorials ask for.
- **Systems in other languages:** on a German (or any non-English) installation the network menu and the Setup Wizard
  thought you were offline with Wi-Fi off, although you were connected. Fixed.
- **Computers without UEFI (older PCs, "legacy BIOS"): GRUB updates work.** The installer never told the system which
  disk holds the boot loader, so the next GRUB update from Debian would have stopped with an error – and every update
  after it. 1.0.4 answers that once by itself; GRUB updates then go to the disk it is on. If another boot loader owns
  the start of the disk, updates leave it alone.
- **Installing from the USB stick** (issues #62, #64):
  - The installer can no longer run twice. A double click (or the desktop icon plus the Welcome button) started a
    second copy that put a live-system file back while the first one was partitioning.
  - While it installs, the computer does not go to sleep, also not when the laptop lid is closed. The power button and
    the power menu ask first: switching off while the installer resizes a partition can leave every system on the disk
    unable to start. "Shut down anyway" is still there if the installer really hangs.
  - Partitions of this computer that you opened in the file manager are closed before the installer starts; if one is
    still in use, a message says so instead of an installation that stops right after it started.
  - "Lock" and Super+L in Live Mode no longer lock you out of the live session (its password is unknown to you).
  - Before the restart at the end, a window asks you to **remove the USB stick** – otherwise the computer could start the
    live system again instead of your new Simple OS. Pulling the stick before the restart is safe now.
- **Setup Wizard: easier internet step** (issue #63). Already online (network cable or a known Wi-Fi)? Then the
  wizard skips the step. Otherwise it shows three numbered steps (click your network, type its password, click
  Connect), says for which network the password is, and has an eye button to show what you typed. Clicking Next
  after typing the password connects first instead of moving on offline.
- **Installations in other languages** (issue #31): the language you picked in the installer (e.g. German) was set,
  but never generated – programs stayed in English and every update printed "perl: warning: Setting locale failed".
  The dictionary and Firefox in your language were never installed during the installation either. Both work now;
  on an installed system the update generates the missing language once (sign out and in afterwards).
- **The login keyring works from the first login on** (issue #32). In the first session after the installation
  Chromium, Discord and other apps asked for a password for a new keyring – or waited for a window that never
  appeared. Now the keyring is unlocked with your login password right away.
- **Other systems stay in the boot menu.** With Windows or another Linux on the disk, the first GRUB update from
  Debian removed them from the menu at startup. The update brings them back once and keeps them there.
- **Install next to another system on older PCs (BIOS/MBR):** "Install alongside" stopped with "The installer failed
  to create a partition" when the partition to shrink was inside an extended partition (logical partitions, common on
  older PCs with several systems). It works now, and the partition that was marked as active stays active (some older
  BIOSes do not start a disk without one).
- **Fixes:**
  - Control Center → System → Date & Time: cancelling the password window showed "The setting could not be changed".
  - Text you type into the app menu and the search was dark teal on a dark field and hard to read.
  - The Task Manager cut off the Memory column.
  - In light mode some symbols (like Sound in the Control Center) were light gray on white.
  - The Welcome window was taller than small screens (1366×768).
  - The Software Store list had a black frame.
  - "Report a Problem" now also hides Bluetooth addresses written with underscores.

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

The other files attached here (`simpleos_1.0.4_all.deb`, `Packages`, `InRelease` …) are the signed update repository that
installed systems use. You don't need to download them yourself.

## System requirements

- 64-bit PC (x86-64) with UEFI or legacy BIOS. **Secure Boot is supported**, so you can leave it on.
- 2 GB RAM (1 GB minimum for the installer, 4 GB or more is recommended for browsing and gaming)
- 20 GB disk space (the installer accepts 10 GB)
- Internet for the setup wizard (browser, office suite, games) and for updates

## What's inside

- **Setup wizard** on first login: Wi-Fi, browser (Firefox, Chromium or Mullvad Browser), light/dark,
  accent color, office suite (LibreOffice or ONLYOFFICE) and an optional gaming setup (Steam, Lutris, MangoHud)
- **Control Center** (Super+I) for sound, display and brightness, Wi-Fi, Bluetooth, appearance, mouse & touchpad,
  power and screen lock, date & time and system settings
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
[issue page](https://github.com/FreakySneaky787/Simple-OS/issues). Drag the file into the issue and describe
what happened.

## License and source code

Simple OS's own scripts and settings are licensed under the GNU GPL, version 3 or later (see `LICENSE`).
Simple OS is built from Debian packages. Each keeps its own license in `/usr/share/doc/<package>/copyright`. The
source code of every package (versions in `Simple-OS.packages.txt` of the 1.0.3 release; Debian's own updates since then
come straight from Debian) is available from
[snapshot.debian.org](https://snapshot.debian.org) and [sources.debian.org](https://sources.debian.org).
