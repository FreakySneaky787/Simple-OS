# Release tests Simple OS 1.0

Tick these off before uploading. Ideally record any bug you find right away with **Menu → Help → Report a
Problem** – that tests the tool at the same time.

## 0. Build

- [ ] `./build_iso.sh` runs without errors. At the end the verify hook reports `Simple OS verify: OK` (in `build/build.log`).
- [ ] `output/` contains `Simple-OS.iso`, `Simple-OS.iso.sha256` and `Simple-OS.packages.txt`.
- [ ] `cd output && sha256sum -c Simple-OS.iso.sha256` reports `Simple-OS.iso: OK`.

## 1. In the VM (no extra hardware)

`./test_vm.sh` boots the ISO, `./test_installed_vm.sh` then boots the installed system, each in the same mode.

| Mode | Command | What to check |
|---|---|---|
| BIOS | `./test_vm.sh` | the boot menu shows Simple OS (no Debian helmet), installation, restart from the disk |
| UEFI + Secure Boot | `./test_vm.sh --secureboot` | as above, **and** after the installation in a terminal: `mokutil --sb-state` → `SecureBoot enabled` |
| UEFI + encryption | `./test_vm.sh --uefi` | tick "Encrypt system" in the installer. After the restart the system asks for the password and then starts normally |

Already done (October 4, with the ISO from October 3 plus the new boot image):

- The live system boots under UEFI with Secure Boot (Microsoft keys, `SecureBoot enabled`) and under BIOS to the desktop.
- The installation itself has not been tested yet.

## 2. On real hardware

- [ ] **ThinkBook (UEFI):** install, then:
  - The firewall in Control Center → System → Security is on.
  - Power mode offers three profiles.
  - Software Updates shows a BIOS update, if there is one.
  - Install updates: clicking the "Updates installed" notification does **not** restart right away but asks
    first ("Restart now" / "Later"). After the restart Software Updates does not offer the same updates again.
    If a BIOS update was included and it shows up again anyway, a notification says it was not applied.
    If there are problems, keep `~/.cache/simpleos-update.log`.
  - Wi-Fi: run a large download (e.g. a Flatpak). The rate must not keep dropping to a few kB/s. If it does:
    Menu → Help → Report a Problem; the "Network" section lists the driver, link rate and power saving mode
    (`Power save: off` expected).
  - Report a Problem creates a file on the desktop.
- [ ] **Secure Boot on** (enable it in the BIOS): the installed system still starts.
- [ ] **Dual boot with Windows:** choose "Install alongside" in the installer. Afterwards the GRUB menu shows Simple OS
      **and** Windows, and Windows still starts. Make a Windows backup first or use a computer where nothing can be lost.
- [ ] **NVIDIA computer:** Control Center → System → Hardware & Drivers suggests the driver. Install it with Secure Boot
      **off**, restart, then check that `glxinfo -B` shows "NVIDIA" as the renderer.
- [ ] **AMD computer:** graphics, Wi-Fi and sound work. Hardware & Drivers reports nothing missing.

## 3. Report a Problem

- [ ] Menu → Help → Report a Problem → "Create report" → enter the password.
- [ ] Open the file on the desktop and check that it does **not** contain:
  - your name, your user name, your computer name
  - your Wi-Fi name
  - your IP addresses
- [ ] The GitHub page for a new bug report opens (only once the repo is public).

## 4. Publish

1. Create a public repo **`simple-os`** under `FreakySneaky787` on GitHub. The name must match, because the
   installer and Report a Problem link to `github.com/FreakySneaky787/simple-os`.
2. `git remote add origin https://github.com/FreakySneaky787/simple-os.git && git push -u origin main`
3. Releases → "Draft a new release" → tag `v1.0`. Paste the text of `RELEASE_NOTES.md` as the description. Attach the
   three files from `output/` (GitHub allows up to 2 GB per file).
