# Hardware compatibility

Simple OS doesn't promise to run on every computer. This page lists the computers it is **known** to work on –
tested by us or reported by people who use it – and what didn't work. Your computer isn't listed? It may still work.
Try the live session from the USB stick first, it changes nothing on the computer. Then
[tell us how it went](#report-your-computer), so the next person knows.

Last updated: 29 October 2026 (Simple OS 1.0.7).

## Tested computers

✅ works · ⚠️ works, with a limitation in the notes · ❌ doesn't work · – not tested yet

| Computer | Firmware | Version | Install | Wi-Fi | Sound | Graphics | Brightness | Suspend | External monitor |
|---|---|---|---|---|---|---|---|---|---|
| Lenovo ThinkPad E16 Gen 3 (21TF) – Intel Core 5 210H, Intel graphics, Intel Wi-Fi | UEFI, Secure Boot off | 1.0.7 | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dell OptiPlex 9020 – desktop | legacy BIOS, MBR, next to another system | 1.0.3 | ❌ | – | – | – | – | – | – |

**ThinkPad E16 Gen 3:** in daily use since Simple OS 1.0. Wi-Fi: with one router the 5 GHz connection (a wide 160 MHz
channel) was slow; setting the network to 2.4 GHz in Control Center → Wi-Fi fixed it. Bluetooth headphones, keyboards
and phones pair. A monitor plugged in later turns on by itself. Suspend and waking up were checked with 1.0.7. The power
button has to be held for about a second – the firmware ignores a quick tap.

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

- A desktop with an **NVIDIA** graphics card and the NVIDIA driver
- A laptop with **AMD** graphics
- **Dual boot with Windows** on a real computer
- **Secure Boot on** with an installed system on a real computer
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
- **One display scale for all screens.** Simple OS uses X11, which has no separate scale per monitor: with a 4K
  laptop screen and a normal external monitor, the main screen decides.
- **Lenovo laptops** may show "Self-Healing BIOS ESP" once on the first start after installing. That's harmless and
  doesn't come back.

## Report your computer

Open a [hardware report](https://github.com/FreakySneaky787/Simple-OS/issues/new?template=hardware_report.yml) on
GitHub. It asks for the same columns as the table above. Menu → Help → Report a Problem creates a text file on your
desktop with the hardware details (model, graphics, Wi-Fi chip, sound) – please attach it. Your computer then gets a
row here, and anything that didn't work becomes an issue of its own.
