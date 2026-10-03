# Release-Tests Simple OS 1.0

Abhaken vor dem Hochladen. Gefundene Fehler am besten gleich mit **Menü → Help → Report a Problem**
festhalten. So wird das Werkzeug nebenbei mitgetestet.

## 0. Bauen

- [ ] `./build_iso.sh` läuft ohne Fehler durch. Der Verify-Hook meldet am Ende `Simple OS verify: OK` (steht in `build/build.log`).
- [ ] In `output/` liegen `Simple-OS.iso`, `Simple-OS.iso.sha256` und `Simple-OS.packages.txt`.
- [ ] `cd output && sha256sum -c Simple-OS.iso.sha256` meldet `Simple-OS.iso: OK`.

## 1. In der VM (ohne zusätzliche Hardware)

`./test_vm.sh` startet die ISO, `./test_installed_vm.sh` danach das installierte System, jeweils mit demselben Modus.

| Modus | Befehl | Was prüfen |
|---|---|---|
| BIOS | `./test_vm.sh` | Bootmenü zeigt Simple OS (kein Debian-Helm), Installation, Neustart von der Platte |
| UEFI + Secure Boot | `./test_vm.sh --secureboot` | wie oben, **und** nach der Installation im Terminal: `mokutil --sb-state` → `SecureBoot enabled` |
| UEFI + Verschlüsselung | `./test_vm.sh --uefi` | im Installer „Encrypt system“ ankreuzen. Nach dem Neustart fragt das System nach dem Passwort und startet danach normal |

Schon erledigt (4. Oktober, mit der ISO vom 3. Oktober plus neuem Bootbild):

- Das Live-System startet unter UEFI mit Secure Boot (Microsoft-Schlüssel, `SecureBoot enabled`) und unter BIOS bis zum Desktop.
- Die Installation selbst ist noch nicht getestet.

## 2. Auf echter Hardware

- [ ] **ThinkBook (UEFI):** Installation, dann:
  - Firewall im Control Center → System → Security steht auf an.
  - Power mode bietet drei Profile an.
  - Software Updates zeigt ein eventuelles BIOS-Update.
  - Report a Problem erstellt eine Datei auf dem Desktop.
- [ ] **Secure Boot an** (im BIOS einschalten): Das installierte System startet trotzdem.
- [ ] **Dual-Boot mit Windows:** Im Installer „Install alongside“ wählen. Danach zeigt das GRUB-Menü Simple OS **und**
      Windows, und Windows startet noch. Vorher ein Windows-Backup machen oder einen Rechner nehmen, auf dem nichts verloren gehen kann.
- [ ] **NVIDIA-Rechner:** Control Center → System → Hardware & Drivers schlägt den Treiber vor. Mit Secure Boot
      **aus** installieren, neu starten, dann in `glxinfo -B` „NVIDIA“ als Renderer prüfen.
- [ ] **AMD-Rechner:** Grafik, WLAN und Ton funktionieren. Hardware & Drivers meldet nichts Fehlendes.

## 3. Report a Problem

- [ ] Menü → Help → Report a Problem → „Create report“ → Passwort eingeben.
- [ ] Die Datei auf dem Desktop öffnen und prüfen: Darin dürfen **nicht** vorkommen:
  - dein Name, dein Benutzername, dein Rechnername
  - dein WLAN-Name
  - deine IP-Adressen
- [ ] Die GitHub-Seite für einen neuen Fehlerbericht öffnet sich (erst, wenn das Repo öffentlich ist).

## 4. Veröffentlichen

1. Auf GitHub ein öffentliches Repo **`simple-os`** unter `FreakySneaky787` anlegen. Der Name muss stimmen, weil
   Installer und Report a Problem auf `github.com/FreakySneaky787/simple-os` verlinken.
2. `git remote add origin https://github.com/FreakySneaky787/simple-os.git && git push -u origin main`
3. Releases → „Draft a new release“ → Tag `v1.0`. Den Text von `RELEASE_NOTES.md` als Beschreibung einfügen. Die drei Dateien
   aus `output/` anhängen (GitHub erlaubt bis 2 GB pro Datei).
