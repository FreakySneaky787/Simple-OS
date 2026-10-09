# Simple OS – Roadmap

Where Simple OS is going. It is a plan, not a promise: dates move, the order follows what real users run into.
Written after 1.0.3 (2026-10-09). What is already done is in `RELEASE_NOTES.md`; what to test before a release is in
`TESTING.md`.

## How we release

| Kind | When | What goes in |
|---|---|---|
| **Hotfix** (1.0.x) | within days | only what breaks starting, installing, data or security, or a core function (Wi-Fi, sound, login) |
| **Point release** (1.0.x, 1.1.x) | every 3–4 weeks | everything collected below, bundled; one restart for the users |
| **Minor release** (1.1, 1.2 …) | about every 3 months | new features |
| **New ISO** | with a minor release, or when the installer / hardware detection changed | everyone already installed gets the rest through Software Updates, so a pure update can be published with `./tools/release.sh publish --no-iso` |

Rules that keep it small: no new always-running process without a good reason (the image is built without Recommends
on purpose); every fix gets a test in `config/hooks/live/99_verify_simpleos.hook.chroot`; anything that mocks can hide
(night light in 1.0.3!) is run for real once, e.g. in a container with Xvfb; nothing is published untested on hardware.

## Now: verify 1.0.3 on real hardware (feeds the next point release)

These could only be tested without hardware. Tick them off on the ThinkPad E16 / ThinkBook and report in the issues.

- [ ] Night light turns the screen warm (before: nothing happened on real hardware).
- [ ] Microphone appears in Sound (alsa-ucm-conf; before only "stereo-fallback" with no input).
- [ ] Plugging in an HDMI/USB-C monitor lights it up on its own; unplugging leaves the laptop screen; standby of a DisplayPort
      monitor does not re-arrange the desktop.
- [ ] Mouse & Touchpad page: natural scrolling, tap, speed apply and survive a restart (Synaptics touchpad of the E16).
- [ ] Date & Time: time zone dialog and automatic time ask for the password and apply.
- [ ] Language packs: install in German with internet → Firefox and the dictionary are German; offline → they follow with Software Updates.
- [ ] The keyring: no "new keyring" prompt in Chromium/Discord. (`gkr-pam: unable to locate daemon control file` in the
      lightdm journal – harmless or not?)
- [ ] Update from 1.0.2 to 1.0.3 through Software Updates on an installed system.

## 1.0.4 – next point release (about 3–4 weeks after 1.0.3)

Small, safe, mostly things users hit in the first hour.

| Item | Why | Effort |
|---|---|---|
| Fixes from the checklist above | whatever turns out broken | ? |
| Brightness slider in Control Center → Display | Fn keys do not exist on every keyboard; the OSD already knows how | S |
| Idle screen lock + blank (issue #25) | no lock after leaving the laptop; check xfce4-power-manager vs `simpleos-power`, add a screensaver inhibit for video | M |
| Power button | pressing it shuts down at once; ask first / open the power menu (needs a hardware test of what X sees) | S–M |
| `git` in the image | first tool many tutorials ask for; 45 MB, decide | S |
| Bluetooth battery level of headphones | BlueZ needs `--experimental`; nice in the taskbar | S |
| "Default apps" page (browser, mail, PDF …) | today only the browser has a chooser | M |
| Startup apps page | enable/disable autostart entries without the terminal | M |
| Wi-Fi: regulatory country from the time zone | the chip guessed NL for a Swiss user | S |

## 1.1 – next minor release (about 3 months)

- **HiDPI / display scaling** – the biggest gap: nothing scales today (no Xft/DPI, no GDK scale, tint2/Openbox use
  pixels). On a 2.8K/4K laptop everything is tiny. Plan: a "Scale" setting in Control Center → Display (100/125/150/200 %)
  that sets Xft.dpi, XSETTINGS (also cursor size), GDK scale for 200 %, Rofi/dunst/kitty sizes and the tint2 panel height;
  automatic default from the screen's real DPI. Needs a HiDPI test screen first (open question: the resolution of the
  development laptop).
- **Language & Region page** (system language, formats) and German/other translations of Simple OS's own tools (all English today).
- **Webcam / camera test** app (the camera works, but there is nothing to try it with).
- **Calendar** (clock click in the taskbar opens a month view).
- **Dual-boot polish:** tell the user about Windows "fast startup" (NTFS mounted read-only), RTC in local time.
- **Boot time & size:** initramfs `MODULES=dep` (113 MB → much smaller, faster boot), AppArmor profiles, zstd squashfs
  (issue #19: faster live session and install, ISO +18 %).
- **Hardware tests still missing:** NVIDIA desktop with the driver, AMD laptop, dual boot with Windows, Secure Boot on.

## 2.0 – Debian 13 "trixie"

Simple OS is built on Debian 12 "bookworm", which moved from the regular security team to Debian LTS in June 2026
(supported until June 2028 – please re-check the dates). Debian 13 has been the stable release since August 2025.
Moving to it is the one big job of the next year, and it has to be planned, not rushed:

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

- Automatic security updates as an option (today: a notification, you click Install).
- Fingerprint reader support (`fprintd`) and a setup page.
- Accessibility: screen reader, large cursor, high-contrast theme in Appearance.
- Printer/scanner setup screenshots in the help; a built-in "Get help" that links to the project page.
- A small web page for the project (download, checksums, screenshots, FAQ).
- Continuous build check on GitHub (build the ISO in CI and run the verify hook on every push; needs a runner that can do `lb build`).
- arm64 image (Raspberry Pi / Apple-less ARM laptops) – large work, low priority.
- Crash/problem reports: a one-click "send to GitHub" option next to the saved file (privacy first).

## Open issues

| # | Title | Status |
|---|---|---|
| 10 | Bluetooth pairing for keyboards/phones (passkey) | fixed in 1.0.2 through blueman's agent; still to be confirmed with a real keyboard and phone |
| 19 | squashfs uses xz; zstd would be faster | 1.1, decide about the +18 % ISO size |
| 25 | screen blanking conflicts / no screensaver inhibit | 1.0.4 |

## Decisions we have made (so we don't argue them again)

- Debian stable base + backports only for kernel/firmware/microcode; no own repository for apps (Flatpak/Flathub instead).
- Openbox on X11, no Wayland for now – everything (night light, screenshot, clipboard, snapping) is built for X11.
- English interface; translations come later and must not bloat the image.
- Updates through APT from the signed GitHub release repository; the release key backup lives outside the repo.
