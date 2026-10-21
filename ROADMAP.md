# Simple OS – Roadmap

Where Simple OS is going. It is a plan, not a promise: dates move, the order follows what real users run into.
Written after 1.0.3 (2026-10-09), updated 2026-10-14 for 1.0.4 and 2026-10-17 for 1.0.5 and 1.0.6. What is already done is in `RELEASE_NOTES.md`; what to test before a release is in
`TESTING.md`.

## How we release

| Kind | When | What goes in |
|---|---|---|
| **Hotfix** (1.0.x) | within days, when needed | only what breaks starting, installing, data or security, or a core function (Wi-Fi, sound, login) |
| **Bugfix release** (1.0.x, 1.1.x) | every 2–3 weeks | everything collected below, bundled; one restart for the users |
| **Feature release** (1.1, 1.2 …) | every 2–3 months | new features |
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

## 1.0.6 – next bugfix release (planned for Saturday, 2026-11-07)

Milestone "1.0.6" on GitHub. Probably an update without a new ISO (`publish --no-iso`), unless the installer changes.

| Item | Status |
|---|---|
| Whatever 1.0.5 users report (Pax's Dell test, #64) | waiting |
| `build_iso.sh`: a docs commit during the build marks it dirty (#72) | open |
| `release.sh sign`: `output/repo` belongs to root after the build (#71) | open |

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

## 1.1 – next feature release (2–3 months after 1.0)

- **HiDPI / display scaling** (#41) – the biggest gap: nothing scales today (no Xft/DPI, no GDK scale, tint2/Openbox use
  pixels). On a 2.8K/4K laptop everything is tiny. Plan: a "Scale" setting in Control Center → Display (100/125/150/200 %)
  that sets Xft.dpi, XSETTINGS (also cursor size), GDK scale for 200 %, Rofi/dunst/kitty sizes and the tint2 panel height;
  automatic default from the screen's real DPI. Needs a HiDPI test screen first (open question: the resolution of the
  development laptop).
- **Language & Region page** (system language, formats) (#42) and German/other translations of Simple OS's own tools (all English today) (#43).
- **Webcam / camera test** app (the camera works, but there is nothing to try it with) (#44).
- **Users & accounts page** in Control Center: create, delete and switch users, change passwords and pictures, administrator or standard user, automatic login (#68).
- **Boot time & size:** initramfs `MODULES=dep` (113 MB → much smaller, faster boot) (#47), AppArmor profiles (#48), zstd squashfs
  (issue #19: faster live session and install, ISO +18 %).
- **Hardware tests still missing:** NVIDIA desktop with the driver, AMD laptop, dual boot with Windows, Secure Boot on (#49).

## 1.2 – feature release after 1.1

- **Windows programs** (#85): double-click on a `.exe`/`.msi` offers to run it with Bottles (installed from the Software
  Store if missing), a plain help page on what works (older programs, many games through Steam/Proton) and what doesn't
  (Microsoft 365, current Adobe apps, kernel anti-cheat) with alternatives, and a hint to Steam's own "Steam Play for
  all titles" switch. Not planned: automatic Windows VMs, CrossOver, our own configs for Windows apps.

## 2.0 – Debian 13 "trixie"

Simple OS is built on Debian 12 "bookworm", which moved from the regular security team to Debian LTS in June 2026
(supported until June 2028 – please re-check the dates). Debian 13 has been the stable release since August 2025.
Moving to it is the one big job of the next year, and it has to be planned, not rushed (issues #50–#53):

- **Why:** newer kernel and Mesa without backports, newer firmware for new laptops, Firefox ESR / LibreOffice / PipeWire
  versions that bookworm will not get, no more `bookworm-backports` pinning for the kernel, fewer special cases.
- **What breaks:** every package list entry, the `simpleos-drivers` NVIDIA logic (driver versions), picom/dunst/rofi
  options, GTK/WebKit versions used by our Python tools, `gammastep`/`nmcli` behaviours (as the night light showed),
  the Calamares settings, Secure Boot packages, `live-build` itself. Plan a branch `trixie` built next to `main`.
- **For installed systems:** an in-place `dist-upgrade` from Software Updates is possible but risky (third-party sources,
  Flatpak, NVIDIA DKMS, backups). Options to decide: (a) a guided "Upgrade to Simple OS 2.0" tool with a restore point and
  checks, (b) a fresh install with a documented migration of the home folder. Probably (a) after a long beta.
- **Timeline sketch:** branch + first trixie ISO as a preview in Q1 2027, public beta in Q2, 2.0 when the upgrade
  tool has been run on several real machines.

## Ideas, not scheduled

- Automatic security updates as an option (today: a notification, you click Install) (#54).
- Fingerprint reader support (`fprintd`) and a setup page (#55).
- Accessibility: screen reader, large cursor, high-contrast theme in Appearance (#56).
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

- Debian stable base + backports only for kernel/firmware/microcode; no own repository for apps (Flatpak/Flathub instead).
- Openbox on X11, no Wayland for now – everything (night light, screenshot, clipboard, snapping) is built for X11.
- English interface; translations come later and must not bloat the image.
- Updates through APT from the signed GitHub release repository; the release key backup lives outside the repo.
