# Simple OS

Minimaler Desktop auf Basis von Debian 12 „Bookworm“ mit Openbox, gebaut mit live-build.

## Befehle

| Befehl | Zweck |
|---|---|
| `./build_iso.sh` | ISO bauen → `output/Simple-OS.iso` + `.sha256` + `Simple-OS.packages.txt` (braucht `sudo`, Log in `build/build.log`) |
| `./build_iso.sh --config-only` | nur die live-build-Konfiguration nach `build/config` erzeugen (ohne `sudo`) |
| `./test_vm.sh [--uefi\|--secureboot]` | ISO in QEMU starten und installieren: BIOS (`output/disk.qcow2`), UEFI oder UEFI mit Secure Boot und Microsoft-Schlüsseln (OVMF, `output/disk-<modus>.qcow2`, NVRAM in `output/ovmf-vars-<modus>.fd`) |
| `./test_installed_vm.sh [--uefi\|--secureboot]` | installiertes System von der Platte des Modus starten |

Release: Testliste in `TESTING.md`, Text für die Download-Seite in `RELEASE_NOTES.md` (Englisch, Abschnitt
`#known-issues` ist das Ziel des Installer-Knopfs „Known issues“).

## Struktur

```
simple-os/
├── build_iso.sh, test_vm.sh, test_installed_vm.sh   Einstiegspunkte
├── LICENSE, RELEASE_NOTES.md, TESTING.md            GPL-3.0, Download-Text, Release-Testliste
├── Containerfile                                   Build-Umgebung (Debian bookworm + live-build)
├── tools/
│   ├── lb_config.sh      lb config + Build-Zeit-Teile (Branding, fastfetch-Download)
│   └── gen_branding.py   erzeugt Wallpaper, Logos, Calamares- und Plymouth-Grafiken, Bootmenü-Bild der ISO
├── config/               Quelle der live-build-Konfiguration (nur eigene Dateien)
│   ├── package-lists/    10-base, 12-userdirs, 15-system, 20-desktop, 30-apps, 40-hardware, 45-printing, 50-installer, 55-bootloader
│   ├── hooks/live/       Chroot-Hooks (00–13), 99_verify_simpleos (bricht den Build bei Fehlern ab),
│   │                     Binär-Hook 90_boot_menu (GRUB-Einträge „Simple OS Live“)
│   ├── bootloaders/      Boot-Menü (isolinux; Hintergrund splash.png/splash800x600.png erzeugt gen_branding.py)
│   └── includes.chroot/  Dateien im Image, 1:1 wie im Zielsystem
├── build/                Arbeitsverzeichnis von live-build (wird bei jedem Build neu befüllt)
└── output/               Simple-OS.iso (+ .sha256, .packages.txt), VM-Platten
```

git: `build/` und `output/` sind ausgeschlossen (`.gitignore`). Leere Ordner speichert git nicht – Ordner, die
leer ins Image sollen, legt ein Hook an (z.B. die Standardordner in `00_skel_bashrc`).

`config/` wird beim Build nie verändert: `build_iso.sh` kopiert es nach `build/config`, dort ergänzt
`tools/lb_config.sh` die lb-Standarddateien, die generierten Grafiken und das fastfetch-Paket.

## Wo liegt was im Image (`config/includes.chroot/`)

| Pfad | Inhalt |
|---|---|
| `etc/skel/.config/` | Openbox (autostart, menu.xml, rc.xml), tint2, rofi, picom, dunst, kitty, fastfetch, GTK 2/3/4, pcmanfm/libfm |
| `etc/fonts/local.conf` | systemweite Schriften: Inter (auch für „sans-serif“/„system-ui“), JetBrains Mono, Cantarell als Ersatz |
| `etc/NetworkManager/conf.d/20-simpleos-route-metric.conf` | Routen-Priorität: Kabel Metrik 100 vor WLAN 600 (auch vor simulierten/virtuellen Netzen) |
| `usr/local/lib/simpleos/welcome-viewer` | eigenes Welcome-Fenster (GTK3 + WebKit2GTK 4.1), unabhängig vom Standardbrowser |
| `usr/local/bin/simpleos-*` | Hilfsprogramme: Setup-Wizard, Theme, Browser-Wahl, Software-Store, Screenshot, Sound (simpleos-volume), Display (simpleos-display), Zwischenablage (simpleos-clipboard), dunst-Starter mit Akku-Filter (simpleos-dunst), Control Center (simpleos-control-center, Super+I), Software Center (simpleos-software-center), Bluetooth (simpleos-bluetooth), Nachtmodus (simpleos-nightlight), Energie (simpleos-power), Thunar-Aktionen (simpleos-wallpaper, simpleos-copy-file, simpleos-admin-open), Keybindings, Welcome, Netzwerk-Info, Taskleisten-Designer |
| `usr/local/bin/simpleos-powermenu` | Power-Menü (Super+X, roter Knopf in der Taskleiste): Lock, Sleep, Restart, Shut Down, Log Out |
| `usr/local/bin/simpleos-help` | Tastenkürzel-Übersicht (Super+H); `simpleos-keybindings` leitet dorthin weiter |
| `usr/local/bin/simpleos-update` | System-Update: Prüfung nach dem Login, Meldung „Install“, Rofi-Fenster, pkexec-Helfer `--upgrade`/`--refresh`, Neustart nur nach Rückfrage |
| `usr/local/bin/simpleos-usb-notify` | USB-Meldungen für udiskie („"STICK" is ready“ – Klick öffnet den Dateimanager) |
| `usr/local/lib/simpleos/common.sh` | gemeinsame Helfer der Rofi-Werkzeuge: Log, Meldungen, Rofi mit Grab-Wiederholung, Menü mit Aktionen |
| `etc/apt/apt.conf.d/20simpleos-periodic` | Paketlisten täglich laden (nur prüfen, nichts automatisch installieren) |
| `usr/sbin/bootloader-config` | ersetzt das Calamares-Skript von Debian: installiert GRUB (BIOS/UEFI) offline aus `usr/share/simpleos/bootloader-debs` (Hook 08) |
| `usr/local/sbin/simpleos-post-install` | läuft nach der Installation (Calamares): entfernt Installer und Live-Reste |
| `usr/local/sbin/simpleos-system-setup` | Root-Helfer des Setup-Wizards (Browser, Firefox-Entfernung, Office, Gaming) |
| `usr/share/polkit-1/actions/` | Polkit-Aktion für den Root-Helfer (pkexec mit GUI-Passwortdialog) |
| `etc/sysctl.d/99-simpleos-perf.conf` | Kernel-Tuning für Desktop und Gaming |
| `etc/systemd/system.conf.d/` | schnelles Herunterfahren (`DefaultTimeoutStopSec=5s`) |
| `usr/share/simpleos/` | Welcome-Seite, fastfetch-Logo (Wizard-Logo wird generiert) |
| `usr/share/themes/SimpleOS/` | Openbox-Theme (Catppuccin Mocha) |
| `etc/lightdm/` | Login-Manager: Greeter-Theme, Openbox als Standard-Session, Live-Autologin |
| `etc/calamares/` | Installer-Branding (Links zu GitHub: Projekt, Fehler, bekannte Probleme, Releases) und Zusatzmodule |
| `usr/lib/os-release` | Name, Version, `VERSION_CODENAME`, `HOME_URL`, `BUG_REPORT_URL` – Quelle der Fehler-Adresse für `simpleos-report` (die Installer-Links müssen dazu passen, prüft 99_verify). Hook 13 schützt die Datei per `dpkg-divert` vor base-files-Updates (sonst „Debian GNU/Linux 12“ nach jedem Punkt-Release); `/etc/os-release` bleibt ein Link darauf |
| `usr/share/doc/simpleos/copyright` | Lizenzhinweis (GPL-3.0-or-later) mit Quellcode-Adresse |
| `etc/X11/` | libinput-Profile, Session-Umgebung (Flatpak, Smooth Scrolling, `NO_PROXY` für localhost) |

## Nutzer-Werkzeuge

- `simpleos-welcome-wizard` – Einrichtung beim ersten Login (Internet/WLAN, Browser, Dark/Light, Akzentfarbe, Office,
  Gaming, Software-Store). Erneut starten: Menü → Settings → Setup Wizard. Erledigt-Markierung:
  `~/.config/simpleos/wizard-done` (wird bei fehlgeschlagener Installation nicht gesetzt).
  - Browser Chromium/Mullvad → Firefox ESR wird danach restlos entfernt (erst wenn der neue Browser installiert ist).
  - Office: LibreOffice (apt), ONLYOFFICE (Flathub) oder Minimal. Gaming: Ultimate (i386 + Steam, Lutris, MangoHud) oder keins.
  - Schritt 2 „Internet“ (vor allen Downloads, wie Windows): oben der Status („Connected to Home“), darunter
    immer die komplette WLAN-Liste – auch wenn der PC schon online ist. Verbundenes Netz → „Disconnect“, jedes
    andere → Passwortfeld → „Connect“ (= Netz wechseln); nmcli im Hintergrund-Thread. Ohne WLAN-Hardware
    Hinweis aufs Netzwerkkabel, WLAN aus → „Turn on Wi-Fi“. Überspringbar. Anzeige-Logik in `network_view()`
    (ohne Bildschirm testbar).
  - Alle Installationen laufen in **einem** Aufruf `pkexec /usr/local/sbin/simpleos-system-setup …`
    (grafischer Passwortdialog über lxpolkit, Polkit-Aktion `org.simpleos.system-setup`), Fortschritt im Wizard.
- APT-Quellen: `contrib non-free non-free-firmware` sind im Image aktiv (`lb_config.sh`). Calamares schreibt bei der
  Installation nur `main non-free-firmware`; `simpleos-post-install` ergänzt die Komponenten per
  `simpleos-system-setup --repos` (der Helfer prüft sie außerdem vor jeder Installation).
- Fensterregeln (`rc.xml`, `<applications>`): Chromium, Firefox, ONLYOFFICE, Lutris maximiert; Mullvad und
  Steam-Hauptfenster 1100x750 zentriert; Setup-Wizard zentriert. Nur `type="normal"`, Dialoge bleiben unverändert.
- Software Store (`simpleos-software`, Bazaar von Flathub): prüft vor der Installation Platz und Flathub-Erreichbarkeit,
  installiert mit Ladefenster und benennt Fehler richtig (Platz / Internet / sonstiges mit Protokoll). Im Live-Betrieb
  vergrößert `simpleos-live-tune` (Dienst nur bei `boot=live`) das RAM-Overlay auf 85 % und senkt Flatpaks
  Platzreserve auf 100 MB – vorher scheiterten Installationen dort „trotz Internet“ am vollen Overlay.
- Fortschritt überall echt (`/usr/local/lib/simpleos/progress-filter`: flatpak/apt/timeshift -> PROGRESS/STAGE,
  streamt sofort): Setup-Wizard (Balken mit Prozent und Restzeit, z.B. ONLYOFFICE ~1 GB), Software Center,
  Software Store, System-Updates (Ladefenster), Treiber, Backups. Flatpak läuft dafür ohne `--noninteractive`.
  Fehler werden nach Grund gemeldet (Platz / Internet / Details im Protokoll) statt pauschal „Internet“.
- Bildwiederholrate: ohne eigene Einstellung wählt `simpleos-display --restore` beim Login die höchste Rate der
  aktuellen Auflösung (z.B. 144 statt 60 Hz); Auswahl im Control Center → Display bzw. Super+P.
- Tastaturlayout (`simpleos-keyboard-setup`, Control Center → System, Menü → Settings): gängige Layouts inkl.
  Varianten (Swiss German/French, German ohne Tottasten, US international …), sofort per `setxkbmap`, fürs Konto
  und systemweit per `localectl` (`/etc/default/keyboard`, auch Anmeldebildschirm).
- Schriften: Inter, JetBrains Mono, Noto Color Emoji, Liberation 2; Fontconfig mit RGB-Subpixel, leichtem Hinting.
- picom: kurze Blenden (~50 ms) nur für Fenster, Menüs/Rofi/Tooltips sofort; auf echter Hardware Vollbild-Unredirect
  (Spiele/Videos ohne Compositor-Latenz). GLX mit `use-damage`, `glx-no-stencil`, `glx-no-rebind-pixmap`.
  Nur Software-OpenGL (llvmpipe, z.B. VM ohne 3D; erkannt per `glxinfo`): `simpleos-picom` startet
  `/usr/share/simpleos/picom-software.conf` (xrender ohne Schatten/Blenden/runde Ecken) – sonst ~55 % CPU.
  `simpleos-picom --mode` zeigt die Entscheidung.
- Flatpak-Fortschritt: Tempo im Untertitel („Downloading part 2 of 8 · 80 kB/s“) – ein langsamer Flathub-Download
  sieht so nicht mehr wie hängengeblieben aus. Keine hochgerechnete Restzeit (Tempo schwankt je Teil zu stark).
- Software Updates: gibt es weder System- noch App-Updates, ist der Helfer nach dem Nachsehen fertig
  („Already up to date“) statt alles mit Ladebalken durchlaufen zu lassen.
- Fn-Tasten (`simpleos-osd`): Lautstärke ±5 % (höchstens 100 %), Stumm, Helligkeit ±5 % (über logind, nie unter 5 %)
  mit kurzem OSD-Balken in dunst (Catppuccin Mocha, ersetzt sich selbst, nicht im Verlauf).
- Audio: neu angeschlossene Geräte (Bluetooth, HDMI, USB) werden automatisch genutzt (`module-switch-on-connect`,
  `/etc/pipewire/pipewire-pulse.conf.d/`), `rtkit` für Echtzeit-Priorität; erweiterte Einstellungen: pavucontrol.
- Kernel, Firmware, Microcode aus `bookworm-backports` (Pinning: `config/archives/backports.pref.chroot`, im System
  `/etc/apt/preferences.d/simpleos-backports.pref`): Kernel 6.12 kennt neuere Grafik (z.B. Intel Raptor Lake 0xA7AA
  im Core 5 210H – mit 6.1 blieb der Bildschirm bei 800x600), Firmware 2025 (Intel-Grafik in
  `firmware-intel-graphics`, MediaTek, SOF-Audio …). NVIDIA 535 bleibt bei Bookworm (aktueller über
  bookworm-security). Feste Firmware-Liste statt live-build-Automatik (`--firmware-chroot false`).
  `broadcom-sta-dkms` baut mit 6.12 über `/etc/dkms/broadcom-sta.conf`.
- Secure Boot: Live-ISO über shim; das installierte System bekommt shim + signiertes GRUB
  (`simpleos-grub-install`, von Calamares mit `--uefi-secure-boot` aufgerufen).
- Performance (fest im Image): `preload`, `gamemode` (`gamemoderun %command%` in Steam),
  `/etc/sysctl.d/99-simpleos-perf.conf` (u.a. `vm.swappiness=10`, `vm.max_map_count` für Proton).
- `simpleos-theme --mode dark|light --accent blue|mauve|pink|green|peach|teal` (`--pick`: Rofi-Auswahl, Menü → Settings → Appearance)
- `simpleos-browser-select` (Rofi) bzw. `simpleos-browser-select --set chromium.desktop`
- `simpleos-netinfo` (Super+N): LAN-IP, Schnittstelle, Gateway, Hostname, VPN-Status, öffentliche IP (Rofi;
  `--text` fürs Terminal). tint2 zeigt die LAN-IP dauerhaft (`--panel`, Tooltip mit Details, Klick = Infofenster);
  fastfetch listet sie ebenfalls.
- Menü (Rechtsklick): Terminal, Files, Browser, Software Store, Apps, **Settings** (Control Center, Display, Sound, Bluetooth, Night Light, Network & Wi-Fi,
  Network Info, Appearance, Taskbar & Panel, Default Browser, Setup Wizard), Help, Power. Rohe bzw. doppelte Werkzeuge
  (arandr, lxappearance, obconf, tint2conf, pcmanfm …) blendet Hook 07 im Launcher aus.
- Snappiness: picom mit kurzen Blenden nur für Fenster (GLX + VSync; nur llvmpipe: xrender ohne Effekte), Openbox-Untermenüs ohne Verzögerung,
  Doppelklick 200 ms, keine Minimier-Animation.
- Taskleiste (tint2): schwebende, abgerundete Leiste (12/10 px Abstand zum Rand, 14 px Radius, feine Kontur, 40 px):
  App-Button · Fenster · LAN-IP · Tray · [Akku] · Uhr (zweizeilig) · Power-Button (rechts, `simpleos-powermenu`).
  Den Akku nimmt `simpleos-taskbar-select --apply` beim Login nur auf, wenn `simpleos-battery --present` einen
  echten Akku findet (`/sys/class/power_supply/BAT*` mit `type` = Battery und `present` = 1; VMs/PCs ohne Akku: kein
  Symbol; in VMs grundsätzlich nie). „Battery low“ meldet tint2 über `simpleos-battery --low-alert`, das zusätzlich
  Status Discharging prüft. xfce4-power-manager startet nur mit echtem Akku und ist still (Xfconf-Vorgabe
  `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml`: kein Tray-Symbol, keine Meldungen);
  UPower läuft nicht in VMs (`upower.service.d/10-simpleos-no-vm.conf`).
- Design: Inter überall (GTK 2/3/4, Openbox, tint2, Rofi, dunst, fontconfig), Papirus-Dark, Catppuccin Mocha.
  Rofi-Flyouts: runde Karte (16 px) mit feiner Kontur, Überschrift statt Suchfeld, Akzent-Markierung am gewählten
  Eintrag; Netzwerk und Power öffnen wie bei Windows 11 rechts über der Taskleiste. Picom: weiche Schatten und runde
  Ecken für Fenster; Rofi ohne picom-Schatten (picom 9.1 zeichnet ihn eckig, er schiene durch die runden Ecken).
  Wallpaper: geschichtete Dünen in Mocha-Tönen mit feiner Lavender-Kante, ohne Logo (`gen_branding.py`).
  Tooltips deutsch/englisch; Tray-Icons (nm-applet, blueman, volumeicon, Energie) bringen ihre eigenen Tooltips mit.
- `simpleos-taskbar-select` (Settings → Taskbar & Panel): Position oben/unten, Layout (Full/Compact,
  Icons + text/Icons only), Look (Dark, Dark transparent, Match theme), Netzwerk-/Uhranzeige an/aus.
  Zustand in `~/.config/simpleos/taskbar`; ändert nur die betroffenen Zeilen in `tint2rc` und lädt tint2 per
  SIGUSR1 neu. Direkt: `--set position=top`, `--apply` (ruft `simpleos-theme` bei „Match theme“ selbst auf).
- Tastenkürzel-Übersicht: `simpleos-help`, Super+H oder Super+Shift+? (gruppiert, Tippen filtert).
- USB: `udiskie` (Autostart) bindet Sticks/Festplatten automatisch ein; `simpleos-usb-notify` meldet
  „"STICK" is ready – Click to see your files“ (Linksklick = Open → Thunar), „can now be removed safely“ und
  Fehler in Alltagssprache. Tray-Symbol zum Auswerfen nur, solange ein Laufwerk steckt. pcmanfm-Autorun ist aus;
  dunst: Linksklick löst die Aktion einer Meldung aus (Hook 09, dunst 1.9 kennt keine Drop-ins).
- Power-Menü: `simpleos-powermenu` (Super+X, Taskleisten-Knopf, Menü → Power); Sleep sperrt vorher den Bildschirm.
- Live-Modus (`simpleos-live`, erkannt an `boot=live` bzw. `/run/live/medium`): Desktop-Icon „Install Simple OS“,
  Welcome-Fenster mit Banner und Knopf „Install Simple OS Now“, Eintrag ganz oben im Rechtsklick-Menü und
  Mauve-Badge in der Taskleiste – alle starten `simpleos-install` (Calamares per pkexec). Nach der Installation
  verschwindet alles davon (`simpleos-post-install`, beim Login zusätzlich `simpleos-live --setup`).
- Suche (Super antippen / Super+Space, `simpleos-search`): Apps, Systembefehle (Neustart/Aus mit Rückfrage),
  Rechnen (`42*12` + Enter, Enter kopiert), Dateisuche im Home – ein Rofi-Fenster (Script-Modus). Super antippen
  schickt per xcape eine eigene Taste (XF86Search) statt eines künstlichen Super+Space; erneutes Antippen schließt.
  In allen Rofi-Fenstern öffnet ein Klick (Desktop-Symbole: Doppelklick); Openbox-Regel hält Rofi im Vordergrund.
- Fenster andocken (`simpleos-snap`): Super+Pfeile (Hälften, maximieren, wiederherstellen/minimieren, zweiter
  Druck wechselt den Monitor), Super+Alt+Pfeile (Viertel); berücksichtigt Taskleiste, Fensterrahmen, Monitore.
- Task-Manager (`simpleos-taskmanager`, Strg+Umschalt+Esc): „End task“ schickt SIGTERM, nach 1,5 s automatisch
  SIGKILL; Prozesse anderer Benutzer über `pkexec simpleos-taskmanager-helper` (Passwort), Schutz vor
  wiederverwendeten PIDs (Startzeit), Liste aktualisiert sich sofort.
- Hardware & Drivers (`simpleos-drivers`, Control Center → System): erkennt Grafik (NVIDIA Maxwell+ →
  `nvidia-driver`, Kepler → `nvidia-tesla-470-driver`), WLAN-Firmware (Intel/Realtek/Atheros/MediaTek/Broadcom,
  auch USB) und CPU-Microcode; „Install Recommended Drivers“ installiert über `simpleos-system-setup --drivers`
  (feste Paketliste) mit Ladefenster.
- Laptop: Tippen = Klicken und natürliches Scrollen fürs Touchpad (Maus unverändert), Deckel zu =
  Energiesparmodus (logind, auch am Netzteil; angedockt nicht), Akku-Anzeige nur bei echtem Akku. Vor jedem
  Schlafen (Deckel, Power-Menü, `systemctl suspend`) sperrt `/usr/lib/systemd/system-sleep/simpleos-lock` die
  Sitzung (LightDM per D-Bus) und wartet, bis der Sperrbildschirm vorne ist – nach dem Aufklappen ist gesperrt.
- Do Not Disturb (`simpleos-dnd`, Control Center → System, Menü → System, Klick aufs Symbol in der Taskleiste):
  Meldungen pausiert (`dunstctl set-paused`), optional ohne Fenstereffekte (`--no-effects on`: picom aus);
  Glocken-Symbol in der Taskleiste, solange es an ist.
- Akkuschonung (`simpleos-power --charge-limit on|off|status`, Control Center → Power, Schalter nur wenn der
  Laptop es kann): lädt nur bis ~80 %. Lenovo IdeaPad/ThinkBook über `conservation_mode` (ideapad_acpi, im
  Laptop gespeichert), andere über `charge_control_end_threshold` (80/100, Start bei Bedarf darunter bzw. 0).
  Ohne Passwort dank `/etc/udev/rules.d/60-simpleos-charge-limit.rules` (Gruppe sudo); die eigene Wahl steht in
  `~/.config/simpleos/power` und wird beim Login erneut gesetzt (ohne eigene Wahl bleibt der Laptop unberührt).
- Firewall (ufw, `15-system`, Hook 12): ab dem ersten Start an – eingehend gesperrt, ausgehend offen; mDNS
  (Druckersuche), UPnP und DHCP lassen die ufw-Grundregeln (`/etc/ufw/before*.rules`) durch. `ENABLED=yes` in
  `/etc/ufw/ufw.conf` statt `ufw enable` (geht im Chroot nicht). Schalter: Control Center → System → Security
  (`pkexec simpleos-system-setup --firewall on|off`); Zustand liest das Control Center aus `ufw.conf`.
- Speicher voll (earlyoom, Hook 12 schreibt `/etc/default/earlyoom`): erst wenn RAM < 5 % UND Swap/zram < 10 %
  frei sind, wird das Programm mit dem größten Verbrauch beendet; Xorg, LightDM, Openbox, tint2, PipeWire,
  NetworkManager nie. Muster ohne Leerzeichen/Anführungszeichen – systemd teilt `$EARLYOOM_ARGS` nur an Leerzeichen.
- Energieprofile (power-profiles-daemon, `simpleos-power --profile [power-saver|balanced|performance]`, Control
  Center → Power → Power mode): nur angebotene Profile (VMs ohne Performance), der Dienst merkt sich die Wahl.
  thermald nur auf Intel (`ExecCondition` in `/etc/systemd/system/thermald.service.d/`, in VMs startet er ohnehin nicht).
- Firmware/BIOS (fwupd + fwupd-amd64-signed, LVFS): `fwupd-refresh.timer` lädt die Metadaten, `simpleos-update`
  zählt Firmware-Updates mit („System Firmware (firmware)“), der Helfer spielt sie bei `--upgrade` zuletzt ein
  (nicht in VMs) und meldet `FIRMWARE: installed|needs-power|failed`. BIOS-Kapseln laufen beim Neustart
  (Neustart-Hinweis); ohne Netzteil verweigert fwupd → Hinweis „plug in the charger“; ein Firmware-Fehler macht
  das übrige Update nicht ungültig.
- Laufwerke (gnome-disk-utility, Control Center → System → Storage, Menü → System → Disks & USB Sticks):
  USB-Sticks formatieren, ISO-Abbilder schreiben, SMART-Werte.
- Fehler melden (`simpleos-report`, Menü → Help → Report a Problem, Control Center → System): Rofi-Fenster →
  Bericht als `~/Desktop/simpleos-report-JJJJMMTT-HHMM.txt` (System, Hardware, Grafik, Netz, Ton, Speicher, Akku,
  fehlgeschlagene Dienste, Simple-OS-Protokolle, Sitzungsfehler; mit Passwort zusätzlich Systemprotokoll dieses
  und des vorigen Starts, Kernel-Warnungen, apt-Verlauf über `pkexec simpleos-report-helper`). Vor dem Speichern
  ersetzt `redact()` Benutzer-, Klar- und Rechnernamen, gespeicherte Verbindungen (WLAN-Namen), IPv4/IPv6, MAC,
  Seriennummern, E-Mails. Danach öffnet sich `BUG_REPORT_URL` (GitHub: `…/issues/new` mit Vorlage); ohne Adresse
  nur speichern. `--collect [--system]` / `--redact` / `--url` ohne Fenster (Tests im Verify-Hook).
- Drucken & Scannen (`45-printing`, Control Center → System, Menü → Settings → Printers & Scanners): CUPS +
  Avahi/libnss-mdns (Netzwerkdrucker ohne Treiber, IPP Everywhere/AirPrint), ipp-usb (USB), printer-driver-all
  und Foomatic-PPDs für ältere Geräte, system-config-printer (+ -udev, cups-pk-helper: Passwortdialog statt
  Terminal); sane-airscan + simple-scan. Benutzer sind in `lpadmin` und `scanner` (Calamares-Vorgabe, Live-Benutzer
  per Hook 01).
- Standardordner (`12-userdirs`, `/etc/skel`): Desktop, Documents, Downloads, Music, Pictures (+ Screenshots),
  Videos, Templates (mit „Text Document.txt“ für Thunar → Create Document). `~/.config/user-dirs.dirs` legt feste
  englische Namen fest, „Public“ ist abgeschaltet; Browser speichern nach ~/Downloads. Der Openbox-Autostart
  füllt beim ersten Login die Seitenleiste (GTK-Lesezeichen, braucht den echten Home-Pfad); bewusst kein
  `xdg-user-dirs-update` dort – das biegt gelöschte Ordner auf ~ um, statt sie neu anzulegen.
- Backups (`simpleos-backup` + `simpleos-backup-helper`, timeshift): Wiederherstellungspunkte anlegen, prüfen,
  zurückspielen, löschen; optional automatisch vor jedem System-Update (die 3 neuesten bleiben). Beim ersten
  Öffnen wird timeshift selbst eingerichtet (RSYNC auf der Partition von `/`, Home ausgeschlossen). Im
  Live-Modus gesperrt; Fehler getrennt nach Live-System / kein Zielgerät / zu wenig Speicherplatz – pro Vorgang
  genau eine Meldung. Freier Platz per `shutil.disk_usage` am Ziel von timeshift (Fallbacks bei Fehler/0 Byte);
  mindestens 5 GB vor dem ersten Punkt, 1 GB vor weiteren; die Platzprüfung läuft vor dem Anlegen. Hinweis:
  timeshift 22.11 lehnt `--tags O` ab und endet auch bei Fehlern mit Exit 0 – der Helfer prüft den Erfolg
  deshalb an der Snapshot-Liste.
- Speicher-Cleaner (`simpleos-cleaner`): Paket-Cache, alte Pakete, verwaiste Flatpak-Runtimes, Thumbnails,
  Protokolle älter als 7 Tage – Größen vorher (Scan ohne root, `--dry-run`), Aufräumen mit einem Passwort;
  "Disk usage" zeigt die größten Ordner.
- Dynamic Wallpaper (`simpleos-wallpaper-schedule`, Control Center → Appearance): tagsüber Latte-hell, abends und
  bei aktivem Nachtmodus Mocha-dunkel (`wallpaper-day.png` erzeugt `tools/gen_branding.py`); optional schaltet
  es auch Hell/Dunkel mit.
- Hell/Dunkel (`simpleos-theme --mode light|dark`) wirkt sofort: GTK3 über XSETTINGS (`xsettingsd`, SIGHUP),
  gsettings/`settings.ini`, Openbox (`--reconfigure`), Wallpaper (`pcmanfm --set-wallpaper`), Rofi-Farben
  Latte/Mocha, Taskleiste mit "Match theme". `gtk-application-prefer-dark-theme` bleibt 0 – GTK liest den Wert
  nur beim Programmstart, dunkel kommt über den Theme-Namen Arc-Dark.
- Rechtsklick-Menü: Catppuccin Mocha, Inter 11, einfarbige Symbole (`/usr/share/simpleos/menu-icons`, Hook
  `11_menu_icons`), runde Ecken und Schatten über picom.
- Updates: `simpleos-update --check` läuft 2 Minuten nach dem Login (nicht in der Live-Session) und meldet sich nur,
  wenn es Updates gibt; Klick → Rofi-Fenster („5 updates available · firefox-esr, …“) → „Install now“ →
  ein Passwortdialog → `simpleos-system-setup --upgrade` (dpkg reparieren, apt-get update, `full-upgrade
  --no-remove`, wenn die Simulation nichts entfernt – sonst `upgrade --with-new-pkgs`; entfernt nie Pakete –,
  danach Flatpak-Apps und Firmware). Gezählt wird genau das, was der Helfer installiert (`apt-get -s`), damit nach
  dem Update nicht dieselben Updates wieder angeboten werden; was nur mit Entfernen ginge, meldet der Helfer als
  `HELD: n` und das Fenster sagt es ehrlich. Kernel, Microcode, Firmware, libc, systemd → `/run/reboot-required`
  (Debian legt die Markierung ohne unattended-upgrades nicht selbst an). Neustart nie direkt aus der Meldung:
  „Restart…“ fragt erst nach („Restart now“ / „Later“). „Check now“ lädt nur die Paketlisten
  (`--refresh`) und zeigt dann, was ansteht. Steht ein eingespieltes BIOS-Update nach dem Neustart noch an, kommt
  eine Meldung, dass es nicht übernommen wurde. Auch über Settings → Software Updates.
- Alle Rofi-Werkzeuge nutzen `usr/local/lib/simpleos/common.sh`: kein `set -e`, Exit 0 in jedem Pfad,
  Details in `~/.cache/<werkzeug>.log`. Der Verify-Hook simuliert alle Klick-Pfade unter dash.
- Netzwerk: `/usr/local/bin/simpleos-wifi` (Settings → Network & Wi-Fi, Klick auf die IP in der Taskleiste; überall
  mit absolutem Pfad eingetragen) – ein Rofi-Flyout wie bei Windows, ohne Terminals, nmtui oder Schnittstellennamen:
  1. Zeile aktives Netz („Connected: Home“ / „Connected: Ethernet“ / „Not connected“; Klick → Disconnect,
  Network Details, Back), darunter die übrigen WLANs nach Signal (Strong/Good/Weak, Schloss = Passwort; Klick
  verbindet bzw. wechselt, Passwort per `rofi -dmenu -password`, gespeicherte Netze ohne Abfrage), ganz unten
  „Turn Off/On Wi-Fi“ und „Network Details“ (`simpleos-netinfo`). Hinweiszeile per `-mesg` (Rofi-Theme mit
  `message`-Element). Ohne WLAN-Adapter nur Kabelstatus + Details. Fehler melden sich per
  `notify-send` in Alltagssprache; startet Rofi nicht, öffnet sich `nm-connection-editor` (GTK), fehlt auch der,
  kommt eine Meldung mit den Netzwerkdaten. Rofi-Grab-Fehler direkt nach dem Taskleisten-Klick → bis zu 3 Versuche.
  Kein `set -e`, jeder Pfad endet mit Exit 0; technische Details in `~/.cache/simpleos-wifi.log`.
  Der Verify-Hook simuliert alle Klick-Pfade (Kabel, WLAN, offline, fehlende GUI-Werkzeuge) unter dash.
  Zusätzlich `nm-applet` im Tray (Linksklick = WLAN-Liste).
- `simpleos-setup` – Kurzname für den Setup-Wizard (`simpleos-welcome-wizard`).
- Willkommensseite `usr/share/simpleos/welcome.html` (offline, ruhige Karten, Catppuccin Mocha, Inter): öffnet
  `simpleos-welcome` im eigenen WebKit-Fenster – nie im Standardbrowser (`$BROWSER`, `xdg-open`), weil gehärtete
  Browser wie der Mullvad Browser (Flatpak) `/usr/share` nicht sehen und ein VPN localhost sperren kann. Ohne Proxy,
  ohne JavaScript, flüchtiges Profil; Web-Links gehen an den Standardbrowser. Fällt WebKit aus: Firefox ESR, dann
  Chromium, sonst eine Meldung mit dem Pfad.
