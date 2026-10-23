# Contributing to Simple OS

Thanks for wanting to help! Simple OS is a small project, so every test report, bug report and idea counts.

## 1. Test Simple OS – the most helpful thing you can do

Simple OS needs to work on many different computers, and that can only be checked on real hardware.
Especially useful:

- installing on **real hardware** (laptops, desktops, older PCs), in **UEFI** and **legacy BIOS/MBR** mode,
- **dual boot** next to Windows or another Linux,
- the setup wizard, updates, restore points, sleep, shutdown and restart.

See [Testing Simple OS](README.md#testing-simple-os) in the README and [TESTING.md](TESTING.md).
Always make a backup (e.g. a Rescuezilla image) before installing on a disk with data on it.

## 2. Report bugs

- On Simple OS: **Menu → Help → Report a Problem** collects the system info for you.
- Or use the [bug report form](https://github.com/FreakySneaky787/Simple-OS/issues/new/choose).
- Logs help a lot: `journalctl -b -p err` (this boot) or `journalctl -b -1 -p err` (the boot before).
- Check the [known issues](RELEASE_NOTES.md#known-issues) first.

## 3. Questions and ideas

- Questions, help and general talk: [Discussions](https://github.com/FreakySneaky787/Simple-OS/discussions).
- Ideas: the [feature request form](https://github.com/FreakySneaky787/Simple-OS/issues/new/choose).
  Have a look at the [roadmap](ROADMAP.md) first – it may already be planned.

## 4. Code and pull requests

- **Open an issue first** and describe what you want to change, so we can agree on it before you spend time on it.
  Small fixes (typos, docs) can go straight to a pull request.
- Keep pull requests **small** and about one thing.
- **Which branch:** fixes for the current release (1.x, Debian 12) go to `main`; work for 2.0 "Rigi" (Debian 13) goes
  to `trixie`. Not sure? Use `main` – fixes from there are merged into `trixie` regularly.
- Build and test as described in [For developers](README.md#for-developers): `./build_iso.sh`, then
  `./test_vm.sh` (BIOS) and `./test_vm.sh --uefi`.
- Simple OS is for normal users: keep things simple, with no terminal needed for everyday tasks.
- Code, comments, UI text and docs are in **English**.

## 5. Translations

Translations of Simple OS's own tools are planned for 1.1 (see the [roadmap](ROADMAP.md)).
If you would like to help with a language, say so in the [Discussions](https://github.com/FreakySneaky787/Simple-OS/discussions).

## Code of conduct

Please be kind and respectful – see the [Code of Conduct](CODE_OF_CONDUCT.md).

## License of contributions

Simple OS's own code is licensed under the [GPL-3.0-or-later](LICENSE). The maintainer may change the license of
Simple OS in the future, for example to a different version of the GPL or to another license.

So that this stays possible, by contributing (code, scripts, text, artwork or translations) you agree that:

- your contribution is licensed under the project's current license, **and**
- the maintainer may also publish your contribution under any other license in the future.

You keep the copyright of your contribution. Releases that were already published stay available under the license
they were published with. Packages that Simple OS takes from Debian and other projects keep their own licenses.

If you don't agree with this, please say so in your pull request before it is merged.
