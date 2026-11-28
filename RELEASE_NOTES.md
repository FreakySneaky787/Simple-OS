# Simple OS 1.2

**SOS – Simple Operating System. Keep it Simple.**

Simple OS is a fast, quiet desktop built on Debian 12 "bookworm". It boots straight into a calm dark desktop
(Openbox, Catppuccin colors), sets itself up with a short wizard and keeps itself up to date. You don't
need a terminal.

## What's new in 1.2

The last feature release of Simple OS 1.x – after it, 1.2.x gets fixes and the work goes into Simple OS 2.0 on Debian 13.
If you run Simple OS 1.0 to 1.1.2, you get it through **Software Updates** – no need to reinstall. The first time you
sign in afterwards, "What's new" shows the highlights.

### New

- **Simple OS speaks German** (issue #43). Every Simple OS window, menu, notification, password prompt and help page
  follows the language you choose in the installer or in Control Center → Language & Region: the Control Center, the
  Setup Wizard, the menus of the taskbar, Software Updates, the right-click menu of the desktop, the app names in the
  start menu and the search. German is the first language; others fall back to English, and more can be added
  without touching the tools (`po/`).
- **Users** in Control Center (issue #68): see who has an account on this computer, add people (name, password,
  Standard user or Administrator), change names, pictures and passwords, delete accounts (keeping or deleting their
  files), and turn on automatic sign-in. Pictures show on the login screen. "Switch user" is in the power menu and the
  search as soon as a second person has an account. Changing your own password keeps your keyring (saved passwords)
  working.
- **Windows programs** (issue #85): double-click a `.exe` or `.msi` file (or right-click → "Run with SOS Bridge").
  **SOS Bridge** – the free app Bottles with Wine – runs many Windows programs. If it is not there yet, a small window
  explains what works and installs it from Flathub with one click, then opens your program. The program opens
  straight away – no Bottles window, no "bottle" to choose (the first time SOS Bridge sets itself up, about a minute).
  Programs you install with their setup file appear in the menu afterwards like any other app, and their
  Documents, Downloads, Pictures, Music and Videos are your own folders (issue #153: tested with 21 programs –
  7-Zip, Notepad++, WinSCP, PuTTY, KeePass, GIMP, Inkscape, LibreOffice, Python and more work; the full list is in [docs/SOS-BRIDGE-APPS.md](docs/SOS-BRIDGE-APPS.md)). The Windows
  installer of an app that has its own Simple OS version (Steam, Discord, Spotify, VLC …) points you to that version
  in the Software Center instead. Menu → Help → Windows
  Programs says honestly what usually works, what doesn't (Microsoft 365, current Adobe apps, games with anti-cheat,
  and never Windows itself: installation media, drivers, antivirus), the alternatives, and where Steam's own
  "Steam Play for all other titles" switch is.
- **Extras in the Setup Wizard** (issue #126): its step "Extras" (the old "Gaming" step) offers SOS Bridge, **Gaming
  Support** (Steam, Lutris, MangoHud – now with game controller support) and **Developer Tools** (Git, compilers,
  Python tools and the code editor VSCodium). All are off unless you turn them on, each shows its download size, and
  one that fails (no internet, no space) no longer ends the setup with an error. The Software Center offers the same
  bundles under the same names.
- **AppArmor** (issue #48): the security profiles that your apps bring along – printing, LibreOffice and more – are
  now loaded at every start. Debian's kernel had the security module on, but no profile was ever used.

### Fixed

- **The search picks the best match** (issue #144). When the mouse pointer rested where the search opened, the row
  under it was selected, and typing "display settings" + Enter could open the Control Center's main page instead.
  Simple OS now ships Rofi with two small fixes: opening a menu no longer selects under a resting pointer, and typing
  always selects the best match again. Moving the mouse still highlights the row under it.
- **No keyring prompt in Chromium** (issue #148). A few minutes after the first sign-in of a new account, Chromium
  asked "Choose password for new keyring": the keyring service that sign-in started quit after two minutes.
- **Chromium in your language** (issue #149): its translations are installed with the system language, like
  Firefox's and LibreOffice's.
- **Your accent color and light mode everywhere** (issue #158). Radio buttons, check boxes, switches, progress bars,
  the selected row and the "Install" buttons of apps now follow the accent you chose (they stayed blue). In light
  mode the file manager's sidebar and the "Open"/"Save" windows are light too, and the Setup Wizard shows the mode and
  accent you pick right away.
- **Folders in your language** (issue #157): a new account on a German or French system gets Dokumente, Bilder,
  Musik … / Documents, Images, Musique …; existing accounts keep their folders.
- **SOS Bridge polish**: the menu calls it "SOS Bridge", not "Bottles" (issue #156); no more empty "Games" folder in
  your home folder (issue #154); while SOS Bridge is removed, your Windows programs disappear from the menu and come
  back when you install it again – and they open at the first click (issue #165).
- **USB sticks** (issues #159, #161): "… is ready" stays until you click it or close it, and ejecting a stick in the
  file manager shows one message, not two.
- **One name for the app store** (issue #155): the Setup Wizard always points to the Software Center; GNOME Software
  is no longer a third store in the menu (it is still under "More apps" in the Software Center).
- **Installer** (issue #160): the time zone starts at Berlin instead of New York (no location lookup on the internet),
  and the last window ("remove the USB stick") and the slideshow are in the language you chose.
- **Installing to an external SSD or USB drive** (issue #166): the live session opened the drive by itself, so the
  installer only offered manual partitioning for it and then stopped with "failed to create partition". USB drives
  are now closed before the installer starts, and nothing is opened by itself while it runs.
- **Welcome window without terminal commands** (issue #162): everything it explains works with clicks.
- **Small things** (issue #147): the calculator in the search understands `round(3.14159,2)`, `max(1,2)` and German
  numbers like `1.234,5`, and shows German results with a decimal comma; the first restore point checks the space it
  really needs (the size of the system) before it starts instead of a fixed 5 GB.

### For testers and developers

- **Automatic boot test** (issue #124): `tools/qemu-test.sh` starts a new ISO in QEMU (BIOS and UEFI) and waits until
  the live desktop runs without failed services; no ISO is published without it.
- **A shorter README** (issue #125): the details moved to `docs/DEVELOPING.md` and `docs/TOOLS.md`.

## What's new in 1.1.2

A bugfix update for 1.1 with better menus. If you run Simple OS 1.0 to 1.1.1, you get it through **Software Updates**
– no need to reinstall. The first time you sign in afterwards, "What's new" shows the highlights.

### Better menus (issue #137)

- **The row under the mouse is highlighted** in the start menu, the search and the taskbar menus (Wi-Fi, sound,
  power …) – the same way as the row picked with the arrow keys, now in your accent color instead of a faint gray.
  Typing still selects the best match; only moving the mouse afterwards moves the highlight.
- **The best match comes first.** Typing "Sound" in the start menu showed Control Center and PulseAudio first; now
  the closest match is at the top.
- **Control Center pages in the search.** "display settings", "sound settings", "Wi-Fi settings" … (also with German
  words like "bildschirm" or "einstellungen") open that page of the Control Center.
- **The sound menu stays open** while you turn the volume up or down, mute, or switch the output – before, it closed
  and opened again after every click.
- **Menus opened from the start menu appear faster.** When the previous menu was still closing, Simple OS waited a
  fixed 0.3 seconds; it now checks every 0.05 seconds.

### Fixed

- **Desktop PCs lock again after a video** (issue #134). On computers without a battery, the service that keeps the
  screen on during a video restarted the screen lock outside your session when the video ended – from then on the
  screen never locked when it turned off. It now only gives the screen time back.
- **Do Not Disturb stays on** (issue #135). After signing out and back in, the bell in the taskbar still said "on"
  while notifications came through again. Do Not Disturb now stays on – also after a restart – until you turn it off.
- **Clearer update window** (issues #129, #131). The window no longer repeats its heading ("Update 3 of 14" under
  "Installing updates"), a new step no longer shows the old step's last line, "Finishing up" no longer flickers, and
  Flatpak's technical lines (table headers, end-of-life notices) and apt's error codes stay in the log.
- **Nothing left behind after signing out** (issue #130). The taskbar's speaker and Do Not Disturb helpers kept
  running after signing out, and one more set was added with every sign-in.
- **Installer: the live session's rights are removed first** (issue #136). If the last installer step failed early,
  the live user's passwordless administrator rights could stay on the installed system.

## What's new in 1.1.1

A bugfix update for 1.1. If you run Simple OS 1.0 to 1.1, you get it through **Software Updates** – no need to
reinstall. Coming from 1.0.x, you get everything of 1.1 below as well.

### Fixed

- **Menus stay open after a slow click** (issue #104). If you held the mouse button a little longer – or pressed the
  touchpad firmly – the desktop and window menus closed again as soon as you let go. They now stay open.
- **The speaker icon opens the sound menu** (issue #104). A click on the speaker in the taskbar used to mute the
  sound without asking; now it opens the sound menu (volume, outputs, advanced settings), like the network
  display next to it. Scroll over it for louder/quieter, middle-click to mute. It shows the volume and mute state.
- **The action menu of notifications follows the display scale** (issue #115). On 2.8K/4K screens it was tiny.
- **Camera: no empty photo files** (issue #116). If a picture could not be read, the camera saved an empty file and
  said "Saved"; now it says the photo could not be saved.
- **Language & Region: changing only the formats** (issue #116) works again on systems whose language setting was
  written in an unusual way by hand.
- **Bigger window buttons** (issue #121). Minimize, maximize and close at the top right of every window were tiny
  (Openbox's 6-pixel defaults). They now have clear shapes of their own, a larger click area, follow the display
  scale, and the close button turns red under the pointer.
- **Updates in plain words** (issue #120). While installing, the progress window said things like "Unpacking apt
  (2.6.2) over (2.6.1) ..." and flickered. It now says "Downloading updates (3 of 14)", "Installing updates (5 of
  14)" and "Finishing up"; apt's own lines are only in the log.
- **The restore point before an update no longer looks frozen** (issue #119). The first restore point can take 10–20
  minutes; the window stood at "0%" and "??? left" the whole time. Now the bar shows that it is working, it counts
  the files already copied, and a line explains that the wait is normal.
- **Each software store has its own icon** (issue #117). The Software Center and the Software Store looked the same
  in the menu and the search; the Software Store now has a shop icon, and Bazaar no longer shows up as a second
  store entry.

## What's new in 1.1

The first feature update. If you run Simple OS 1.0 to 1.0.7, you get it through **Software Updates** – no need to
reinstall. The first time you sign in afterwards, a short **"What's new"** window shows the highlights.

### New

- **Display scaling** (issue #41). Control Center → Display → **Scale** makes text, the taskbar, menus,
  notifications, the mouse pointer and the login screen bigger: 100, 125, 150 or 200 %. "Automatic" picks it from the
  screen's real size – 2.8K and 4K laptops start at 150 or 200 %, Full HD screens stay as they are. It applies at
  once, without signing out.
- **A larger taskbar** for older eyes: Control Center → Appearance → Taskbar → Layout → **Large** gives a higher bar
  with a bigger clock.
- **Language & Region** (issue #42). A new Control Center page changes the language of your apps and the format of
  dates, numbers and currency. Spell checking and the Firefox and LibreOffice languages are installed with it. Sign out
  and back in – no restart needed. Simple OS's own tools stay in English for now (see Known issues).
- **Camera** (issue #44). Menu → Apps → Camera shows your webcam as a mirror and takes photos (Space), saved in
  Pictures/Camera. It tells you plainly when another app is using the camera or none is found.
- **Starting up is quicker** (issue #47). The startup files of an installed system shrink from about 160 MB to
  15–20 MB, so the computer starts about a second sooner and kernel updates finish faster. The new system tries it
  first and keeps the old way if anything doesn't fit; disk mode changes and USB keyboards (for the disk password)
  still work.
- **Faster live system and installation** (issue #19). The ISO is packed with zstd instead of xz: unpacking takes half
  the time, the download is about 6 % bigger.

### Fixed

- **"Safely remove" only for USB drives** (issue #100). A second internal disk with Windows or another Linux on it
  showed up as a USB drive with a "Safely remove" button.
- **Encrypted installations start 20 seconds sooner.** With "Encrypt system" in the installer, every start waited
  about 30 seconds for the encrypted swap until the first kernel update. New installations start without the wait;
  existing ones lose it with this update (at the latest with the next kernel update).
- **Test builds no longer block updates** (issue #102). A computer installed from a test build now gets the published
  version.

## Download

| File | What it is |
|---|---|
| `Simple-OS.iso` | The live and installer image (about 1.7 GB) |
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

The other files attached here (`simpleos_1.2_all.deb`, `rofi_…deb`, `Packages`, `InRelease` …) are the signed update
repository that installed systems use. You don't need to download them yourself.

## System requirements

- 64-bit PC (x86-64) with UEFI or legacy BIOS. **Secure Boot is supported**, so you can leave it on.
- 2 GB RAM (1 GB minimum for the installer, 4 GB or more is recommended for browsing and gaming)
- 20 GB disk space (the installer accepts 10 GB)
- Internet for the setup wizard (browser, office suite, games) and for updates

## What's inside

- **Setup wizard** on first login: Wi-Fi, browser (Firefox, Chromium or Mullvad Browser), light/dark,
  accent color, office suite (LibreOffice or ONLYOFFICE) and optional extras: SOS Bridge for Windows programs, Gaming
  Support (Steam, Lutris, MangoHud, game controllers) and Developer Tools
- **In your language:** every Simple OS window and message in English, German or French (more languages can be added)
- **Control Center** (Super+I) for Wi-Fi, Bluetooth, sound, display, brightness and scaling, appearance, notifications,
  mouse & touchpad, keyboard, language & region, printers, power and screen lock, default and startup apps, date & time, storage and backups,
  password and firewall, user accounts, updates and drivers
- **Software Store** (Flathub) and **Software Updates** with a single password prompt. Firmware and BIOS updates
  from the LVFS are included, and so are **new versions of Simple OS itself**: you don't need to reinstall to get
  the next Simple OS. Settings you changed yourself are kept.
- **Hardware & Drivers**: detects NVIDIA graphics, Wi-Fi chips and CPU microcode and installs what is missing
- **Backups**: restore points with Timeshift, optionally created before every update
- **Windows programs** with SOS Bridge (Bottles): double-click a `.exe` – many programs run, Menu → Help explains which
- **Firewall** on by default, **AppArmor** profiles for the apps that bring them: other devices can't connect to you, while browsing, printing and updates keep working
- **Battery care** (charge to 80 %) on laptops that support it, **power modes**, and protection against freezing
  when memory runs out (earlyoom)
- **Camera** app to see your webcam and take photos
- **Printers & scanners** are found automatically on the network and over USB
- **Report a Problem** (Menu → Help) saves the details of your computer to a file you can attach to a bug report.
  Your name, user name, network names and addresses are removed.
- Kernel 6.12 and current firmware from Debian backports, for recent laptops

## Known issues

- **Languages:** Simple OS's own tools are translated into German; in other languages they stay English while your
  apps follow the language. The keyboard layout can be changed at any time in Control Center → Keyboard.
- **Windows programs** run with SOS Bridge only if Wine supports them: many older programs and lots of games do,
  Microsoft 365, current Adobe apps and games with kernel anti-cheat don't. Programs made for Windows itself –
  Windows installation media and setup tools, drivers, antivirus – never do. Electron apps such as the Windows
  versions of Visual Studio Code and Obsidian don't work in our test (#153) – see the
  [list of tested programs](docs/SOS-BRIDGE-APPS.md). Menu → Help → Windows Programs has alternatives.
- **Formats in English installations:** the installer preselects the time zone Europe/Berlin (no location lookup,
  for privacy), so an English installation gets German number and date formats. Change them in Control Center →
  Language & Region.
- **Installer:** a few texts of the installer itself stay English in a German installation (the summary's "Erase
  disk … and install Simple OS 1.2"), and it suggests a computer name made of your name and the model number
  (e.g. "lena-21tf…") – change it on the "Users" page if you like. Both come from the installer (Calamares 3.2).
- **The network icon's right-click menu** (next to the network display in the taskbar) closes again if you hold the
  mouse button for more than half a second – a limit of that GTK menu, it has no setting. Click quickly, or use the
  network display itself (a click opens the Simple OS network menu).
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
