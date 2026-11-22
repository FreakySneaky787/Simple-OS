# Simple OS – the tools

What each of Simple OS's own tools does and how (the developer overview: [DEVELOPING.md](DEVELOPING.md)).

- `simpleos-welcome-wizard` – setup on first login (internet/Wi-Fi, browser, dark/light, accent color, office,
  optional components, Software Store). Run it again: Menu → Help → Setup Wizard. Done marker:
  `~/.config/simpleos/wizard-done` (not set if an installation failed).
  - Browser Chromium/Mullvad → Firefox ESR is removed completely afterwards (only once the new browser is installed).
  - Office: LibreOffice (apt), ONLYOFFICE (Flathub) or Minimal.
  - Step 6 "Extras" (#126, 1.2): optional components, **all off by default**, each with a switch and its download
    size – **SOS Bridge** (Bottles from Flathub for Windows programs, #85), **Gaming Support** (i386 + Steam, Lutris,
    MangoHud, game controllers via `steam-devices`) and **Developer Tools** (Git, `build-essential`, `python3-pip`,
    `python3-venv`, the code editor VSCodium from Flathub). Offline the switches are off with a hint. One that fails
    is no error screen: the helper reports `OPTIONAL-FAILED: <name>` and exits with 3, the wizard says it can be
    added later (Software Center, same names). With an NVIDIA driver from Debian, Gaming Support also installs its
    32-bit libraries: `nvidia-driver-libs:i386`, or `nvidia-tesla-470-driver-libs:i386` for the legacy driver 470
    (Kepler) – chosen by the installed package.
  - Menu entries for the office apps (Openbox → Apps) come from `/usr/local/lib/simpleos/office-menu`, as the
    user, into `~/.config/openbox/menu.xml` only: after the marker `<!-- simpleos-office: … -->` one block per app,
    for exactly what is installed (also from the Software Center or a terminal; removed apps lose their entries).
    The root helper no longer touches any menu (up to 1.0 it also changed `/etc/skel`, a file of the package).
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
- Keyboard layout (`simpleos-keyboard-setup`, Control Center → Keyboard, Menu → Settings → Keyboard): common layouts including
  variants (Swiss German/French, German without dead keys, US international …), applied at once with `setxkbmap`,
  for the account and system-wide via `localectl` (`/etc/default/keyboard`, also the login screen).
- Monitor plugged in later (`simpleos-display --watch`, Openbox autostart): Xorg only reports a new screen, it stays dark
  until someone configures it. The watcher waits for udev's DRM events (no polling), switches the new screen on to the
  right of the existing ones with a hint (Super+P changes the layout), releases unplugged ones and turns all screens on
  again if none is left. It remembers the connected outputs in `$XDG_RUNTIME_DIR/simpleos-display.outputs`.
- Mouse & touchpad (`simpleos-input`, Control Center → Mouse & Touchpad): natural scrolling, tap to click and pointer
  speed through libinput properties (`xinput`), saved in `~/.config/simpleos/input`; the Xorg defaults
  (`40-simpleos-input.conf`) stay untouched until a value is saved. `--watch` re-applies when a device is plugged in.
- Wi-Fi band (Control Center → Wi-Fi, shown while connected): Automatic / 5 GHz only / 2.4 GHz only per connection
  (`nmcli connection modify … 802-11-wireless.band a|bg`, then reconnect). Found on a Sunrise router whose wide DFS channel
  on 5 GHz (160 MHz, ch. 124) made downloads drop to a few kB/s with a perfect signal; 2.4 GHz was steady.
- Date & time (Control Center → Date & Time): automatic time (`timedatectl set-ntp`) and time zone (region + city,
  `timedatectl set-timezone`; polkit asks for the password); "Password" opens `passwd` in a terminal.
- Fonts: Inter, JetBrains Mono, Noto Color Emoji, Liberation 2; fontconfig with RGB subpixel and slight hinting.
  Noto Sans (`fonts-noto-core`, all writing systems) and WenQuanYi Micro Hei (small CJK font) fill the gaps so web pages in
  Arabic, Thai, Hindi, Chinese … show letters instead of empty boxes; Chinese/Japanese/Korean systems get Noto CJK.
- Language packs (`simpleos-system-setup --language`): the image is English; for the system language chosen in the
  installer the dictionary (hunspell), Firefox and LibreOffice language packs are installed – after the installation
  (`simpleos-post-install`, needs the internet; only the download has a time limit, dpkg is never interrupted), by the
  Setup Wizard and by Software Updates. The language itself: hook 04 lists every locale in `/etc/locale.gen` (commented
  out, only en_US generated) – Calamares can only switch on a locale that is listed there. Names are resolved with
  `apt-cache` (`<prefix>-<language>-<country>`, then `<prefix>-<language>`). Firefox's `policies.json` no longer
  forces `en-US`.
- Everyday tools in the image: curl, wget, unzip, zip, openssh-client, git (tutorials and install scripts expect them),
  alsa-ucm-conf (audio profiles of current laptops) and alsa-utils (alsamixer), OpenVPN for NetworkManager.
  journald keeps at most 200 MB of logs (`/etc/systemd/journald.conf.d/10-simpleos.conf`).
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
- Performance (built into the image): `gamemode` (`gamemoderun %command%` in Steam),
  `/etc/sysctl.d/99-simpleos-perf.conf` (among others `vm.swappiness=100` + `vm.page-cluster=0` for zram swap, `vm.max_map_count` for Proton).
- `simpleos-theme --mode dark|light --accent blue|mauve|pink|green|peach|teal` (`--pick`: Rofi selection; Control Center → Appearance)
- `simpleos-browser-select` (Rofi) or `simpleos-browser-select --set chromium.desktop`
- `simpleos-netinfo` (Super+N): LAN IP, interface, gateway, hostname, VPN status, public IP (Rofi;
  `--text` for the terminal). tint2 always shows the LAN IP (`--panel`, tooltip with details, click = info
  window); fastfetch lists it as well.
- Menu (right-click, 1.0.5): Search, Files, Browser, Software Center, Terminal, Apps, **Settings** (All Settings, then
  Wi-Fi & Network, Bluetooth, Sound, Display, Appearance & Wallpaper, Keyboard, Printers & Scanners, Default & Startup
  Apps – each opens its Control Center page – plus Night Light and Do Not Disturb), **Tools** (Software Updates, Task
  Manager, Backups, Storage Cleaner, Disks & USB Sticks, Network Info), **Help** (Welcome, What's New, Keyboard
  Shortcuts, Setup Wizard, Report a Problem), Power. Raw or duplicate tools (arandr, lxappearance, obconf, tint2conf,
  pcmanfm, nm-connection-editor, blueman-manager, htop …) are hidden from the launcher by hook 07.
- Control Center pages (1.0.5): Wi-Fi, Bluetooth (with the battery level of headphones: `bluetoothd --experimental`
  drop-in), Sound, Display, Appearance, Notifications, Mouse & Touchpad, Keyboard, Printers & Scanners, Power,
  **Apps** (default apps → `~/.config/mimeapps.list` + `~/.local/share/applications/defaults.list`; startup apps →
  `~/.config/autostart`, switched off with `Hidden=true`), Date & Time, Storage & Backups, Password & Security, System &
  Updates. `simpleos-control-center PAGE` opens a page; old names (e.g. `system` for the printers) still work.
- Calendar (`simpleos-calendar`, 1.0.5): click on the taskbar clock (tint2 `clock_lclick_command`) – a GTK month view
  next to the clock inside the work area, week numbers, "Date & Time settings"; click again / Esc closes it.
- Dual boot with Windows (1.0.5): with Windows in the GRUB menu (`--class windows`) simpleos-post-install sets the
  hardware clock to local time like Ubuntu (`hwclock --systohc --localtime`); Control Center → Date & Time shows a
  switch (`timedatectl set-local-rtc`) and the fast-startup hint whenever Windows is in the boot menu.
- What's new (`simpleos-whats-new`): once at the first sign-in after an update to a new version (not on a fresh
  install), Menu → Help → What's New. Notes: `usr/share/simpleos/whats-new`, written by hand for every release – the
  build stops if its first line is not `# Simple OS <version>`.
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
- `simpleos-taskbar-select` (Control Center → Appearance → Taskbar): position top/bottom, layout (Full/Compact,
  Icons + text/Icons only), look (Dark, Dark transparent, Match theme), network/clock display on/off.
  State in `~/.config/simpleos/taskbar`; changes only the affected lines in `tint2rc` and reloads tint2 with
  SIGUSR1. Directly: `--set position=top`, `--apply` (calls `simpleos-theme` itself for "Match theme").
- Keyboard shortcut overview: `simpleos-help`, Super+H or Super+Shift+? (grouped, typing filters).
- USB: `udiskie` (autostart) mounts sticks and drives automatically; `simpleos-usb-notify` reports
  "'STICK' is ready – Click to see your files" (left click = Open → Thunar), "can now be removed safely" and
  errors in plain language. A tray icon for ejecting is shown only while a drive is plugged in. pcmanfm autorun
  is off; dunst: a left click triggers a notification's action (hook 09, dunst 1.9 has no drop-ins).
- Power menu: `simpleos-powermenu` (Super+X, taskbar button, Menu → Power); Sleep locks the screen first.
  The power button opens it too (`XF86PowerOff` in `rc.xml`; the Openbox autostart holds a logind inhibitor
  `handle-power-key` for the session). On the lock screen and the login screen `simpleos-power-key` (root, one
  `simpleos-power-key@eventN.service` per ACPI "Power Button", started by udev rule 62) decides: somebody signed in →
  sleep, nobody → shut down (#97; before, logind shut a locked laptop down at once). Some laptops (ThinkPad E16 Gen 3) only
  report the button when it is held for about a second – the firmware drops a quick tap.
- Keyring: hook 17 masks `gnome-keyring-daemon.socket` (globally) so `pam_gnome_keyring` starts the daemon at login –
  with the systemd socket the login keyring created at the first login was unusable for that whole session.
- Screen blanking and lock (`simpleos-power --screen-off MIN | --lock on|off|status | --suspend | --apply`, Control Center
  → Power): **with a battery xfce4-power-manager owns the X screensaver time and the DPMS times** (it sets them again at
  every plug/unplug and keeps the screen on while a browser plays a video; source `xfpm-power.c`/`xfpm-dpms.c`), so the
  setting is written to its xfconf channel; without a battery `xset` is used and `simpleos-screensaver` (D-Bus-activated,
  `org.freedesktop.ScreenSaver`, quits 30 s after the last video) answers the browsers' inhibit request. `xss-lock`
  locks with `dm-tool lock` (`simpleos-power --lock-now`) when the screensaver starts – not in the live session and not
  while the lock screen is already in front (#88) or a lock was started in the last 4 s (#96: the time is in
  `$XDG_RUNTIME_DIR/simpleos-lock`; power menu, Control Center and search lock through it too); LightDM's `display-setup-script`
  (`greeter-screen`) darkens the lock screen after 2 minutes and writes the greeter's clock format in the order of the
  system language (`/etc/xdg/lightdm/lightdm-gtk-greeter.conf.d/50-simpleos-clock.conf`, #81). Brightness: `simpleos-osd brightness get|set PCT`
  (Control Center → Display). Wi-Fi regulatory country from the time zone: `simpleos-regdom` (service, path unit on
  `/etc/localtime`, udev rule on `ieee80211`).
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
- Hardware & Drivers (`simpleos-drivers`, Control Center → System & Updates): detects graphics (NVIDIA Maxwell+ →
  `nvidia-driver`, Kepler → `nvidia-tesla-470-driver`), Wi-Fi firmware (Intel/Realtek/Atheros/MediaTek/Broadcom,
  also USB) and CPU microcode; "Install Recommended Drivers" installs via `simpleos-system-setup --drivers`
  (fixed package list) with a progress window.
- Laptop: tap to click and natural scrolling for the touchpad (mouse unchanged), closing the lid = sleep (logind,
  also on AC power; not when docked), battery display only with a real battery. Before every sleep (lid, power
  menu, `systemctl suspend`) `/usr/lib/systemd/system-sleep/simpleos-lock` locks the session (LightDM via D-Bus)
  and waits until the lock screen is in front – after opening the lid the session is locked. It does not lock a second
  time (#96: each extra lock restarts LightDM's login screen): not when the lock screen is in front already, a lock was
  just started, or xss-lock locks on the sleep signal – then it only waits, and locks only if the lock screen never comes.
- Do Not Disturb (`simpleos-dnd`, Control Center → Notifications, Menu → Settings, click on the icon in the taskbar):
  notifications paused (`dunstctl set-paused`), optionally without window effects (`--no-effects on`: picom off);
  a bell icon in the taskbar while it is on.
- Battery protection (`simpleos-power --charge-limit on|off|status`, Control Center → Power, switch only if the
  laptop supports it): charges only up to ~80 %. Lenovo IdeaPad/ThinkBook via `conservation_mode` (ideapad_acpi,
  stored in the laptop), others via `charge_control_end_threshold` (80/100, start below it if needed, or 0).
  No password needed thanks to `/etc/udev/rules.d/60-simpleos-charge-limit.rules` (group sudo); your choice is
  stored in `~/.config/simpleos/power` and set again at login (without your own choice the laptop is left alone).
- AppArmor (`apparmor`, `15-system`, #48, 1.2): loads the profiles that Debian packages bring themselves at boot
  (CUPS and its PDF backend, man, dhclient enforced; LibreOffice in complain mode = only logged). Debian's kernel has
  the module on anyway – before 1.2 no profile was ever loaded. No `apparmor-profiles(-extra)`: untested confinement.
  Check: `sudo aa-status`, denials: `journalctl -k | grep DENIED` (cupsd's "net_admin" at start is harmless).
- Firewall (ufw, `15-system`, hook 12): on from the first boot – incoming blocked, outgoing open; mDNS
  (printer discovery), UPnP and DHCP pass through ufw's default rules (`/etc/ufw/before*.rules`). `ENABLED=yes` in
  `/etc/ufw/ufw.conf` instead of `ufw enable` (does not work in the chroot). Switch: Control Center → Password &
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
- Disks (gnome-disk-utility, Control Center → Storage & Backups, Menu → Tools → Disks & USB Sticks):
  format USB sticks, write ISO images, SMART values.
- Report a problem (`simpleos-report`, Menu → Help → Report a Problem, Control Center → System & Updates): Rofi window →
  report as `~/Desktop/simpleos-report-YYYYMMDD-HHMM.txt` (system, hardware, graphics, network, sound, storage,
  battery, failed services, Simple OS logs, session errors; with a password also the system log of this and the
  previous boot, kernel warnings and the apt history via `pkexec simpleos-report-helper`). Before saving,
  `redact()` replaces user, real and host names, saved connections (Wi-Fi names), IPv4/IPv6, MAC addresses,
  serial numbers and email addresses. Then `BUG_REPORT_URL` opens (GitHub: `…/issues/new` with a template);
  without an address the report is only saved. `--collect [--system]` / `--redact` / `--url` work without a window
  (tests in the verify hook).
- Printing & scanning (`45-printing`, Control Center → Printers & Scanners, Menu → Settings → Printers & Scanners): CUPS +
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
- Updates: `simpleos-update --watch` (Openbox autostart) runs `--check` 2 minutes after login and then every 12
  hours while the session runs – it looks at the clock every minute, so after waking up from sleep a due check runs
  2 minutes later (before 1.0.1 there was only the check after login). Not in the live session; it only shows up when
  there are updates. Counted: Debian packages, a new Simple OS edition, firmware, and apps from the Software Store
  (Flatpak, system installation, `flatpak remote-ls --updates`, listed as "… (app)" – before 1.0.1 an update of
  only e.g. the Mullvad Browser was never offered). Click → Rofi window ("5 updates available · firefox-esr, …") → "Install now" → one password
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
  after the restart, a notification says it was not applied. Also via Menu → Tools → Software Updates.
- All Rofi tools use `usr/local/lib/simpleos/common.sh`: no `set -e`, exit 0 on every path, details in
  `~/.cache/<tool>.log`. The verify hook simulates all click paths under dash.
- Network: `/usr/local/bin/simpleos-wifi` (click on the IP in the taskbar; registered
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
- **Control Center → Users** (#68, 1.2): the people's accounts with picture and type; add (full name, a suggested
  user name, password, Standard user or Administrator = group `sudo`), delete (keep or delete the home folder), full
  name, picture, password, account type, sign in automatically, switch user (`dm-tool switch-to-greeter`, also in the
  power menu and the search when another account exists). Root parts: `/usr/local/sbin/simpleos-users-helper` via
  pkexec (polkit `org.simpleos.users`, administrator password; only accounts with UID_MIN..UID_MAX and a login shell;
  the last administrator and your own account can't be deleted or demoted; a signed-in account isn't deleted). New
  accounts get the installer's groups (audio, video, lpadmin, scanner, bluetooth …). Pictures go through
  **AccountsService** (new home folders are private, the greeter can't read `~/.face`); your own name and picture
  through AccountsService without a password, your own password through `passwd` in a pseudo terminal (the keyring
  follows). Automatic sign-in: `/etc/lightdm/lightdm.conf.d/50-simpleos-autologin.conf`, the installer's
  `autologin-user` line in `lightdm.conf` is commented out (that file is read last). No guest account.
- `simpleos-windows-app` – Windows programs (#85): a double-click on a `.exe`/`.msi` (and the right-click action "Run
  with SOS Bridge") starts it directly in SOS Bridge's own bottle "Windows" (`bottles-cli run`, the sandbox gets the
  program's folder; the bottle is created on first use with a progress window, ~1 min). When Wine has ended, the
  shortcuts the program put in Wine's start menu become menu entries (`~/.local/share/applications/simpleos-bridge-*`,
  started with `--start`, removed when the program is gone). Without Bottles a small window explains honestly what
  works and offers to install **SOS Bridge** (Bottles from Flathub, space and Flathub checked first, progress
  window). `--help-page` opens
  `/usr/share/simpleos/windows-programs.html` (Menu → Help → Windows Programs) in the welcome window: what usually
  works, what doesn't (Microsoft 365, current Adobe apps, kernel anti-cheat) with alternatives, Steam's "Steam Play
  for all other titles" switch. SOS Bridge is only the name of the bundle, not a Windows layer of our own.
- Welcome page `usr/share/simpleos/welcome.html` (offline, calm cards, Catppuccin Mocha, Inter): `simpleos-welcome`
  opens it in its own WebKit window – never in the default browser (`$BROWSER`, `xdg-open`), because hardened
  browsers like the Mullvad Browser (Flatpak) cannot see `/usr/share` and a VPN can block localhost. No proxy,
  no JavaScript, an ephemeral profile; web links go to the default browser. If WebKit fails: Firefox ESR, then
  Chromium, otherwise a notification with the path of the page.
