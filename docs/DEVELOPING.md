# Simple OS – for developers

How Simple OS is built, updated and organized. The tools themselves are described in [TOOLS.md](TOOLS.md), the release steps in [MAINTAINING.md](MAINTAINING.md), the test checklist in [TESTING.md](../TESTING.md).

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
| `./tools/qemu-test.sh [ISO] [--bios\|--uefi]` | Automatic boot test (#124): starts the ISO headless, BIOS and UEFI, and waits for the live session to report a running desktop without failed services (`output/qemu-test/`, needed by `release.sh publish`) |
| `./test_installed_vm.sh [--uefi\|--secureboot]` | Boot the installed system from that mode's disk |
| `./tools/release.sh key` | Once: create the release signing key (private key outside the repo, public key into the image) |
| `./tools/release.sh version X.Y.Z` | Set the version of the next edition everywhere it is shown (`usr/lib/os-release`, installer branding) |
| `./tools/release.sh sign` / `publish` | Sign `output/repo`, publish it with the ISO as GitHub release `v<VERSION>` ("latest"); every release has an ISO (#114) |

Release: test checklist in `TESTING.md`, text for the download page in `RELEASE_NOTES.md` (its `#known-issues`
section is the target of the installer's "Known issues" button).

## Updates to new Simple OS editions

Installed systems follow the newest Simple OS on their own – through **Software Updates**, like any Debian update:

- Everything Simple OS adds to Debian is the package **`simpleos`** (`tools/build_deb.sh`, built by every
  `./build_iso.sh`, also `--config-only`): `config/includes.chroot` minus installer/live-only files and first
  defaults (`EXCLUDE`), its `/etc` files are conffiles. Version = `VERSION_ID` in `usr/lib/os-release`, also the
  version on the boot menu. `./tools/release.sh version X.Y.Z` sets it together with `VERSION`, `PRETTY_NAME` and the
  installer's branding (`etc/calamares/branding/simpleos/branding.desc`); `build_deb.sh` refuses to build when they
  do not match (before 1.0.1 the installer had "1.0" written in by hand).
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
    the build hooks marked "Re-run on Simple OS updates" (00, 07, 09, 10, 11, 14, 17 – derived settings, must stay
    idempotent; never 12, it would switch a firewall turned off by the user back on); a new boot splash → initramfs.
  - **New packages** in `config/package-lists` (except installer/bootloader): installed once after the upgrade
    (`--todo-packages`, `--mark-packages`); what the user removes later is not installed again, a package that
    could only be installed by removing something is left out (otherwise every update would fail on it).
  - **One-time steps** for changes that need more than replacing a file: executable scripts in
    `config/includes.chroot/usr/share/simpleos/edition/migrations/system/` (root, from the postinst) or `…/user/`
    (each account at sign-in), named `NNN-name`, run once in order; exit ≠ 0 = again next time. A fresh system or
    account counts the existing ones as done. Example: `system/010-skel-office-menu` (1.0.1) takes the office
    entries that the 1.0 Setup Wizard wrote into `/etc/skel/.config/openbox/menu.xml` out again – with them the
    file counted as changed, and no later menu change would have reached those systems.
    `system/020-browser-defaults` (1.0.2) gives the shipped browser (`firefox-esr`) back to `/etc/xdg/mimeapps.list` and
    `defaults.list`, which the Setup Wizard's Firefox removal used to rewrite. 1.0.4: `030-grub-pc-devices` (BIOS: tell
    grub-pc which disk holds GRUB), `040-locale-gen` (generate the system language that up to 1.0.3 was never
    generated), `050-os-prober` (rebuild the GRUB menu once with other systems in it). 1.0.5: `060-bluetooth-restart`
    (ask for a restart so headphone battery levels show). 1.0.6: `user/070-whats-new-existing-account` (an account from
    before 1.0.5 whose Setup Wizard was closed with the window's X is not taken for a new one – "What's new" shows).
    1.0.7: `080-power-key` (start the power button service right away instead of after the next restart),
    `090-python-bytecode` (remove the build test's Python bytecode from `/usr/local/bin`). 1.1: `100-initramfs-dep`
    (a small initramfs, `MODULES=dep`, tried in a copy first). 1.1.1: `user/110-menus-and-sound-icon` (menus that stay
    open after a slow click, the taskbar's own speaker icon, for accounts whose files were not merged),
    `user/120-store-launcher` (one Software Store icon, not two), `user/130-window-buttons` (rewrite an account's own
    copy of the Openbox theme with the bigger buttons). 1.1.2: `user/140-menu-highlight` (the row under the mouse in
    the account's accent color). 1.2: `110-stray-home` (the image's /home/aaron), `user/150-menu-lang` (the menu in the
    system language), `120-bottles-games` (Bottles may not create ~/Games/umu, #154), `user/160-gtk-accent` (light
    mode = Arc-Lighter and the accent in GTK apps for accounts that chose them, #158). 1.2.1: `130-lock-vt-restart`
    (asks for a restart: only a newly started X server reads the setting that stops Ctrl+Alt+F7 at the lock screen).
  - **Files the system changes itself:** tools never write into package files under `/etc/skel` (or other conffiles)
    for everyday settings – a changed conffile is kept by dpkg and the edition tool forever. Per-account changes go
    into the home copies (merged by the edition tool), see `office-menu` below.
- `/usr/lib/os-release` belongs to base-files: the package diverts Debian's copy (`dpkg-divert --package simpleos`,
  Debian's goes to `os-release.debian`); hook 13 only checks it.
- Releasing an edition: `./tools/release.sh version X.Y.Z`, commit **and push**, `./build_iso.sh`, test
  (`TESTING.md`), `./tools/release.sh sign`, `./tools/release.sh publish` (draft first, checks that all repository
  files are attached and the signature matches the key in the image, only then "latest"; never an older or equal
  version). The tag `vX.Y.Z` is set on exactly the local commit (`--target`); `publish` refuses a commit that is not
  on GitHub yet – without that, GitHub tagged the newest commit of its default branch, and the release's source code
  could differ from the ISO.
  **Every** release must carry the repository – `publish` refuses otherwise, also with uncommitted changes in
  `config/`/`tools/` (the next edition only recognizes file versions that are in git) or an `output/repo` that is not
  from the ISO build (marker `output/repo/.in-iso`, written by `build_iso.sh`).
  `build_iso.sh` also records the commit it built and whether `config/` and `tools/` were clean (`output/repo/.build-state`);
  `publish` refuses a build from uncommitted files and any change in `config/`/`tools/` after the build (the ISO and the
  update package would not contain what the tag's source code does). Back up the signing key
  (`~/.local/share/simpleos-release/gnupg`): installed systems only trust that key.
- A new Debian base (Debian 13) is a bigger step than an edition update and is not covered by this.

## How we work

- **`main` is the published edition, pushed with a release.** Between releases nothing new goes to `main` on GitHub,
  so it always matches what installed systems run. The release tags (`v1.0.3` …) always match exactly what was
  published. Release day: `git push`, then build, test, `sign`, `publish`.
- **`next` is the branch for the next release** – at the moment the fixes for **1.2.2**.
  It is pushed as the work goes on; on release day `next` is merged into `main` and released from there.
  Details: [`docs/MAINTAINING.md`](MAINTAINING.md#7-branches).
- **Website** (freakysneaky787.github.io, its own repository): updated after every release – version, download, roadmap.
- **Issues and the project board follow the work, not the push:** when something is done and tested without hardware, its issue
  is closed (comment: "done, ships in X.Y.Z") and its board item set to Done – even before the release. What still needs a
  real computer stays open as a "Verify …" issue.
- Plan and cadence: `ROADMAP.md`; what to test before a release: `TESTING.md`; the whole release and maintenance work
  (signing key, issues, website) in one place: [`docs/MAINTAINING.md`](MAINTAINING.md).

## Structure

```
simple-os/
├── build_iso.sh, test_vm.sh, test_installed_vm.sh   entry points
├── LICENSE, RELEASE_NOTES.md, TESTING.md            GPL-3.0, download text, release checklist
├── Containerfile                                   build environment (Debian bookworm + live-build)
├── docs/                DEVELOPING.md (this file), TOOLS.md, MAINTAINING.md, HARDWARE.md, screenshots/
├── docs/sos-banner.png   README banner (tools/gen_branding.py --readme docs)
├── po/                  translations of the tools (#43): simpleos.pot, de.po – tools/i18n.py extract / check / build
├── tools/
│   ├── lb_config.sh      lb config + build-time parts (branding, fastfetch download, rofi, edition package)
│   ├── build_deb.sh      edition package "simpleos" + APT repository files in output/repo
│   ├── build_rofi.sh     Debian's rofi with our patches in rofi/ (#144), cached in build/downloads/rofi
│   ├── managed_history.py  every git version of the managed files (edition tool: "unchanged?")
│   ├── release.sh        signing key, sign output/repo, GitHub release
│   ├── qemu-test.sh      automatic boot test of the ISO in QEMU, BIOS + UEFI (#124; before publish)
│   ├── i18n.py           translations without the gettext tools: extract, check, build the .mo (#43)
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
| `usr/local/bin/simpleos-update` | system updates: check after login and every 12 hours (`--watch`), "Install" notification, Rofi window, pkexec helper `--upgrade`/`--refresh` (checking without a password), restart only after asking |
| `usr/local/lib/simpleos/office-menu` | office entries (LibreOffice, ONLYOFFICE) in the account's Openbox menu for exactly what is installed; at every sign-in (`etc/X11/Xsession.d/81simpleos-office-menu`), after the Setup Wizard and the Software Center |
| `usr/local/bin/simpleos-usb-notify` | USB notifications for udiskie ("'STICK' is ready" – a click opens the file manager) |
| `usr/local/lib/simpleos/common.sh` | shared helpers of the Rofi tools: log, notifications, Rofi with grab retry, menu with actions |
| `etc/apt/apt.conf.d/20simpleos-periodic` | refresh package lists daily (check only, never install automatically) |
| `usr/local/sbin/simpleos-efi-refresh` | keeps shim + signed GRUB in `EFI/Simple_OS` on the EFI partition at the installed packages' version (Debian's postinst only refreshes `EFI/<GRUB_DISTRIBUTOR>`) and creates the fallback loader `EFI/BOOT/BOOTX64.EFI` if none exists; called by the package's postinst/dpkg trigger (`/usr/lib/shim`, `/usr/lib/grub/x86_64-efi-signed`) and by `simpleos-post-install` |
| `usr/sbin/bootloader-config` | replaces Debian's Calamares script: installs GRUB (BIOS/UEFI) offline from `usr/share/simpleos/bootloader-debs` (hook 08) |
| `usr/local/sbin/simpleos-post-install` | runs after the installation (Calamares): removes the installer and live leftovers, language packs |
| `usr/local/lib/simpleos/sfdisk-installer` | live session only (put in front of `/usr/sbin/sfdisk` by `simpleos-live-tune`): "Install alongside" inside an extended partition – moves the new logical partition's start past its EBR; keeps the active primary partition when Calamares marks a logical one |
| `etc/default/grub.d/simpleos-os-prober.cfg` | os-prober on (other systems in the GRUB menu); here because grub-pc/grub-efi switch a line in `/etc/default/grub` off at every update |
| `usr/local/lib/simpleos/open-as-user` | live image only: links in the installer (runs as root) open in the live user's browser – browsers refuse to run as root; root's http(s) default from hook 15 |
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

## Translations (#43, since 1.2)

Simple OS's own tools speak the system language (German and French so far, everything else falls back to English). One gettext
domain `simpleos`; `tools/i18n.py` does what the gettext tools would, in pure Python.

- **Python tools:** `_ = gettext.translation("simpleos", fallback=True).gettext` at the top, every shown text in
  `_("…")`. A text with values is a whole sentence with names: `_("Connected to {network}").format(network=…)` – never an
  f-string inside `_()`. Texts that are also keys or compared (wizard steps, Software Center categories) stay English
  in the code with `N_("…")` and are translated where they are shown (`_(name)`). Never use `_` as a throwaway variable
  (`for _ in`, `a, _, b =`, `*_`) in a function that calls `_()`.
- **Shell tools:** `. /usr/local/lib/simpleos/i18n.sh` (or common.sh, which sources it), then `$(_t 'Text')`; with
  values `$(printf "$(_t 'Connected to %s')" "$name")`. `_t` always uses the system language – also in root helpers
  (pkexec has no LANG) and in tools that set `LC_ALL=C` to read command output. Protocol lines that other tools read
  (`ERROR:`, `NOSPACE:`, `OPTIONAL-FAILED:`, `HELD:` …) stay English. Rofi menus answer with the row number
  (`-format i`), never with the translated text.
- **Elsewhere:** `Name[de]`/`Comment[de]` (and `[fr]`) in the launchers, `xml:lang="de"`/`"fr"` in the polkit policies and Thunar's uca.xml, `welcome.de.html` /
  `windows-programs.de.html` (welcome-viewer picks them), `whats-new.de` (the same with `.fr`), the shortcut list in `simpleos-help`, and the
  Openbox menu: `menu-lang` writes `~/.config/openbox/menu-simpleos.xml` at sign-in, which rc.xml loads before the
  English menu.xml. Texts that are not in a tool go into `config/i18n/extra.txt`.
- **Workflow:** after changing texts `./tools/i18n.py extract` (new texts appear in `po/de.po` with an empty msgstr),
  translate them, `./tools/i18n.py check` (everything translated, same placeholders). The build compiles the .mo files
  (`tools/lb_config.sh`); `release.sh publish` refuses incomplete translations. A new language: copy `po/de.po` to
  `po/<code>.po`, empty the msgstr lines, translate.
