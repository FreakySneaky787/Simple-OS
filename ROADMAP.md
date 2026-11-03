# Simple OS – Roadmap

Where Simple OS is going. It is a plan, not a promise: dates move, the order follows what real users run into.
Written after 1.0.3 (2026-10-09), updated 2026-10-14 for 1.0.4, 2026-10-17 for 1.0.5, 2026-10-24 for 1.0.6 and 2026-10-25 for 1.0.7 (this copy on the branch `trixie` follows the work on 2.0 "Rigi"; 2.x plan 2026-11-03). What is already done is in `RELEASE_NOTES.md`; what to test before a release is in
`TESTING.md`.

## How we release

| Kind | When | What goes in |
|---|---|---|
| **Hotfix** (1.0.x) | within days, when needed | only what breaks starting, installing, data or security, or a core function (Wi-Fi, sound, login) |
| **Bugfix release** (1.0.x, 1.1.x, 1.2.x) | every 2–3 weeks | everything collected below, bundled; one restart for the users |
| **Feature release** (1.1, **1.2 – the last one**) | every 2–3 months | new features. **After 1.2 there are no more feature releases of 1.x** (see "After 1.2") |
| **Big release** (2.0, 3.0 …) | only with a new Debian version | new base system, new ISO, upgrade path |
| **New ISO** | with a feature or big release, or when the installer / hardware detection changed | everyone already installed gets the rest through Software Updates, so a pure update is published with `./tools/release.sh publish --no-iso` |

Rules that keep it small: no new always-running process without a good reason (the image is built without Recommends
on purpose); every fix gets a test in `config/hooks/live/99_verify_simpleos.hook.chroot`; anything that mocks can hide
(night light in 1.0.3!) is run for real once, e.g. in a container with Xvfb; nothing is published untested on hardware.

## Done: 1.0.3 verified on real hardware (fed 1.0.4)

These could only be tested without hardware at first; all checked on the ThinkPad E16 / ThinkBook or in a VM.

- [x] Night light turns the screen warm (before: nothing happened on real hardware).
- [x] Microphone appears in Sound (alsa-ucm-conf; before only "stereo-fallback" with no input).
- [x] Plugging in an HDMI/USB-C monitor lights it up on its own; unplugging leaves the laptop screen; standby of a DisplayPort
      monitor does not re-arrange the desktop (#28, ThinkBook 2026-10-14).
- [x] Mouse & Touchpad page: natural scrolling, tap, speed apply and survive a restart (Synaptics touchpad of the E16).
- [x] Date & Time: time zone dialog and automatic time ask for the password and apply (#30, VM 2026-10-14; Cancel no
      longer shows an error – fixed in 1.0.4).
- [x] Language packs: install in German with internet → Firefox and the dictionary are German (#31, VM 2026-10-14: they were
      never installed and the language itself was never generated – both fixed in 1.0.4).
- [x] The keyring: no "new keyring" prompt in Chromium/Discord (#32, VM 2026-10-14: it came in the first session after the
      installation – fixed in 1.0.4; the `gkr-pam: unable to locate daemon control file` line is harmless).
- [x] Update from 1.0.2 to 1.0.3 through Software Updates on an installed system (#33, works).

## 1.0.4 – bugfix release (published 2026-10-14)

Small, safe, mostly things users hit in the first hour. Published **with a new ISO**
(`./tools/release.sh publish`): the installer changed (#62, #64 – one installer only, no switching off while it works,
"remove the USB stick" before the restart).

| Item | Status |
|---|---|
| Fixes from the checklist above (#30, #31, #32: language, language packs, first-login keyring, Date & Time) | done |
| Idle screen lock + blank, video inhibit (#25) | done |
| Power button opens the power menu (#35) | done – ThinkBook: hold ~1 s, the firmware ignores a quick tap |
| Brightness slider in Control Center → Display (#34) | done |
| Wi-Fi: regulatory country from the time zone (#40) | done |
| `git` in the image (#36) | done |
| Sixth bug hunt (nmcli in other languages, Task Manager, light-mode icons, small screens, report privacy) | done |
| App menu / search: typed text readable (#61) | done |
| Installer safety: one installer, no switching off while it works, "remove the USB stick" (#62, #64) | done, VM-tested (BIOS, UEFI + Secure Boot) |
| Setup Wizard: internet step skipped when online, simpler Wi-Fi page (#63) | done |
| Older PCs (BIOS/MBR): "Install alongside" inside an extended partition, active partition kept | done, VM shaped like a Dell OptiPlex 9020 |
| Other systems stay in the GRUB menu after GRUB updates | done |
| Bluetooth pairing with a keyboard/phone (#10), monitor hotplug (#28) | confirmed on the ThinkBook |

## 1.0.7 – bugfix release (published 2026-10-30)

Milestone "1.0.7" on GitHub (all 7 issues closed). Published **with a new ISO** (`./tools/release.sh publish`): built
2026-10-25 from 01b79b4 (SHA-256 7fa408ff…), tested on the ThinkPad E16 (TESTING.md section 12) and in a VM (update
from 1.0.6, update with an almost full disk).

| Item | Status |
|---|---|
| Refresh rates: one "60 Hz" instead of "60 Hz" and "59.95 Hz" (#78, ThinkPad E16) | done (d8c6eaa), confirmed on the E16 |
| Dates in the language's own order: calendar header, clock tooltip, taskbar clock (#81) | done – order from glibc's date_fmt (`date-formats`), VM de_CH "So, 25. Okt", also the clock of the login/lock screen (`greeter-screen`) |
| Software Updates: check free disk space before installing (#91) | done – apt's own summary + 300 MB reserve, nothing changed when too little, Storage Cleaner offered; VM with a really full disk: "NOSPACE", nothing changed |
| Ninth bug hunt on 1.0.6 | done 2026-10-24: #96–#99 below; verify hook fixed for #78 (c561446) |
| Sleep locks the screen two or three times, each extra lock restarts the login screen (#96, #88 follow-up) | done – VM: one lock per sleep (power menu, lid, lid while locked); real sleep confirmed on the E16 |
| Power button on the lock screen shuts down at once (#97) | done – `simpleos-power-key` service: lock screen → sleep, nobody signed in → shut down; VM and E16 checked |
| A keyboard connected later gets the system layout, not the account's (#98) | done – VM: hotplugged USB keyboard gets the account layout |
| Python bytecode from the build tests in the image (#99) | done – hook 99 cleans up, migration 090 for installed systems |
| Whatever 1.0.6 users report | nothing reported |

## 1.0.6 – bugfix release (published 2026-10-24)

Milestone "1.0.6" on GitHub. Published **with a new ISO** (`./tools/release.sh publish`): the installer changed (#73,
hardware clock after a dual-boot install without internet).

| Item | Status |
|---|---|
| Whatever 1.0.5 users report (Pax's Dell test, #64) | nothing came before the release; #88 came from our own test on the E16 |
| Control Center → Wi-Fi shows no networks since 1.0.4 (#76) | done – its own view (list online and offline, Disconnect); the build's GUI self-test now really runs (a test dummy had hidden it since 1.0) |
| Closing the Software Center stops an installation halfway (#83) | done – the window hides, the installation finishes, then a notification; one instance; Browser Selector without a terminal |
| Default app for documents, spreadsheets, presentations (#75) | done – Control Center → Apps |
| Identical "60 Hz" refresh rates (#78), search calculates dates (#82) | done |
| "What's new" skipped after closing the wizard with X (#79) | done – user migration 070 for accounts from before 1.0.5 |
| Text fixes (#80) | done – all old menu/Control Center paths, shortcut list in line (with PR #84's lines) |
| Dual-boot install offline: clock off by the UTC offset (#73) | done – offline UEFI install next to a (fake) Windows in a VM with the RTC in local time: right time; the 1.0.5 script in the same setup: 2 h off |
| After the automatic screen lock, unlocking gives a black screen (#88) | done – xss-lock no longer locks again while the lock screen is in front (`simpleos-power --lock-now`); reproduced and fixed in a VM |
| `build_iso.sh`: a docs commit during the build marks it dirty (#72); `release.sh sign`: `output/repo` belongs to root (#71) | done |
| `release.sh publish`: the new tag never reaches the local clone (#77) | done – fetched after publishing; `check_skel_merge` picks the release tag by version and warns about a gap |

## 1.0.5 – bugfix release (published 2026-10-17)

Moved from 1.0.4 to keep it small, plus what came up since:

| Item | Status |
|---|---|
| Bluetooth battery level of headphones (#37) | done – `bluetoothd --experimental` (drop-in), Control Center + flyout; tested with real headphones; updates ask for a restart (migration 060) |
| "Default apps" page (browser, mail, PDF …) (#38) | done – Control Center → Apps |
| Startup apps page (#39) | done – Control Center → Apps |
| "What's new" window after an update (#65) | done – `simpleos-whats-new`, notes in `usr/share/simpleos/whats-new` |
| Clearer menus: right-click menu in Apps / Settings / Tools / Help, Control Center split into smaller pages, duplicate launchers hidden | done |
| Calendar: clicking the clock shows the month (#45) | done – `simpleos-calendar` |
| Dual boot: clock like Windows, fast-startup hint (#46) | done – new installs next to Windows: local time; Control Center → Date & Time |
| Whatever 1.0.4 users report (Pax's Dell test, #64) | nothing came before the release – moved to 1.0.6 |
| y/z swapped in search/app menu with Swiss/German keyboards (ThinkPad test) | done – XTEST keyboard gets the real layout |

## 1.1 – next feature release (planned around 2026-11-07)

Bugfix releases (1.0.x) come in between when users report something. Kept to what fits in about two weeks; the
rest moved to 1.2.

- **HiDPI / display scaling** (#41) – the biggest gap: nothing scales today (no Xft/DPI, no GDK scale, tint2/Openbox use
  pixels). On a 2.8K/4K laptop everything is tiny. Plan: a "Scale" setting in Control Center → Display (100/125/150/200 %)
  that sets Xft.dpi, XSETTINGS (also cursor size), GDK scale for 200 %, Rofi/dunst/kitty sizes and the tint2 panel height
  and clock font (also a "Large" taskbar size – asked for on Bluesky, the clock is too small for older eyes);
  automatic default from the screen's real DPI. Needs a HiDPI test screen first (open question: the resolution of the
  development laptop).
- **Language & Region page** (system language, formats) (#42).
- **Boot time & size:** initramfs `MODULES=dep` (113 MB → much smaller, faster boot) (#47), zstd squashfs
  (#19: faster live session and install, ISO +18 %).
- **Webcam / camera test** app (the camera works, but there is nothing to try it with) (#44).
- On the side, as far as hardware is at hand: **hardware tests** (NVIDIA desktop with the driver, AMD laptop, dual boot
  with Windows, Secure Boot on) (#49) and a public hardware compatibility page (#92).

## 1.2 – feature release after 1.1

- **Translations** of Simple OS's own tools (all English today) (#43).
- **Users & accounts page** in Control Center: create, delete and switch users, change passwords and pictures, administrator or standard user, automatic login (#68).
- **AppArmor** profiles (#48).
- **Windows programs** (#85): double-click on a `.exe`/`.msi` offers to run it with Bottles (installed from the Software
  Store if missing), a plain help page on what works (older programs, many games through Steam/Proton) and what doesn't
  (Microsoft 365, current Adobe apps, kernel anti-cheat) with alternatives, and a hint to Steam's own "Steam Play for
  all titles" switch. Not planned: automatic Windows VMs, CrossOver, our own configs for Windows apps.

## After 1.2 – bugfixes only, the port starts slowly

**Decision (2026-11-02): 1.2 is the last feature release of 1.x.** From then on 1.2.x only gets fixes, and the work goes
into the Debian 13 port. Why: 1.x runs on Debian 12, whose regular security support ended on 12 July 2026; Debian LTS
covers it until 30 June 2028 ([debian.org](https://www.debian.org/News/2026/20260712.en.html),
[release page](https://www.debian.org/releases/oldstable/)). That is enough time for a careful port – and every new
feature on the old base would have to be ported again.

What is allowed in 1.2.x:
- fixes for bugs, hardware that does not work, security and data safety (the hotfix and bugfix rules above);
- **the preparations for 2.0 that must reach 1.x systems first:** the separate update channel per Debian base (#106, so a
  Debian 12 system is never offered the Debian 13 package, see "2.0" below) and, later, the hint and entry point for
  the upgrade tool (#52). These are the only "features" allowed, and only because 2.0 depends on them.

What is not: new Control Center pages, new apps, new settings. Ideas that come in go to "Ideas, not scheduled" or to
2.x. Whatever 1.1/1.2 do not finish moves to 2.x as well – nothing is stretched to squeeze it into 1.2.

What goes into 2.0 (decided 2026-11-03): **the new base and nothing that is not needed for it** – plus everything 1.x
has by then. In detail:
- **every feature 1.x has – all of 1.1 and 1.2** (HiDPI scaling #41, Language & Region #42, faster boot #47/#19, camera
  test #44, translations #43, Users & accounts #68, AppArmor #48, Windows programs #85 …) **and every 1.x bugfix**: `main`
  is merged into `trixie` regularly, and once more before the preview ISO, the beta and the release, so 2.0 never lacks
  a feature or a fix that 1.x has;
- the Rigi look (peach accent, wallpaper, logo colors);
- the upgrade tool (#52) and the update channels (#106);
- the simpler partitioning page in the installer (#101), because the installer is ported anyway.
New things that 1.x does not have (#89 backups of personal files, #56 accessibility, Wayland #87 …) come in 2.1 and
later (see "2.x" below).

Support of 1.x after 2.0: **no fixed end date.** 1.2.x keeps getting fixes as long as people use it; the hard limit is
Debian's own security support for Debian 12 (Debian LTS until 30 June 2028).

How the port goes, in small steps (each step ends with something that builds and can be tested):

| Phase | When | What |
|---|---|---|
| 0. Prepare (#107) | during 1.1 and 1.2 | keep every new thing portable (no Debian-12-only tricks), collect the list of what breaks (picom/dunst/rofi options, NVIDIA, Calamares, Secure Boot, gammastep, live-build); no changes to the base yet |
| 1. First build (#50) | right after 1.2 | `lb_config.sh` on `trixie`, package lists, no backports pins; the build runs and the ISO starts in a VM (#50) |
| 2. Make it work (#51) | after the first build | the verify hook (`99_verify_simpleos`) green again, then the tools one by one: theme, display, drivers, installer, updates |
| 3. Preview ISO (#50) | planned Q1 2027 – moves if 1.2 takes longer | public preview with real 2.0 screenshots, hardware tests |
| 4. Upgrade tool and beta (#52, #106, #53) | planned Q2 2027 | "Upgrade to Simple OS 2.0" with a restore point (#52), channel split live, tested on several real machines |
| 5. 2.0 (#53) | when 4 has run cleanly | release; 1.2.x keeps getting fixes after it, with no fixed end date (see above) |

## 2.0 "Rigi" – Debian 13 "trixie"

**Status (2026-10-24):** branch `trixie` created, the texts (README, RELEASE_NOTES, TESTING) describe 2.0 already; the
code is still the one of 1.0.7 – the port has not started yet (#50).

Simple OS 1.x is built on Debian 12 "bookworm", which moved from the regular security team to Debian LTS on 12 July 2026
(LTS supported until 30 June 2028, [debian.org](https://www.debian.org/releases/oldstable/)). Debian 13 has been the stable release since August 2025.
Moving to it is the one big job of the next year, and it has to be planned, not rushed (issues #50–#53):

- **Why:** newer kernel and Mesa without backports, newer firmware for new laptops, Firefox ESR / LibreOffice / PipeWire
  versions that bookworm will not get, no more `bookworm-backports` pinning for the kernel, fewer special cases.
- **What breaks:** every package list entry, the `simpleos-drivers` NVIDIA logic (driver versions), picom/dunst/rofi
  options, GTK/WebKit versions used by our Python tools, `gammastep`/`nmcli` behaviours (as the night light showed),
  the Calamares settings, Secure Boot packages, `live-build` itself. The work happens on the branch `trixie` (since
  2026-10-24), next to `main`.
- **Update channel:** 1.x systems follow `releases/latest`. If 2.0 simply became "latest", every Debian 12 system would
  be offered the Debian 13 package. Before 2.0 is published: one channel per Debian base (e.g. the 1.x source pinned
  to the newest 1.x release), shipped to 1.x in a last 1.x update; 2.0 reaches 1.x only through the upgrade tool (#106).
- **For installed systems:** an in-place `dist-upgrade` from Software Updates is possible but risky (third-party sources,
  Flatpak, NVIDIA DKMS, backups). **Decided (2026-11-03): (a)** a guided "Upgrade to Simple OS 2.0" tool with a restore point and
  checks, after a long beta (#52); (b) a fresh install with a documented migration of the home folder stays only the fallback.
- **Timeline sketch:** branch + first trixie ISO as a preview in Q1 2027, public beta in Q2, 2.0 when the upgrade
  tool has been run on several real machines.
- **Codename: Rigi** ("REE-gee", the "Queen of the Mountains") – one per big release, Swiss mountains.
  Ideas for 3.0 and later in [docs/CODENAMES.md](docs/CODENAMES.md).

## 2.x – feature releases after 2.0

2.0 "Rigi" brings only the new base. New features start with 2.1, one theme per release, every 2–3 months like the 1.x
feature releases. The order may change with what users report; hardware support is not a release of its own – it
grows with every release (#49, the hardware compatibility page).

### 2.1 – keep your data safe

- **Backups of personal files** (#89) – today the restore points (Timeshift) only cover the system.
- **Recovery assistant** (#108): "Simple OS – restore" in the boot menu, to bring back a restore point when the
  desktop no longer starts.
- **Update scheduling** (#109): install updates when shutting down or at a set time, together with the option for
  automatic security updates (#54).
- **Clipboard history with images and pinned entries** (#110).
- Small: make the split view of the file manager (Thunar, F3) visible in its menu and the help.

### 2.2 – usable for everyone

- **Accessibility** (#56): screen reader, large cursor, high-contrast theme in Appearance.
- **Fingerprint reader** (`fprintd`) and a setup page (#55).
- **Wayland session with labwc, preview** (#87): an extra login session "Simple OS (Wayland, preview)" next to the X11
  default; the tools move over one by one (taskbar, idle/lock, displays, clipboard, screenshots, night light, menus).
  Not in any 2.0.x release – never change the base and the desktop in the same release.

### 2.3 – tools

- **Wayland becomes the default** (#87) once everything works; X11 stays as a fallback for a while.
- **Screenshot editor** (#111): arrows, text, crop and blur. Here and not earlier because the screenshot tool uses
  `maim` (X11 only) and has to be rebuilt for Wayland anyway – the editor is built once, on the new tool.
- **RGB lighting and game controllers** (#112, optional): no own RGB tool – OpenRGB recommended in the Software Store;
  controllers work out of the box and show their battery level.

### Three areas

The work is sorted into three areas, also as labels on GitHub (`core`, `desktop`, `tools`):

| Area | What belongs to it |
|---|---|
| **Simple OS Core** – the foundation | system, kernel, updates, security, drivers, installer, recovery |
| **Simple OS Desktop** – using it | Control Center, taskbar, file manager, search, notifications, windows |
| **Simple OS Tools** – the helpers | backups, cleaner, Software Store, hardware, screenshots, diagnostics |

## Ideas, not scheduled

- Own **Simple OS Software Store** (#86): the whole Flathub catalogue in the Simple OS style, replacing Bazaar/GNOME
  Software – grown step by step from today's Software Center, no extra multi-GB runtime.
- Printer/scanner setup screenshots in the help; a built-in "Get help" that links to the project page.
- Continuous build check on GitHub (build the ISO in CI and run the verify hook on every push; needs a runner that can do `lb build`) (#58).
- arm64 image (Raspberry Pi / Apple-less ARM laptops) (#59) – **not planned**; if at all, most likely not before the 2.x
  versions, and even then unlikely.
- Crash/problem reports: a one-click "send to GitHub" option next to the saved file (privacy first) (#60).

## Open issues

| # | Title | Status |
|---|---|---|
| 19 | squashfs uses xz; zstd would be faster | 1.1, decide about the +18 % ISO size |

## Decisions we have made (so we don't argue them again)

- Debian stable base + backports only for kernel/firmware/microcode (with Debian 13 none are planned); no own repository for apps (Flatpak/Flathub instead).
- Openbox on X11 for all 1.x and 2.0.x releases – everything (night light, screenshot, clipboard, snapping) is built for
  X11. Wayland comes after 2.0.x via labwc: first as a preview session, then the default later in 2.x (#87).
- English interface; translations come later and must not bloat the image.
- Updates through APT from the signed GitHub release repository; the release key backup lives outside the repo.
