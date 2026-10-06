# Simple OS

<p align="center"><img src="docs/sos-banner.png" alt="SOS – Simple Operating System. Keep it Simple." width="100%"></p>

A minimal desktop based on Debian 12 "Bookworm" with Openbox, built with live-build.

Brand: **SOS** – Simple Operating System. The "O" is a lifebuoy (red and white – a rescue from Big Tech), the
slogan is **"Keep it Simple"**. The name stays "Simple OS" (IDs, packages and paths use `simpleos`); SOS is the
logo and short form.

## Commands

| Command | Purpose |
|---|---|
| `./build_iso.sh` | Build the ISO → `output/Simple-OS.iso` + `.sha256` + `Simple-OS.packages.txt` (needs `sudo`, log in `build/build.log`) |
| `./build_iso.sh --config-only` | Only generate the live-build configuration in `build/config` (no `sudo`) |
| `./test_vm.sh [--uefi\|--secureboot]` | Boot the ISO in QEMU and install it: BIOS (`output/disk.qcow2`), UEFI, or UEFI with Secure Boot and Microsoft keys (OVMF, `output/disk-<mode>.qcow2`, NVRAM in `output/ovmf-vars-<mode>.fd`) |
| `./test_installed_vm.sh [--uefi\|--secureboot]` | Boot the installed system from that mode's disk |
| `./tools/release.sh key` | Once: create the release signing key (private key outside the repo, public key into the image) |
| `./tools/release.sh sign` / `publish [--no-iso]` | Sign `output/repo`, publish it with the ISO as GitHub release `v<VERSION>` ("latest") |

Release: test checklist in `TESTING.md`, text for the download page in `RELEASE_NOTES.md` (its `#known-issues`
section is the target of the installer's "Known issues" button).

## Updates to new Simple OS editions

Installed systems follow the newest Simple OS on their own – through **Software Updates**, like any Debian update:

- Everything Simple OS adds to Debian is the package **`simpleos`** (`tools/build_deb.sh`, built by every
  `./build_iso.sh`, also `--config-only`): `config/includes.chroot` minus installer/live-only files and first
  defaults (`EXCLUDE`), its `/etc` files are conffiles. Version = `VERSION_ID` in `usr/lib/os-release` – the **one
  place** to raise for a new edition (also the version on the boot menu and in Calamares).
- The image installs the package (live-build `packages.chroot`) and the APT source
  `/etc/apt/sources.list.d/simpleos.sources`: `https://github.com/FreakySneaky787/simple-os/releases/latest/download/`,
  a flat repository signed with `usr/share/keyrings/simpleos-archive-keyring.asc`. Every GitHub release carries the
  repository (`output/repo`: `simpleos_<v>_all.deb`, fastfetch, `Packages`, `Release`, `InRelease`, `Release.gpg`);
  "latest" always points to the newest one. Hook `98_update_channel` switches the source off in the image if GitHub
  is not reachable during the build (the first release does not exist yet); `simpleos-post-install` switches it on.
- `simpleos-update` lists the new edition at the top ("Simple OS 1.1"), `simpleos-system-setup --upgrade` installs
  it with the other updates. If only the Simple OS source fails (GitHub down), Debian's updates still go on.
- What a package update alone does not reach, `/usr/local/lib/simpleos/edition` does (data in
  `/usr/share/simpleos/edition`, log `/var/log/simpleos-edition.log` and `~/.cache/simpleos-edition.log`):
  - **Settings in the homes** (`--user`, at every sign-in via `/etc/X11/Xsession.d/80simpleos-edition`, before the
    desktop starts): each copy of an `/etc/skel` file is replaced by the new version **only if nobody changed it** –
    its content is a version Simple OS once shipped (`skel.history`, every version from git,
    `tools/managed_history.py`) or the one the tool put there last time. Changed copies – by the user, or at every
    sign-in by Simple OS tools (taskbar: battery/layout lines in `tint2rc`, theme: accent colors, wallpaper
    schedule) – get a **3-way merge** (`diff3`, like git): the changes between the skel version the copy is based on
    (`~/.local/state/simpleos/base/`) and the new one are worked in, the user's/tools' lines stay; if both changed
    the same place the copy stays as it is ("kept" in the log). Deleted copies stay deleted, new files are added.
  - **System** (`--system`, from the package's postinst): `/etc` files dpkg kept although they are an unchanged
    older Simple OS version (`system.history`); files of Debian packages that dpkg would refuse in our package
    (`/etc/issue`, `/etc/motd`, `zramswap`, LightDM greeter, xfce4-power-manager – copies in `edition/system`, same rule);
    the build hooks marked "Re-run on Simple OS updates" (00, 07, 09, 10, 11, 14 – derived settings, must stay
    idempotent; never 12, it would switch a firewall turned off by the user back on); a new boot splash → initramfs.
  - **New packages** in `config/package-lists` (except installer/bootloader): installed once after the upgrade
    (`--todo-packages`, `--mark-packages`); what the user removes later is not installed again, a package that
    could only be installed by removing something is left out (otherwise every update would fail on it).
  - **One-time steps** for changes that need more than replacing a file: executable scripts in
    `config/includes.chroot/usr/share/simpleos/edition/migrations/system/` (root, from the postinst) or `…/user/`
    (each account at sign-in), named `NNN-name`, run once in order; exit ≠ 0 = again next time. A fresh system or
    account counts the existing ones as done.
- `/usr/lib/os-release` belongs to base-files: the package diverts Debian's copy (`dpkg-divert --package simpleos`,
  Debian's goes to `os-release.debian`); hook 13 only checks it.
- Releasing an edition: raise the version in `usr/lib/os-release`, `./build_iso.sh`, test (`TESTING.md`),
  `./tools/release.sh sign`, `./tools/release.sh publish` (draft first, checks that all repository files are
  attached and the signature matches the key in the image, only then "latest"; never an older or equal version).
  **Every** release must carry the repository – `publish` refuses otherwise, also with uncommitted changes in
  `config/`/`tools/` (the next edition only recognizes file versions that are in git) or an `output/repo` newer
  than the ISO. Back up the signing key
  (`~/.local/share/simpleos-release/gnupg`): installed systems only trust that key.
- A new Debian base (Debian 13) is a bigger step than an edition update and is not covered by this.

## Structure

```
simple-os/
├── build_iso.sh, test_vm.sh, test_installed_vm.sh   entry points
├── LICENSE, RELEASE_NOTES.md, TESTING.md            GPL-3.0, download text, release checklist
├── Containerfile                                   build environment (Debian bookworm + live-build)
├── docs/sos-banner.png   README banner (tools/gen_branding.py --readme docs)
├── tools/
│   ├── lb_config.sh      lb config + build-time parts (branding, fastfetch download, edition package)
│   ├── build_deb.sh      edition package "simpleos" + APT repository files in output/repo
│   ├── managed_history.py  every git version of the managed files (edition tool: "unchanged?")
│   ├── release.sh        signing key, sign output/repo, GitHub release
│   └── gen_branding.py   generates wallpapers, logos, Calamares and Plymouth graphics, the ISO boot menu image
├── config/               source of the live-build configuration (own files only)
│   ├── package-lists/    10-base, 12-userdirs, 15-system, 20-desktop, 30-apps, 40-hardware, 45-printing, 50-installer, 55-bootloader
│   ├── hooks/live/       chroot hooks (00–14), 98_update_channel, 99_verify_simpleos (aborts the build on errors),
│   │                     binary hook 90_boot_menu (GRUB entries "Simple OS Live")
│   ├── bootloaders/      boot menu (isolinux; background splash.png/splash800x600.png generated by gen_branding.py)
│   └── includes.chroot/  files in the image, 1:1 as in the target system
├── build/                live-build working directory (refilled on every build)
└── output/               Simple-OS.iso (+ .sha256, .packages.txt), repo/ (update repository), VM disks
```

git: `build/` and `output/` are excluded (`.gitignore`). git does not store empty folders – folders that must be
empty in the image are created by a hook (e.g. the standard folders in `00_skel_bashrc`).

`config/` is never modified by a build: `build_iso.sh` copies it to `build/config`, where `tools/lb_config.sh` adds
the lb default files, the generated graphics and the fastfetch package.

## Where things live in the image (`config/includes.chroot/`)

| Path | Contents |
|---|---|
| `etc/skel/.config/` | Openbox (autostart, menu.xml, rc.xml), tint2, rofi, picom, dunst, kitty, fastfetch, GTK 2/3/4, pcmanfm/libfm |
| `etc/fonts/local.conf` | system-wide fonts: Inter (also for "sans-serif"/"system-ui"), JetBrains Mono, Cantarell as fallback |
| `etc/NetworkManager/conf.d/20-simpleos-route-metric.conf` | route priority: cable metric 100 before Wi-Fi 600 (also before simulated/virtual networks) |
| `etc/NetworkManager/conf.d/30-simpleos-wifi-powersave.conf` | Wi-Fi power saving off (drops to a few kB/s) |
| `etc/modprobe.d/simpleos-wifi.conf` | Realtek rtw89/rtw88, MediaTek mt7921e: PCIe/firmware power saving off (only when that driver is loaded) |
| `usr/local/lib/simpleos/welcome-viewer` | own Welcome window (GTK3 + WebKit2GTK 4.1), independent of the default browser |
| `usr/local/bin/simpleos-*` | helper programs: Setup Wizard, theme, browser choice, Software Store, screenshot, sound (simpleos-volume), display (simpleos-display), clipboard (simpleos-clipboard), dunst launcher with battery filter (simpleos-dunst), Control Center (simpleos-control-center, Super+I), Software Center (simpleos-software-center), Bluetooth (simpleos-bluetooth), night light (simpleos-nightlight), power (simpleos-power), Thunar actions (simpleos-wallpaper, simpleos-copy-file, simpleos-admin-open), keybindings, Welcome, network info, taskbar designer |
| `usr/local/bin/simpleos-powermenu` | power menu (Super+X, red button in the taskbar): Lock, Sleep, Restart, Shut Down, Log Out |
| `usr/local/bin/simpleos-help` | keyboard shortcut overview (Super+H); `simpleos-keybindings` forwards to it |
| `usr/local/bin/simpleos-update` | system updates: check after login, "Install" notification, Rofi window, pkexec helper `--upgrade`/`--refresh` (checking without a password), restart only after asking |
| `usr/local/bin/simpleos-usb-notify` | USB notifications for udiskie ("'STICK' is ready" – a click opens the file manager) |
| `usr/local/lib/simpleos/common.sh` | shared helpers of the Rofi tools: log, notifications, Rofi with grab retry, menu with actions |
| `etc/apt/apt.conf.d/20simpleos-periodic` | refresh package lists daily (check only, never install automatically) |
| `usr/sbin/bootloader-config` | replaces Debian's Calamares script: installs GRUB (BIOS/UEFI) offline from `usr/share/simpleos/bootloader-debs` (hook 08) |
| `usr/local/sbin/simpleos-post-install` | runs after the installation (Calamares): removes the installer and live leftovers |
| `usr/local/sbin/simpleos-system-setup` | root helper of the Setup Wizard (browser, Firefox removal, office, gaming) |
| `usr/share/polkit-1/actions/` | Polkit action for the root helper (pkexec with a graphical password dialog) |
| `etc/sysctl.d/99-simpleos-perf.conf` | kernel tuning for desktop and gaming |
| `etc/systemd/system.conf.d/` | fast shutdown (`DefaultTimeoutStopSec=5s`) |
| `usr/share/simpleos/` | Welcome page, fastfetch logo (the wizard logo is generated) |
| `usr/share/themes/SimpleOS/` | Openbox theme (Catppuccin Mocha) |
| `etc/lightdm/` | login manager: greeter theme, Openbox as default session, live autologin |
| `etc/calamares/` | installer branding (links to GitHub: project, issues, known issues, releases) and extra modules |
| `usr/lib/os-release` | name, version (= version of the package `simpleos`), `VERSION_CODENAME`, `HOME_URL`, `BUG_REPORT_URL` – source of the issue address for `simpleos-report` (the installer links must match it, checked by 99_verify). The package `simpleos` protects the file from base-files updates with `dpkg-divert` (otherwise "Debian GNU/Linux 12" after every point release); `/etc/os-release` stays a link to it |
| `usr/share/doc/simpleos/copyright` | license notice (GPL-3.0-or-later) with the source code address |
| `etc/X11/` | libinput profiles, session environment (Flatpak, smooth scrolling, `NO_PROXY` for localhost) |

## User tools

- `simpleos-welcome-wizard` – setup on first login (internet/Wi-Fi, browser, dark/light, accent color, office,
  gaming, Software Store). Run it again: Menu → Settings → Setup Wizard. Done marker:
  `~/.config/simpleos/wizard-done` (not set if an installation failed).
  - Browser Chromium/Mullvad → Firefox ESR is removed completely afterwards (only once the new browser is installed).
  - Office: LibreOffice (apt), ONLYOFFICE (Flathub) or Minimal. Gaming: Ultimate (i386 + Steam, Lutris, MangoHud) or none.
  - Step 2 "Internet" (before any download, like Windows): the status at the top ("Connected to Home"), below it
    always the full Wi-Fi list – even when the PC is already online. Connected network → "Disconnect", any other
    → password field → "Connect" (= switch networks); nmcli runs in a background thread. Without Wi-Fi hardware a
    hint about the network cable, Wi-Fi off → "Turn on Wi-Fi". Can be skipped. The display logic is in
    `network_view()` (testable without a screen).
  - All installations run in **one** call `pkexec /usr/local/sbin/simpleos-system-setup …`
    (graphical password dialog via lxpolkit, Polkit action `org.simpleos.system-setup`), progress in the wizard.
- APT sources: `contrib non-free non-free-firmware` are enabled in the image (`lb_config.sh`). During installation
  Calamares writes only `main non-free-firmware`; `simpleos-post-install` adds the components with
  `simpleos-system-setup --repos` (the helper also checks them before every installation).
- Window rules (`rc.xml`, `<applications>`): Chromium, Firefox, ONLYOFFICE, Lutris maximized; Mullvad and the
  Steam main window 1100x750 centered; Setup Wizard centered. Only `type="normal"`, dialogs stay unchanged.
- Software Store (`simpleos-software`, Bazaar from Flathub): checks free space and whether Flathub is reachable
  before installing, installs with a progress window and names errors correctly (space / internet / other, with
  log). In live mode `simpleos-live-tune` (service only with `boot=live`) enlarges the RAM overlay to 85 % and
  lowers Flatpak's space reserve to 100 MB – before that, installations failed there "despite internet" because
  the overlay was full.
- Real progress everywhere (`/usr/local/lib/simpleos/progress-filter`: flatpak/apt/timeshift → PROGRESS/STAGE,
  streams immediately): Setup Wizard (bar with percent and time left, e.g. ONLYOFFICE ~1 GB), Software Center,
  Software Store, system updates (progress window), drivers, backups. Flatpak runs without `--noninteractive`
  for this. Errors are reported by cause (space / internet / details in the log) instead of always "internet".
- Refresh rate: without a saved setting, `simpleos-display --restore` picks the highest rate of the current
  resolution at login (e.g. 144 instead of 60 Hz); if a saved monitor is unplugged it does the same. Choose it in
  Control Center → Display or with Super+P.
- Keyboard layout (`simpleos-keyboard-setup`, Control Center → System, Menu → Settings): common layouts including
  variants (Swiss German/French, German without dead keys, US international …), applied at once with `setxkbmap`,
  for the account and system-wide via `localectl` (`/etc/default/keyboard`, also the login screen).
- Fonts: Inter, JetBrains Mono, Noto Color Emoji, Liberation 2; fontconfig with RGB subpixel and slight hinting.
- picom: short fades (~50 ms) for windows only, menus/Rofi/tooltips instant; on real hardware full-screen unredirect
  (games/videos without compositor latency). GLX with `use-damage`, `glx-no-stencil`, `glx-no-rebind-pixmap`.
  Software OpenGL only (llvmpipe, e.g. a VM without 3D; detected with `glxinfo`): `simpleos-picom` starts
  `/usr/share/simpleos/picom-software.conf` (xrender without shadows/fades/rounded corners) – otherwise ~55 % CPU.
  `simpleos-picom --mode` shows the decision.
- Flatpak progress: the speed is shown in the subtitle ("Downloading part 2 of 8 · 80 kB/s") – a slow Flathub
  download no longer looks stuck. No extrapolated time left (the speed varies too much between parts).
- Software Updates: if there are neither system nor app updates, the helper is done after checking
  ("Already up to date") instead of running everything with a progress bar.
- Fn keys (`simpleos-osd`): volume ±5 % (at most 100 %; a volume already above 100 % is kept), mute, brightness
  ±5 % (via logind, never below 5 %) with a short OSD bar in dunst (Catppuccin Mocha, replaces itself, not in the
  history).
- Audio: newly connected devices (Bluetooth, HDMI, USB) are used automatically (`module-switch-on-connect`,
  `/etc/pipewire/pipewire-pulse.conf.d/`), `rtkit` for real-time priority; advanced settings: pavucontrol.
- Kernel, firmware and microcode from `bookworm-backports` (pinning: `config/archives/backports.pref.chroot`, in the
  system `/etc/apt/preferences.d/simpleos-backports.pref`): kernel 6.12 knows newer graphics (e.g. Intel Raptor
  Lake 0xA7AA in the Core 5 210H – with 6.1 the screen stayed at 800x600), firmware 2025 (Intel graphics in
  `firmware-intel-graphics`, MediaTek, SOF audio …). NVIDIA 535 stays with Bookworm (newer via bookworm-security).
  A fixed firmware list instead of live-build's automatic selection (`--firmware-chroot false`).
  `broadcom-sta-dkms` builds with 6.12 via `/etc/dkms/broadcom-sta.conf`.
- Secure Boot: the live ISO boots via shim; the installed system gets shim + signed GRUB
  (`simpleos-grub-install`, called by Calamares with `--uefi-secure-boot`).
- Performance (built into the image): `preload`, `gamemode` (`gamemoderun %command%` in Steam),
  `/etc/sysctl.d/99-simpleos-perf.conf` (among others `vm.swappiness=10`, `vm.max_map_count` for Proton).
- `simpleos-theme --mode dark|light --accent blue|mauve|pink|green|peach|teal` (`--pick`: Rofi selection, Menu → Settings → Appearance)
- `simpleos-browser-select` (Rofi) or `simpleos-browser-select --set chromium.desktop`
- `simpleos-netinfo` (Super+N): LAN IP, interface, gateway, hostname, VPN status, public IP (Rofi;
  `--text` for the terminal). tint2 always shows the LAN IP (`--panel`, tooltip with details, click = info
  window); fastfetch lists it as well.
- Menu (right-click): Terminal, Files, Browser, Software Store, Apps, **Settings** (Control Center, Display, Sound, Bluetooth, Night Light, Network & Wi-Fi,
  Network Info, Appearance, Taskbar & Panel, Default Browser, Setup Wizard), Help, Power. Raw or duplicate tools
  (arandr, lxappearance, obconf, tint2conf, pcmanfm …) are hidden from the launcher by hook 07.
- Snappiness: picom with short fades for windows only (GLX + VSync; llvmpipe only: xrender without effects),
  Openbox submenus without delay, double-click 200 ms, no minimize animation.
- Taskbar (tint2): floating, rounded bar (12/10 px from the edge, 14 px radius, fine border, 40 px):
  app button · windows · LAN IP · tray · [battery] · clock (two lines) · power button (right, `simpleos-powermenu`).
  `simpleos-taskbar-select --apply` adds the battery at login only if `simpleos-battery --present` finds a real
  battery (`/sys/class/power_supply/BAT*` with `type` = Battery and `present` = 1; VMs/PCs without a battery: no
  icon; never in VMs). tint2 reports "Battery low" via `simpleos-battery --low-alert`, which also checks for the
  status Discharging. xfce4-power-manager only starts with a real battery and stays quiet (Xfconf default
  `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml`: no tray icon, no notifications);
  UPower does not run in VMs (`upower.service.d/10-simpleos-no-vm.conf`).
- Design: Inter everywhere (GTK 2/3/4, Openbox, tint2, Rofi, dunst, fontconfig), Papirus-Dark, Catppuccin Mocha.
  Rofi flyouts: rounded card (16 px) with a fine border, a heading instead of a search field, an accent marker on
  the selected entry; Network and Power open above the taskbar on the right, like Windows 11. picom: soft shadows
  and rounded corners for windows; Rofi without picom shadow (picom 9.1 draws it square, it would show through the
  rounded corners). Wallpaper: layered dunes in Mocha tones with a fine lavender edge, no logo (`gen_branding.py`).
  Logo: a lifebuoy (white, four stripes in Catppuccin Red); the wordmark "SOS" uses the ring as the "O" and the two
  "S" in a blue → pink gradient, slogan "Keep it Simple" – Calamares, boot menu, Plymouth, wizard, Welcome page.
  Tooltips in German/English; tray icons (nm-applet, blueman, volumeicon, power) bring their own tooltips.
- `simpleos-taskbar-select` (Settings → Taskbar & Panel): position top/bottom, layout (Full/Compact,
  Icons + text/Icons only), look (Dark, Dark transparent, Match theme), network/clock display on/off.
  State in `~/.config/simpleos/taskbar`; changes only the affected lines in `tint2rc` and reloads tint2 with
  SIGUSR1. Directly: `--set position=top`, `--apply` (calls `simpleos-theme` itself for "Match theme").
- Keyboard shortcut overview: `simpleos-help`, Super+H or Super+Shift+? (grouped, typing filters).
- USB: `udiskie` (autostart) mounts sticks and drives automatically; `simpleos-usb-notify` reports
  "'STICK' is ready – Click to see your files" (left click = Open → Thunar), "can now be removed safely" and
  errors in plain language. A tray icon for ejecting is shown only while a drive is plugged in. pcmanfm autorun
  is off; dunst: a left click triggers a notification's action (hook 09, dunst 1.9 has no drop-ins).
- Power menu: `simpleos-powermenu` (Super+X, taskbar button, Menu → Power); Sleep locks the screen first.
- Live mode (`simpleos-live`, detected by `boot=live` or `/run/live/medium`): desktop icon "Install Simple OS",
  Welcome window with a banner and the button "Install Simple OS Now", an entry at the top of the right-click menu
  and a mauve badge in the taskbar – all start `simpleos-install` (Calamares via pkexec). After the installation
  all of it disappears (`simpleos-post-install`, plus `simpleos-live --setup` at login).
- Search (tap Super / Super+Space, `simpleos-search`): apps, system commands (restart/shut down with
  confirmation), calculations (`42*12` + Enter, Enter copies; also `×` and `÷`), file search in the home folder –
  one Rofi window (script mode). Tapping Super sends its own key via xcape (XF86Search) instead of a synthetic
  Super+Space; tapping again closes it. In all Rofi windows a single click opens (desktop icons: double-click); an
  Openbox rule keeps Rofi in front.
- Window snapping (`simpleos-snap`): Super+arrows (halves, maximize, restore/minimize, a second press moves to the
  next monitor), Super+Alt+arrows (quarters); respects the taskbar, window borders and monitors.
- Task Manager (`simpleos-taskmanager`, Ctrl+Shift+Esc): "End task" sends SIGTERM, then SIGKILL automatically
  after 1.5 s; processes of other users via `pkexec simpleos-taskmanager-helper` (password), protection against
  reused PIDs (start time), the list updates immediately.
- Hardware & Drivers (`simpleos-drivers`, Control Center → System): detects graphics (NVIDIA Maxwell+ →
  `nvidia-driver`, Kepler → `nvidia-tesla-470-driver`), Wi-Fi firmware (Intel/Realtek/Atheros/MediaTek/Broadcom,
  also USB) and CPU microcode; "Install Recommended Drivers" installs via `simpleos-system-setup --drivers`
  (fixed package list) with a progress window.
- Laptop: tap to click and natural scrolling for the touchpad (mouse unchanged), closing the lid = sleep (logind,
  also on AC power; not when docked), battery display only with a real battery. Before every sleep (lid, power
  menu, `systemctl suspend`) `/usr/lib/systemd/system-sleep/simpleos-lock` locks the session (LightDM via D-Bus)
  and waits until the lock screen is in front – after opening the lid the session is locked.
- Do Not Disturb (`simpleos-dnd`, Control Center → System, Menu → System, click on the icon in the taskbar):
  notifications paused (`dunstctl set-paused`), optionally without window effects (`--no-effects on`: picom off);
  a bell icon in the taskbar while it is on.
- Battery protection (`simpleos-power --charge-limit on|off|status`, Control Center → Power, switch only if the
  laptop supports it): charges only up to ~80 %. Lenovo IdeaPad/ThinkBook via `conservation_mode` (ideapad_acpi,
  stored in the laptop), others via `charge_control_end_threshold` (80/100, start below it if needed, or 0).
  No password needed thanks to `/etc/udev/rules.d/60-simpleos-charge-limit.rules` (group sudo); your choice is
  stored in `~/.config/simpleos/power` and set again at login (without your own choice the laptop is left alone).
- Firewall (ufw, `15-system`, hook 12): on from the first boot – incoming blocked, outgoing open; mDNS
  (printer discovery), UPnP and DHCP pass through ufw's default rules (`/etc/ufw/before*.rules`). `ENABLED=yes` in
  `/etc/ufw/ufw.conf` instead of `ufw enable` (does not work in the chroot). Switch: Control Center → System →
  Security (`pkexec simpleos-system-setup --firewall on|off`); the Control Center reads the state from `ufw.conf`.
- Memory full (earlyoom, hook 12 writes `/etc/default/earlyoom`): only when RAM < 5 % AND swap/zram < 10 % are
  free is the program using the most memory ended; never Xorg, LightDM, Openbox, tint2, PipeWire or
  NetworkManager. Patterns without spaces/quotes – systemd splits `$EARLYOOM_ARGS` only at spaces.
- Power profiles (power-profiles-daemon, `simpleos-power --profile [power-saver|balanced|performance]`, Control
  Center → Power → Power mode): only the offered profiles (VMs have no Performance), the service remembers the
  choice. thermald only on Intel (`ExecCondition` in `/etc/systemd/system/thermald.service.d/`, it does not start
  in VMs anyway).
- Firmware/BIOS (fwupd + fwupd-amd64-signed, LVFS): `fwupd-refresh.timer` downloads the metadata, `simpleos-update`
  counts firmware updates too ("System Firmware (firmware)"), the helper installs them last during `--upgrade`
  (not in VMs) and reports `FIRMWARE: installed|needs-power|failed`. BIOS capsules are applied at the next restart
  (restart notice); without a charger fwupd refuses → hint "plug in the charger"; a firmware error does not
  invalidate the rest of the update.
- Disks (gnome-disk-utility, Control Center → System → Storage, Menu → System → Disks & USB Sticks):
  format USB sticks, write ISO images, SMART values.
- Report a problem (`simpleos-report`, Menu → Help → Report a Problem, Control Center → System): Rofi window →
  report as `~/Desktop/simpleos-report-YYYYMMDD-HHMM.txt` (system, hardware, graphics, network, sound, storage,
  battery, failed services, Simple OS logs, session errors; with a password also the system log of this and the
  previous boot, kernel warnings and the apt history via `pkexec simpleos-report-helper`). Before saving,
  `redact()` replaces user, real and host names, saved connections (Wi-Fi names), IPv4/IPv6, MAC addresses,
  serial numbers and email addresses. Then `BUG_REPORT_URL` opens (GitHub: `…/issues/new` with a template);
  without an address the report is only saved. `--collect [--system]` / `--redact` / `--url` work without a window
  (tests in the verify hook).
- Printing & scanning (`45-printing`, Control Center → System, Menu → Settings → Printers & Scanners): CUPS +
  Avahi/libnss-mdns (network printers without drivers, IPP Everywhere/AirPrint), ipp-usb (USB), printer-driver-all
  and Foomatic PPDs for older devices, system-config-printer (+ -udev, cups-pk-helper: password dialog instead of a
  terminal); sane-airscan + simple-scan. Users are in `lpadmin` and `scanner` (Calamares default, the live user
  via hook 01).
- Standard folders (`12-userdirs`, `/etc/skel`): Desktop, Documents, Downloads, Music, Pictures (+ Screenshots),
  Videos, Templates (with "Text Document.txt" for Thunar → Create Document). `~/.config/user-dirs.dirs` sets fixed
  English names, "Public" is disabled; browsers save to ~/Downloads. The Openbox autostart fills the sidebar on
  first login (GTK bookmarks, needs the real home path); deliberately no `xdg-user-dirs-update` there – it points
  deleted folders to ~ instead of creating them again.
- Backups (`simpleos-backup` + `simpleos-backup-helper`, timeshift): create, check, restore and delete restore
  points; optionally automatically before every system update (the 3 newest are kept). timeshift sets itself up
  the first time it is opened (RSYNC on the partition of `/`, home excluded). Blocked in live mode; errors are
  told apart (live system / no target device / not enough space) – exactly one message per action. Free space
  via `shutil.disk_usage` at timeshift's target (fallbacks on error/0 bytes); at least 5 GB before the first
  point, 1 GB before further ones; the space check runs before creating. Note: timeshift 22.11 rejects
  `--tags O` and exits with 0 even on errors – so the helper checks success against the snapshot list.
- Storage Cleaner (`simpleos-cleaner`): package cache, old packages, orphaned Flatpak runtimes, thumbnails,
  logs older than 7 days – sizes beforehand (scan without root, `--dry-run`), cleaning with one password;
  "Disk usage" shows the largest folders.
- Dynamic wallpaper (`simpleos-wallpaper-schedule`, Control Center → Appearance): Latte light during the day,
  Mocha dark in the evening and while night light is on (`wallpaper-day.png` is generated by
  `tools/gen_branding.py`); optionally it switches light/dark mode too.
- Light/dark (`simpleos-theme --mode light|dark`) takes effect immediately: GTK3 via XSETTINGS (`xsettingsd`,
  SIGHUP), gsettings/`settings.ini`, Openbox (`--reconfigure`), wallpaper (`pcmanfm --set-wallpaper`), Rofi colors
  Latte/Mocha, taskbar with "Match theme". `gtk-application-prefer-dark-theme` stays 0 – GTK reads the value only
  at program start, dark comes from the theme name Arc-Dark.
- Right-click menu: Catppuccin Mocha, Inter 11, monochrome icons (`/usr/share/simpleos/menu-icons`, hook
  `11_menu_icons`), rounded corners and shadows via picom.
- Updates: `simpleos-update --check` runs 2 minutes after login (not in the live session) and only shows up when
  there are updates; click → Rofi window ("5 updates available · firefox-esr, …") → "Install now" → one password
  dialog → `simpleos-system-setup --upgrade` (repair dpkg, apt-get update, `full-upgrade --no-remove` if the
  simulation removes nothing – otherwise `upgrade --with-new-pkgs`; never removes packages –, then Flatpak apps
  and firmware). Exactly what the helper installs is counted (`apt-get -s`), so the same updates are not offered
  again after updating; what would only work by removing something is reported by the helper as `HELD: n` and the
  window says so honestly. Kernel, microcode, firmware, libc, systemd → `/run/reboot-required` (Debian does not
  create the marker itself without unattended-upgrades). Never a restart straight from the notification:
  "Restart…" asks first ("Restart now" / "Later"). Opening Software Updates checks by itself (`--refresh` if the
  lists are older than 30 minutes; without a password via the Polkit rule from hook `14_update_refresh`) and shows
  "Install now" right away – without updates only a notification. If the installation fails, the apt error line
  is in the notification (with a pending restart: "Restart … first"). If an installed BIOS update is still pending
  after the restart, a notification says it was not applied. Also via Settings → Software Updates.
- All Rofi tools use `usr/local/lib/simpleos/common.sh`: no `set -e`, exit 0 on every path, details in
  `~/.cache/<tool>.log`. The verify hook simulates all click paths under dash.
- Network: `/usr/local/bin/simpleos-wifi` (Settings → Network & Wi-Fi, click on the IP in the taskbar; registered
  with its absolute path everywhere) – a Rofi flyout like on Windows, without terminals, nmtui or interface names:
  first row the active network ("Connected: Home" / "Connected: Ethernet" / "Not connected"; click → Disconnect,
  Network Details, Back), below it the other Wi-Fi networks by signal (Strong/Good/Weak, lock = password; a click
  connects or switches, password via `rofi -dmenu -password`, saved networks without asking), at the bottom
  "Turn Off/On Wi-Fi" and "Network Details" (`simpleos-netinfo`). Hint line via `-mesg` (Rofi theme with a
  `message` element). Without a Wi-Fi adapter only the cable status + details. Errors are reported via
  `notify-send` in plain language; if Rofi does not start, `nm-connection-editor` (GTK) opens, and if that is
  missing too, a notification with the network data appears. Rofi grab errors right after the taskbar click →
  up to 3 attempts. No `set -e`, every path ends with exit 0; technical details in `~/.cache/simpleos-wifi.log`.
  The verify hook simulates all click paths (cable, Wi-Fi, offline, missing GUI tools) under dash.
  Additionally `nm-applet` in the tray (left click = Wi-Fi list).
- `simpleos-setup` – short name for the Setup Wizard (`simpleos-welcome-wizard`).
- Welcome page `usr/share/simpleos/welcome.html` (offline, calm cards, Catppuccin Mocha, Inter): `simpleos-welcome`
  opens it in its own WebKit window – never in the default browser (`$BROWSER`, `xdg-open`), because hardened
  browsers like the Mullvad Browser (Flatpak) cannot see `/usr/share` and a VPN can block localhost. No proxy,
  no JavaScript, an ephemeral profile; web links go to the default browser. If WebKit fails: Firefox ESR, then
  Chromium, otherwise a notification with the path of the page.
