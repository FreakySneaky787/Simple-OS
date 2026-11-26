# Hardware compatibility

Simple OS doesn't promise to run on every computer. This page lists the computers it is **known** to work on –
tested by us or reported by people who use it – and what didn't work. Your computer isn't listed? It may still work.
Try the live session from the USB stick first, it changes nothing on the computer. Then
[tell us how it went](#report-your-computer), so the next person knows.

Last updated: 26 November 2026 (Simple OS 1.1.2).

## Tested computers

**Yes** works · **Partly** works, with a limitation in the notes · **No** doesn't work · **–** not tested yet

| Computer | Firmware | Version | Install | Wi-Fi | Sound | Graphics | Brightness | Suspend | External monitor |
|---|---|---|---|---|---|---|---|---|---|
| Lenovo ThinkPad E16 Gen 3 (21TF) – Intel Core 5 210H, Intel graphics, Intel Wi-Fi | UEFI, Secure Boot off | 1.0.7, 1.1, 1.1.1, 1.1.2 | Yes | Partly | Yes | Yes | Yes | Yes | Yes |
| Self-built desktop – AMD Ryzen 5 5600X, NVIDIA GeForce RTX 3050 (8 GB), 16 GB DDR4, Wi-Fi | UEFI, Secure Boot off, next to Windows | 1.1.1 | Yes | Yes | Yes | Yes | – | Yes | Yes |
| Acer Predator – gaming desktop, Intel Core i7 (13th gen), NVIDIA GeForce RTX 4070 Super, 32 GB RAM | UEFI, Secure Boot off, next to Windows | 1.0.7, 1.1.2 | Yes | Yes | Yes | – | Yes | Yes | Yes |
| Samsung Galaxy Book 4 – Intel Core 7 150U, 16 GB RAM | UEFI, Secure Boot on, whole disk | 1.1.2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| ASUS K42JA – laptop from 2010, Intel Core i5-460M, ATI Mobility Radeon HD 5730 | legacy BIOS | 1.1.2 | Yes | – | – | Yes | – | – | – |
| Dell OptiPlex 9020 – desktop | legacy BIOS, MBR, next to another system | 1.0.3 | No | – | – | – | – | – | – |

**ThinkPad E16 Gen 3:** in daily use since Simple OS 1.0. Wi-Fi: with one router the 5 GHz connection (a wide 160 MHz
channel) was slow; setting the network to 2.4 GHz in Control Center → Wi-Fi fixed it. Bluetooth headphones, keyboards
and phones pair. A monitor plugged in later turns on by itself. Suspend and waking up were checked with 1.0.7. 1.1.1 was installed fresh on it before its
release: menus stay open with a firm touchpad click, and the bigger window buttons are easy to hit. 1.1.2 was checked on it before its release too (menus, search, sound menu). The power
button has to be held for about a second – the firmware ignores a quick tap.

**Acer Predator (gaming desktop):** installed next to Windows with 1.0.7 – installing, Wi-Fi, sound, suspend and
an external monitor work. Graphics with 3D (games) and the NVIDIA driver weren't tried yet
([#105](https://github.com/FreakySneaky787/Simple-OS/issues/105)). 1.1.2 was checked on it before its release.

**Self-built desktop (Ryzen 5 5600X, RTX 3050):** installed next to Windows with 1.1.1 and tested by a friend of the
project – everything except games and heavy load works, including the **NVIDIA driver** from Control Center → System &
Updates → Hardware & Drivers (Secure Boot off) and Wi-Fi. The first report of the NVIDIA driver on real hardware.

**Samsung Galaxy Book 4:** installed to the whole disk (512 GB M.2 SSD, automatic partitioning) with 1.1.2, Secure Boot on, and used as a daily computer from now on. Installing, Wi-Fi, sound, graphics, brightness, suspend and waking up work. Chromium, LibreOffice and Steam installed from the Software Store without problems, and updates from Control Center ran cleanly. An external monitor on HDMI (1920×1080) works, and so do all ports: two USB-A, USB-C, HDMI, network cable, headphone jack and the microSD slot. A Bluetooth mouse, the number pad and the Fn keys for brightness, keyboard backlight and volume work. The Fn keys for CPU level, touchpad off and settings, and the Copilot key, do nothing; they often have no standard mapping on Linux ([#146](https://github.com/FreakySneaky787/Simple-OS/issues/146)).

**ASUS K42JA:** a laptop from 2010, reported by a user on YouTube. It runs well on the old hardware: low memory use, the
desktop looks good and browsers start faster than on other Linux systems they tried. No problems so far, and Simple OS
stays on the laptop. The single parts (Wi-Fi, sound, brightness, suspend) weren't reported one by one yet.

**Dell OptiPlex 9020:** with 1.0.3 the installer could leave the disk unable to start (issues
[#62](https://github.com/FreakySneaky787/Simple-OS/issues/62) and
[#64](https://github.com/FreakySneaky787/Simple-OS/issues/64)). Fixed in 1.0.4 and tested in a virtual machine set up
like this computer (legacy BIOS, MBR, "Install alongside" in an extended partition) – a test on the real computer is
still to come.

## Virtual machines

Releases are tested in QEMU/KVM before they are published: installing with legacy BIOS, with UEFI and with UEFI and
Secure Boot on (Microsoft keys), and updating from the previous version. In virt-manager (SPICE) the screen size
follows the window and copy & paste works between the virtual machine and your computer.

## Not tested yet – help wanted

- **Games** (Steam, Proton) and heavy load with the NVIDIA driver – the driver itself works (RTX 3050, see above)
- A newer laptop with **AMD** graphics (the 2010 ASUS K42JA with ATI Radeon works, see above)
- Older **Mac** laptops (Intel) – they usually need the Broadcom Wi-Fi driver

## Known limitations

- **64-bit PCs only** (x86-64). No ARM computers (Raspberry Pi, Apple Silicon Macs) and no 32-bit PCs.
- **NVIDIA driver only with Secure Boot off.** The driver is built on your computer and the firmware doesn't know its
  signature. Turn Secure Boot off in the firmware settings, then install the driver in Control Center → System &
  Updates → Hardware & Drivers.
- **GeForce RTX 50** cards: the NVIDIA driver in Debian 12 doesn't support them yet, so Hardware & Drivers doesn't
  offer it. The picture works with the free driver, without 3D acceleration.
- **Broadcom Wi-Fi** (many older laptops and Macs) needs an extra driver from Hardware & Drivers – that needs an
  internet connection by cable or through a phone (USB tethering) first.
- **Screens with very many pixels** (2.8K/4K laptops): Simple OS 1.1 brings a Scale setting (Control Center →
  Display); in 1.0.x text and menus stay small there. There is one scale for all screens (X11 has none per monitor):
  with a 4K laptop screen and a normal external monitor, the main screen decides.
- **Lenovo laptops** may show "Self-Healing BIOS ESP" once on the first start after installing. That's harmless and
  doesn't come back.

## Report your computer

Open a [hardware report](https://github.com/FreakySneaky787/Simple-OS/issues/new?template=hardware_report.yml) on
GitHub. It asks for the same columns as the table above. Menu → Help → Report a Problem creates a text file on your
desktop with the hardware details (model, graphics, Wi-Fi chip, sound) – please attach it. Your computer then gets a
row here, and anything that didn't work becomes an issue of its own.
